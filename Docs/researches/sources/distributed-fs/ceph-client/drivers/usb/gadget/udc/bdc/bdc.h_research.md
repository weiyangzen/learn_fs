<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc.h

## Purpose
This is the central private header for the Broadcom BDC USB3 device controller driver. It defines register offsets, bit fields, descriptor formats, endpoint/request/controller state structures, inline MMIO helpers, and cross-file prototypes.

## Important APIs, Types, And Functions
Important data types are `struct bdc_bd` for buffer descriptors, `struct bdc_sr` for status reports, `struct bd_table` and `struct bd_list` for chained descriptor tables, `struct bd_transfer`, `struct bdc_req`, `struct bdc_ep`, `struct srr`, and `struct bdc`. EP0 state is encoded by `enum bdc_ep0_state`, and USB link states by `enum bdc_link_state`. Constants describe command opcodes/status values, USPC/USPPMS/BDCSC fields, BD flags, status report types, transfer statuses, maximum transfer sizes, U1 timing, interrupt coalescing, and remote wake bookkeeping. Cross-file APIs include controller lifecycle (`bdc_run()`, `bdc_stop()`, `bdc_reset()`, `bdc_reinit()`), gadget lifecycle (`bdc_udc_init()`, `bdc_udc_exit()`), connection control, transfer notification, status report handlers, and EP0 report handlers.

## Control Flow
The header encodes hardware conventions used by all BDC source files: endpoint array index 1 is EP0, endpoint indexes map as OUT even and IN odd for nonzero endpoints, status reports dispatch by `sr_handler[]`, and EP0 transfer status reports dispatch through `sr_xsf_ep0[]`. `bdc_readl()` and `bdc_writel()` are the shared MMIO accessors.

## State And Persistence
`struct bdc` owns all persistent in-memory driver state: gadget object, gadget driver pointer, spinlock, PHYs, endpoint array, registers, scratchpad DMA buffer, status report ring, setup packet, EP0 requests and state, delayed status/ZLP flags, pullup state, device status bits, DMA pool, remote wake delayed work, and optional clock. Endpoint and request state persists until disabled, completed, or freed.

## Dependencies And Integration Points
The header depends on Linux USB gadget/ch9 types, DMA mapping, lists, spinlocks, debugfs, unaligned access helpers, and BDC hardware definitions local to the file. It is included by core, command, endpoint, gadget, and debug implementation files.

## Risks
Most hardware programming constants are open-coded here; mistakes in bit shifts or endpoint index conventions affect every implementation file. `BDC_PSP` is defined twice with the same expression, which is harmless but easy to notice during maintenance. Maximum transfer and descriptor ring sizing are fixed by macros and can reject large gadget requests or stress isochronous buffering.

## Test Signals
Compile coverage is the main header test. Runtime signals include correct endpoint naming/indexing, successful EP0 configuration after connect, status report dispatch to the expected handler, correct DMA address programming on 32-bit and 64-bit capable devices, and remote wake status bit transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc.h -->
