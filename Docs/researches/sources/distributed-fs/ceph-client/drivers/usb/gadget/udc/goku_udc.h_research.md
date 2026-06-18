# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/goku_udc.h

## Purpose

`goku_udc.h` defines the Toshiba TC86C001 "Goku-S" PCI BAR0 register layout, interrupt and command bits, DMA master controls, endpoint status/mode fields, standard-request helper bits, fixed FIFO limits, and private software data structures used by `goku_udc.c`.

## Important APIs, Types, and Functions

The central hardware type is packed `struct goku_udc_regs`, covering interrupt registers, DMA registers, power detect, endpoint FIFOs, endpoint mode/status/size registers, setup-packet byte registers, command/status registers, request-mode registers, address/ready fields, and an optional descriptor RAM area. Software types are `struct goku_ep`, `struct goku_request`, `enum ep0state`, and `struct goku_udc`. Utility macros include interrupt groups `INT_DEVWIDE` and `INT_EP0`, dataset masks `DATASET_A/B/AB()`, endpoint status encodings, command encodings, DMA endpoint constants `UDC_MSTWR_ENDPOINT` and `UDC_MSTRD_ENDPOINT`, and logging helpers.

## Control Flow

The header itself has no runtime flow, but it defines how the C file drives the device. Interrupt bits in `int_status` are masked by the software `int_enable` shadow and routed to device-wide, ep0, PIO endpoint, or DMA-completion handling. Endpoint commands are issued by writing `COMMAND_EP(n) | command` to `Command`. PIO paths inspect `DataSet`, `EPxSizeLA/LB`, and FIFO registers. DMA paths program `out_dma_*`, `in_dma_*`, and `dma_master` with the MST read/write enable, reset, timeout, and EOP policies. Ep0 state values constrain when setup, data, status, stall, suspend, and disconnect processing can touch registers.

## State and Persistence Behavior

All state represented here is runtime-only. `struct goku_udc` persists for the lifetime of the PCI device and owns the gadget, endpoint array, driver pointer, ep0 state, resource flags, register mapping, interrupt mask shadow, configuration flags, and statistics. `struct goku_ep` persists for each fixed endpoint and tracks DMA/PIO mode, direction, stopped state, request queue, and register pointers. `struct goku_request` is per-transfer. Hardware state is the MMIO BAR contents and is reset during probe, disconnect, and stop paths.

## Dependencies and Integration Points

This header is private to the Goku UDC driver but assumes Linux USB gadget types and PCI/MMIO usage from the C file. It encodes the controller's fixed four-endpoint model, hardware-assisted subset of standard requests, full-speed FIFO limits, and DMA wiring where master-write maps to ep1 OUT and master-read maps to ep2 IN when `MST_CONNECTION` is clear.

## Risks and Test Signals

Risks include packed register-layout correctness, bit-mask mistakes in interrupt acknowledgement and endpoint commands, mismatch between fixed endpoint numbers and descriptors, DMA direction assumptions tied to `MST_CONNECTION`, and state-machine transitions that allow register access during suspend. Test signals are compile coverage, BAR register dump sanity through proc debug, endpoint enable for 8/16/32/64 maxpacket values, PIO dataset handling with single and double buffering, DMA IN on ep2, power-detect connect/disconnect, command delay adequacy, and ep0 state transitions through setup/data/status/stall/suspend.
