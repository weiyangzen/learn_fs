<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mousedev.c -->
# sources/distributed-fs/ceph-client/drivers/input/mousedev.c

## Purpose
`mousedev.c` implements the legacy `/dev/input/mouseX`, `/dev/input/mice`, and optional `/dev/psaux` compatibility interface. It consumes generic input events from mouse-like, tablet-like, touchpad, and wheel devices and emits PS/2, IntelliMouse, or ExplorerPS/2 byte streams to character-device clients.

## Important APIs, Types, and Functions
`struct mousedev` represents a per-input-device node or the global mixer, including input handle, client list, locks, cdev/device, packet accumulator, touchpad conversion history, and open/close hooks. `struct mousedev_client` is per open file and stores queued motion packets, PS/2 response buffer, emulation mode, and async state. Event handling uses `mousedev_event()`, `mousedev_abs_event()`, `mousedev_touchpad_event()`, `mousedev_rel_event()`, `mousedev_key_event()`, and `mousedev_notify_readers()`. File operations are `mousedev_open()`, `mousedev_release()`, `mousedev_read()`, `mousedev_write()`, `mousedev_poll()`, and `mousedev_fasync()`.

## Control Flow
Module init creates the global `mice` mix device, registers an input handler, and optionally registers `/dev/psaux`. When a matching input device appears, `mousedev_connect()` creates a cdev-backed device and adds it to the mixer. Incoming input events accumulate into `mousedev->packet` until `SYN_REPORT`, then notify per-device clients and mixer clients. Each client has a 16-entry circular queue; reads convert queued motion into PS/2-compatible packets, clamping large deltas and leaving residue for subsequent reads. Writes emulate mouse commands, including sample-rate sequences that switch the client into IMPS or ExplorerPS/2 mode.

## State and Persistence
State is in kernel memory only. Per-device open counts drive `input_open_device()`/`input_close_device()`. Mixer open state can open all currently known devices and later opens new devices added to the mix. Per-client position starts at screen center and persists for the life of the file descriptor. Module parameters `xres`, `yres`, and `tap_time` globally control absolute scaling and touchpad tap emulation.

## Dependencies and Integration Points
The file integrates with the input handler API, input minor allocator, cdev/device model, wait queues, fasync, poll, optional misc `/dev/psaux`, RCU list traversal for clients, and input device ID matching. It is the compatibility consumer for many drivers in this subset, including Synaptics and VSXXX absolute reports.

## Risks and Edge Cases
Legacy emulation requires careful state sequencing: button changes can force a new queue entry, large deltas are split across reads, and writes can interleave PS/2 responses with motion data. Touchpad absolute-to-relative conversion relies on duplicate event handling and four-sample history. The global `mousedev_mix->packet.buttons` is updated from all devices, so button state races across devices must be considered. Disconnect marks devices dead and wakes clients, but already queued clients must handle `-ENODEV`.

## Test Signals
Validate per-device and `/dev/input/mice` reads, blocking and nonblocking reads, poll/fasync wakeups, IMPS/Explorer command negotiation, absolute tablet scaling, touchpad tap-to-click timing, disconnect wakeups, and module parameter effects. Regression tests should include multiple clients and multiple devices opened through the mixer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mousedev.c -->
