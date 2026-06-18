<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/pipe.h -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/pipe.h

## Purpose
Declares Renesas USBHS pipe state and pipe-management APIs.

## Important APIs, Types, And Functions
`struct usbhs_pipe` stores transfer type, `usbhs_priv`, selected FIFO, packet list, maxpacket, flags, current handler, and mode-private pointer. `struct usbhs_pipe_info` owns the pipe array and DMA map/unmap callback. Iteration macros cover pipes with or without DCP. Declarations cover allocation/free, lifecycle, direction/running predicates, clear/enable/disable/stall, counters, FIFO selection, config update, sequence, and DCP helpers.

## Control Flow
Mode modules allocate/configure pipes and assign handlers; FIFO code uses pipe fields during transfer; teardown frees or clears pipes.

## State And Persistence
Pipe software state mirrors hardware pipe/FIFO state. Packet lists persist until completion/cancel.

## Dependencies And Integration Points
Includes `common.h` and `fifo.h`; internal only, with external parameters from `linux/usb/renesas_usbhs.h`.

## Risks
`usbhs_pipe_type(p)` is an lvalue macro. `usbhs_pipe_is_busy()` means a FIFO is selected, not necessarily hardware electrical busy. Direction helpers require mode context.

## Test Signals
Compile coverage, pipe list lifetime, FIFO selection, DCP identification, and direction behavior in host and gadget mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/pipe.h -->
