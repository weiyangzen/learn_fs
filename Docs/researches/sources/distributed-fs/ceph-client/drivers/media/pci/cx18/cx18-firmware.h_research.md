# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-firmware.h

## Purpose
This header declares firmware, power, and memory initialization functions for the cx18 main driver.

## Important APIs, Types, and Functions
It declares `cx18_firmware_init()`, `cx18_halt_firmware()`, `cx18_init_memory()`, and `cx18_init_power()`.

## Control Flow
The header has no executable control flow. Probe calls power and memory initialization; first open calls firmware initialization; remove calls halt.

## State and Persistence
The functions operate on `struct cx18` and program hardware state, but the header itself holds no state.

## Dependencies and Integration Points
It is included by `cx18-driver.c` and implemented by `cx18-firmware.c`. It assumes a visible declaration of `struct cx18` from the main driver header.

## Risks and Edge Cases
Prototype drift would break the probe and first-open paths. Because firmware loading is delayed until first open, callers must continue to handle runtime errors from `cx18_firmware_init()`.

## Test Signals
Compile/link success and runtime first-open firmware loading are the meaningful signals.
