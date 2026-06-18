# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/gr_udc.h

## Purpose

`gr_udc.h` is the private hardware and state header for the Aeroflex Gaisler GRUSBDC gadget driver. It defines the big-endian AMBA register layout, endpoint/control/status bit fields, DMA descriptor format, endpoint/request/controller private structures, and ep0 state enum used by `gr_udc.c`.

## Important APIs, Types, and Functions

Hardware layout types are `struct gr_epregs` for per-endpoint registers and `struct gr_regs` for OUT endpoint blocks, IN endpoint blocks, global control, and global status. DMA is described by `struct gr_dma_desc`, with hardware-used `ctrl`, `data`, and `next` fields followed by software-only physical and virtual chain pointers. Driver-private types are `struct gr_ep`, `struct gr_request`, `enum gr_ep0state`, and `struct gr_udc`. The helper macro `to_gr_udc()` maps a gadget pointer back to controller state.

Constants describe endpoint control fields for buffer size, packet interrupt, clear buffer/status, max payload, additional transactions, transfer type, halt/disable/valid; DMA control bits for AMBA error, abort, interrupt, interrupt enable, and descriptor availability; endpoint status buffer bits and byte counts; global control bits for interrupts, pullup, remote wakeup, test mode, address, and speed update; and status fields for endpoint counts, DMA mode, USB reset, VBUS, speed, address function, and frame number.

## Control Flow

The header has no independent execution, but it defines the hardware contract for the driver. Probe reads `GR_STATUS_NEPI`, `GR_STATUS_NEPO`, and `GR_STATUS_DM` to discover capabilities. Endpoint init and enable program `epctrl` and `dmactrl` using the bit definitions. Queueing creates `gr_dma_desc` chains and writes descriptor physical addresses to `dmaaddr`; interrupt handling checks descriptor enable bits, endpoint status buffers, DMA error bits, and global status changes. Ep0 control flow is represented by `enum gr_ep0state`, which distinguishes disconnect, setup, IN/OUT data, IN/OUT status, stall, and suspend states.

## State and Persistence Behavior

All structures are runtime-only. `struct gr_udc` persists for the platform device lifetime and owns the gadget, endpoint arrays, descriptor DMA pool, ep0 request objects, register mapping, IRQ numbers, remote-wakeup/test-mode state, endpoint counts, and lock. `struct gr_ep` persists per direction and endpoint number, including queue state and coherent `tailbuf` for OUT odd-tail reception. `struct gr_request` persists per transfer and owns a DMA descriptor chain until completion. The only external projection is hardware MMIO state, gadget state, and optional debugfs output.

## Dependencies and Integration Points

The header is private to GRUSBDC and assumes Linux USB gadget types, DMA APIs, list handling, spinlocks, and platform/of integration supplied by the C file. It encodes the core's DMA-only driver support; the C file rejects slave-mode hardware despite the register union documenting slave-mode fields. It also embeds the maximum 16-IN/16-OUT endpoint topology used for endpoint arrays and name tables.

## Risks and Test Signals

Risks include big-endian register access assumptions, descriptor layout mismatch where hardware only consumes the first three words, bit-field mistakes in max payload and buffer-size calculations, endpoint count bounds, and the use of one `GR_EPSTAT_PT/PR` bit position for direction-specific meanings. Test signals include compile coverage, register dump sanity from debugfs, probe on cores with different endpoint counts and buffer sizes, DMA descriptor pool alignment, ep0 setup and status transitions, OUT odd-tail bounce behavior, and hardware interrupt/error handling for all endpoint directions.
