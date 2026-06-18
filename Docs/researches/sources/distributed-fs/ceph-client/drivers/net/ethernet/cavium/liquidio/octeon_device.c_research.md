# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_device.c

## Purpose
Provides core Octeon device allocation, default configuration selection, global device registry, queue setup wrappers, dispatch table management, firmware core-ready handling, indirect PCI register access, memory readiness checks, and interrupt re-enable accounting for the LiquidIO driver family.

## Important APIs, Types, and Functions
Public entry points include `octeon_init_device_list`, `octeon_allocate_device`, `octeon_free_device_mem`, `octeon_register_device`, `octeon_deregister_device`, `octeon_allocate_ioq_vector`, `octeon_free_ioq_vector`, `octeon_setup_instr_queues`, `octeon_setup_output_queues`, `octeon_set_io_queues_off`, `octeon_set_droq_pkt_op`, `octeon_init_dispatch_list`, `octeon_delete_dispatch_list`, `octeon_get_dispatch`, `octeon_register_dispatch_fn`, `octeon_core_drv_init`, `octeon_get_tx_qsize`, `octeon_get_rx_qsize`, `octeon_get_conf`, `lio_get_device`, `lio_pci_readq`, `lio_pci_writeq`, `octeon_mem_access_ok`, `octeon_wait_for_ddr_init`, and `lio_enable_irq`.

## Control Flow
Device allocation reserves one contiguous block for `octeon_device`, private driver storage, chip-specific storage, and dispatch table entries, then inserts it into the global device array under lock. Registration shares adapter refcount and firmware state between functions on the same bus/device. Queue setup creates the initial IQ and OQ using chip-specific default descriptor counts and sizes. Dispatch initialization clears the hash table and request free-function table; registration installs the first opcode in-place and hash collisions on a linked list. Core-ready handling parses firmware app mode, capabilities, max ports, PKIND, board info, and moves the device to `OCT_DEV_CORE_OK`.

## State and Persistence Behavior
Static state includes default CN66xx, CN68xx, CN23xx configs, the global `octeon_device[]` table, adapter refcounts, adapter firmware states, and cached core setup. Per-device state includes PCI location, status, chip/config pointer, queue arrays, dispatch table, firmware info, board info, PF/VF handshake fields, and interrupt vectors. Register access functions serialize windowed BAR operations with `pci_win_lock`.

## Dependencies and Integration Points
Depends on Linux PCI/netdevice/vmalloc APIs and LiquidIO headers for IQ, DROQ, response management, network helpers, and chip-specific CN66xx/CN23xx definitions. It is called by PF and VF main drivers, DROQ processing, console memory checks, interrupt handlers, and netdev setup.

## Risks
Global device registry lifetime is delicate because lookup is lockless in `lio_get_device` while allocation/free update the array. Dispatch registration checks for duplicates outside the lock after releasing the first-level lock, so duplicate races would need external serialization. Queue setup initially creates only queue zero, with later NIC setup creating additional firmware-assigned queues. `octeon_set_io_queues_off` has chip-specific register paths and a shared loop counter for VF reset waits. Indirect PCI window reads/writes require strict ordering and locking.

## Test Signals
Multiple adapters and PF/VF functions, shared adapter refcounts, allocation failure paths, dispatch hash collisions and duplicate registration, firmware core-ready packet parsing, queue size queries, CN23xx VF IO queue reset clearing, DDR-ready timeout, indirect CSR reads/writes, IRQ resend behavior for IQ and DROQ, and teardown after partial initialization are useful signals.
