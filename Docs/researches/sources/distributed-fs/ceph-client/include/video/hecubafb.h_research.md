# sources/distributed-fs/ceph-client/include/video/hecubafb.h

## Purpose
`hecubafb.h` defines the platform contract for the Hecuba e-paper framebuffer driver and Apollo controller command set. It separates framebuffer logic from board-specific GPIO/data/acknowledge handling.

## Important APIs, Types, and Functions
Apollo commands include `APOLLO_START_NEW_IMG`, `APOLLO_STOP_IMG_DATA`, `APOLLO_DISPLAY_IMG`, `APOLLO_ERASE_DISPLAY`, and `APOLLO_INIT_DISPLAY`. Hecuba interface bits include wakeup, data strobe, read/write, command/data, and acknowledge bits. `struct hecubafb_par` stores the `fb_info`, board pointer, and send-command/send-data callbacks. `struct hecuba_board` supplies module ownership plus `remove`, `set_ctl`, `set_data`, `wait_for_ack`, and `init` callbacks.

## Control Flow
The framebuffer driver calls board initialization, emits Apollo commands/data through `send_command` and `send_data`, toggles board control/data lines via board callbacks, waits for acknowledge transitions, and displays or erases images with the controller command bytes.

## State and Persistence Behavior
Runtime state is limited to the framebuffer private data and board callbacks. Image persistence is primarily an e-paper hardware property after `APOLLO_DISPLAY_IMG`; the header has no persistent software store.

## Dependencies and Integration Points
The header integrates framebuffer core state (`struct fb_info`), loadable board modules, and board-level GPIO or bus code. Board drivers can implement polling or interrupt-backed acknowledge waits.

## Risks and Test Signals
Risks include inverted control bits, missing acknowledge waits, callback lifetime issues with the owner module, and image transfer framing errors. Test signals include init/display/erase command traces, ack timeout testing, board remove cleanup, and framebuffer updates on real Hecuba/Apollo hardware.
