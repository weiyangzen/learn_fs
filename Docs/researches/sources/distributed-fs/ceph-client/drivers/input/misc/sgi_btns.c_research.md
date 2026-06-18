# sources/distributed-fs/ceph-client/drivers/input/misc/sgi_btns.c

## Purpose
`sgi_btns.c` polls SGI Indy/O2 volume buttons and reports debounced `KEY_VOLUMEDOWN` and `KEY_VOLUMEUP` events with scan codes.

## Important APIs, Types, and Functions
Architecture-specific `button_status()` implementations read SGI IP22 IOC panel bits or IP32 MACE audio-control bits. `struct buttons_dev` stores keymap and per-button debounce counters. `handle_buttons()` implements threshold-based press/release reporting. `sgi_buttons_probe()` registers a polled input device.

## Control Flow
Probe allocates state/input, copies the two-key map, configures `EV_MSC/MSC_SCAN` and `EV_KEY`, sets polling every 30 ms, and registers. Each poll reads the two-bit hardware status, increments counters until a press threshold of three polls, reports press once, reports release when a previously pressed counter clears, and resets counters.

## State and Persistence Behavior
Persistent state consists of the copied keymap and debounce counters. Hardware state is read-only except IP32 clears the button status bits by writing back masked audio-control state. Input core stores current key state.

## Dependencies and Integration Points
The driver depends on SGI IP22 or IP32 architecture headers/MMIO globals, input polling, platform device enumeration, and input sparse key capabilities. Userspace sees volume keys plus scan codes.

## Risks and Edge Cases
The file relies on exactly one architecture-specific `button_status()` being compiled. Poll debounce assumes 30 ms cadence, producing about 90 ms press threshold. IP32 status read clears bits, so missed polls or concurrent consumers could lose events. There is no explicit remove logic beyond devm/input cleanup.

## Test Signals
Test IP22 and IP32 builds, button press/release debounce, scan-code emission, volume key mapping, polling interval, and behavior with short pulses shorter than the threshold.
