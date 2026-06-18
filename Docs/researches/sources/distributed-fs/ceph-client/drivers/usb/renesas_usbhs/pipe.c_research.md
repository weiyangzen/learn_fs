<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/pipe.c -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/pipe.c

## Purpose
Hardware pipe manager for Renesas USBHS. It allocates pipes by transfer type/direction, programs PIPECFG/PIPEBUF/PIPEMAXP/DCP registers, controls PID/STALL/DATA sequence, clears buffers, sets bulk counters, and connects pipes to FIFOs and mode-private endpoint state.

## Important APIs, Types, And Functions
Public APIs include `usbhs_pipe_probe/remove()`, `usbhs_pipe_init()`, `usbhs_pipe_malloc/free()`, `usbhs_dcp_malloc()`, `usbhs_pipe_config_update()`, `usbhs_pipe_enable/disable/stall/is_stall()`, `usbhs_pipe_clear()`, `usbhs_pipe_clear_without_sequence()`, `usbhs_pipe_config_change_bfre()`, `usbhs_pipe_set_trans_count_if_bulk()`, and `usbhs_pipe_select_fifo()`. Internal helpers handle DCP versus PIPE registers, safe barriers, PIPECFG creation, and PIPEBUF encoding.

## Control Flow
Probe allocates the pipe array from platform configs. Mode start resets flags/lists/FIFO links and hardware buffers. Endpoint enable or host start allocates compatible unused pipes, waits for safe barrier, writes config/buffer registers, clears buffers, and sets DATA0. Transfers update PID, running flags, DATA sequence, and counters.

## State And Persistence
Each pipe stores type, owner, FIFO pointer, packet list, maxpacket, flags, handler, and mode-private pointer. Hardware state includes PIPESEL, PIPECFG, PIPEBUF, PIPEMAXP, PIPEnCTR/DCPCTR, transaction counters, and DATA toggle bits.

## Dependencies And Integration Points
Consumes platform pipe configs, common register definitions, FIFO DCP clearing, and host/gadget allocation patterns.

## Risks
Reconfiguration requires NAK, no busy, and no selected FIFO. Direction flags combine host/gadget semantics. Bulk transfer counters only apply to bulk IN. `usbhs_pipe_clear_without_sequence()` must preserve DATA toggle while changing BFRE/clearing buffers.

## Test Signals
Pipe allocation exhaustion, DCP/non-DCP config, host/gadget direction combinations, stall/unstall, DATA0/1 preservation, bulk counters, FIFO cleanup, and busy barriers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/pipe.c -->
