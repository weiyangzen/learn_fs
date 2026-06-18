# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/remote.h

## Purpose
`remote.h` defines IBM ASM remote-console MMIO offsets, remote input wire structures, queue helpers, display-setting address macros, and keysym constants.

## Important APIs, Types, and Functions
It defines offsets under `CONDOR_MOUSE_DATA`, display registers, ISR control/status, queue reader/writer/begin, input types, mouse button masks, `struct mouse_input`, `struct keyboard_input`, `struct remote_input`, address macros such as `mouse_addr()`, `display_width()`, and queue helpers like `get_queue_reader()`, `get_queue_writer()`, `get_queue_entry()`, and `advance_queue_reader()`. It also enumerates many X-style keysyms consumed by `remote.c`.

## Control Flow
Inline/macros directly read and write MMIO for interrupts and queue state. `advance_queue_reader()` wraps at `REMOTE_QUEUE_SIZE` and stores the new reader index in hardware.

## State and Persistence
No software state is stored. The macros operate on service-processor MMIO queue and display registers.

## Dependencies and Integration Points
It includes `asm/io.h` and is used by remote input, low-level interrupt handling, and ibmasmfs remote-video settings.

## Risks and Edge Cases
Macros evaluate `sp` and address expressions directly, so callers must pass valid live service-processor state. The many keysym constants are not self-validating; translation coverage must be maintained in `remote.c`.

## Test Signals
Validate queue address calculations, wrap behavior, display register read/write through ibmasmfs, ISR control/status operations, and translation table coverage for declared keysyms.
