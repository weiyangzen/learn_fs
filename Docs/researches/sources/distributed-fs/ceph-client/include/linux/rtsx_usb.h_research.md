# sources/distributed-fs/ceph-client/include/linux/rtsx_usb.h

## Purpose
`rtsx_usb.h` is the register map and exported core interface for Realtek RTS5139/RTS5179 USB card readers.

## Important APIs, types, and functions
Key constants cover USB endpoint numbers, vendor requests, card IDs/status bits, command packet offsets, stage flags, register maps for SD/MS/card/clock/OCP/USB/FIFO/DMA blocks, and internal bit values. The core type is `struct rtsx_ucr`, storing IDs, package/version, clock, command/response buffers, USB device/interface, current SG request, SG timer, and device mutex. APIs include register read/write via bulk or EP0, command batching/sending, response retrieval, data transfer, ping-pong buffer read/write, clock switching, card-exclusive checks, and inline LED/FSM/DMA error helpers.

## Control flow, state, and persistence
USB child drivers build commands in `cmd_buf` with `rtsx_usb_init_cmd()`, send them via vendor protocol, optionally read responses, and move payloads over bulk endpoints or USB SG. `cmd_idx`, current clock, SG request, and timer track in-flight operations. Inline error helpers flush FIFO and reset DMA on hardware faults. Persistent state is the USB interface/device registration and `rtsx_ucr` contents while the reader is present.

## Dependencies and integration points
It depends on the USB core, timer/mutex support via implementation users, and Realtek SD/MMC/MS child drivers. It integrates with USB control endpoint register access, bulk transfers, card detect/status, clock and voltage programming, OCP handling, and LED control.

## Risks and test signals
Risks include command buffer overflow, endpoint/protocol mismatches, SG timeout races, duplicate register definitions, insufficient locking around `cmd_buf`/`current_sg`, and failing to clear DMA/FSM errors after stalls. Test signals include USB probe/disconnect, EP0 and bulk register access, command batching, bulk read/write with and without SG, timeout/cancel paths, SD/MS card status, LED toggles, OCP status, and suspend/resume.
