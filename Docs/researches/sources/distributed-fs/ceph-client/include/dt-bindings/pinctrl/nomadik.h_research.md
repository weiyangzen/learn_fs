<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/nomadik.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/nomadik.h

## Purpose

`nomadik.h` provides small numeric constants for ST-Ericsson Nomadik pinctrl device-tree properties. It names pull, direction, sleep-mode, GPIO-mode, wakeup, and power-disconnect selections used by Nomadik pin configuration bindings.

## Important APIs, Types, and Functions

The header exports 21 numeric constants. Active-state input constants are `INPUT_NOPULL`, `INPUT_PULLUP`, and `INPUT_PULLDOWN`. Output constants are `OUTPUT_LOW`, `OUTPUT_HIGH`, and `DIR_OUTPUT`. Sleep-mode constants include `SLPM_DISABLED`, `SLPM_ENABLED`, `SLPM_INPUT_*`, `SLPM_DIR_INPUT`, `SLPM_OUTPUT_*`, `SLPM_DIR_OUTPUT`, `SLPM_WAKEUP_*`, and `SLPM_PDIS_*`. `GPIOMODE_DISABLED` and `GPIOMODE_ENABLED` select whether a pin is exposed as GPIO.

## Control Flow

There is no executable flow. DTS source includes the header, the preprocessor substitutes small integers, and the Nomadik pinctrl driver interprets those integers when parsing pin configuration properties.

## State and Persistence Behavior

The header has no mutable state or persistence. Values are persisted only indirectly in compiled device trees. Runtime pin state belongs to the pinctrl driver and hardware registers after the kernel applies active or sleep states.

## Dependencies and Integration Points

There are no C includes or helper macros. Integration is with Nomadik DTS files and the corresponding pinctrl binding parser. Because the values are intentionally small and reused across independent property domains, the meaning depends on the property in which a constant appears.

## Risks and Edge Cases

Several domains reuse the same numeric values with different meanings, for example `0` can mean no pull, output low, sleep disabled, wakeup disabled, GPIO mode disabled, or sleep power-disconnect disabled. This is safe in the correct property but dangerous if constants are moved between properties during DTS edits. The file lacks include guards, so duplicate inclusion is harmless for identical macros but leaves less protection against accidental redefinition by other headers.

## Test Signals

Test signals include DTS compilation for boards that include Nomadik pin states, binding validation for accepted property values, runtime pinctrl debugfs inspection of active and sleep states, suspend/resume tests for `SLPM_*` settings, and wakeup tests for pins using `SLPM_WAKEUP_ENABLE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/nomadik.h -->
