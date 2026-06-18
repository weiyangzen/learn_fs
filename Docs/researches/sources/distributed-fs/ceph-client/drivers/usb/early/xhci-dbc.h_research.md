# sources/distributed-fs/ceph-client/drivers/usb/early/xhci-dbc.h

Purpose: defines the register layout, hardware data structures, constants, and software state used by the xHCI Debug Capability early console driver.

Important APIs/types/functions: key types are `struct xdbc_regs`, `xdbc_trb`, `xdbc_erst_entry`, `xdbc_info_context`, `xdbc_ep_context`, `xdbc_context`, `xdbc_strings`, `xdbc_segment`, `xdbc_ring`, and `xdbc_state`. It defines DbC control/status/port bits, descriptor identity values, string constants, ring sizes, endpoint ID variants, PCI scan limits, table layout constants, state flags, max packet size, doorbell target encoding, and `xdbc_read64`/`xdbc_write64` wrappers.

Control flow: the C file uses these layouts to map MMIO registers, allocate rings and descriptor tables, program ERST/DCCP/devinfo registers, queue TRBs, interpret event TRBs, track cycle state, and decide whether endpoint events refer to IN or OUT rings.

State and persistence: `struct xdbc_state` is the persistent early-console state container. It holds PCI coordinates, mapped xHCI base, DbC register pointer, DMA addresses, backing pages, rings, buffers, flags, port number, and a raw spinlock.

Dependencies and integration: includes Linux types and USB chapter 9 constants, and expects xHCI 64-bit accessor helpers to be available where included. It is private to early xDBC support.

Risks: structures mirror hardware ABI and require correct endianness and alignment. Endpoint ID differences across vendors are captured by duplicate constants; missing another variant would break event handling. Table size constants must remain consistent with allocations in `xhci-dbc.c`. The max packet and ring sizes drive transfer chunking and memory layout.

Test signals: compile-time layout use, successful DbC context programming, correct descriptor strings on the debug host, transfer events mapping to expected endpoints, and stable output across ring wrap.
