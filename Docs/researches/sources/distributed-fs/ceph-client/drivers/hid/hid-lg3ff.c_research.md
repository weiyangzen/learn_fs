# sources/distributed-fs/ceph-client/drivers/hid/hid-lg3ff.c

## Purpose

`hid-lg3ff.c` implements force feedback for the Logitech Flight System G940, selected by `LG_FF3` in the main Logitech driver. It supports constant force and autocenter commands for the stick's X and Y axes.

## Important APIs, Types, And Functions

`lg3ff_init()` validates that an input device exists and output report 0 field 0 has at least 35 values, sets `FF_CONSTANT` and `FF_AUTOCENTER`, creates a memless FF device, and attaches `hid_lg3ff_set_autocenter()` if autocenter is available. `hid_lg3ff_play()` writes constant-force command bytes. `hid_lg3ff_set_autocenter()` writes the discovered autocenter pattern into both X and Y axis command regions.

## Control Flow

The main driver disables generic FF and calls `lg3ff_init()`. Runtime FF playback clears the entire output report value array, handles `FF_CONSTANT`, reads X/Y levels from the ramp fields used by memless force feedback, writes command `0x51`, stores negated two's-complement X at index 1 and Y at index 31, then sends the report. Autocenter writes command `0x51` plus fixed values at indices 1..4 and 31..34 and sends the report. The comments note a hardware deadman's switch must be covered for effects to work.

## State And Persistence Behavior

There is no additional heap state. The driver mutates the HID output report value buffer and relies on HID/input core for FF object lifetime. Hardware force state persists until overwritten by later commands.

## Dependencies And Integration Points

It depends on the first HID input device, Linux input memless FF, and `hid_validate_values()` against the G940 output report shape. It is built only when `CONFIG_LOGIG940_FF` provides the real initializer declared in `hid-lg.h`.

## Risks And Test Signals

Risks include using ramp fields for constant-force X/Y levels, assuming exactly one fixed report layout, sign conventions that differ from other Logitech sticks, and clearing all output fields before each effect. Test by confirming `FF_CONSTANT`/`FF_AUTOCENTER` exposure, positive and negative X/Y force direction, autocenter strength, deadman's switch behavior, and clean failure when reports or inputs are absent.
