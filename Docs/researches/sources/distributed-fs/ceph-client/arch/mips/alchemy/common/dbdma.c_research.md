# sources/distributed-fs/ceph-client/arch/mips/alchemy/common/dbdma.c

## Purpose
`dbdma.c` implements the Descriptor Based DMA manager used by Au1550, Au1200, and Au1300 Alchemy SoCs. It maintains device ID tables, allocates DMA channels, allocates and initializes descriptor rings, queues source/destination buffers or whole descriptors, starts/stops/resets channels, handles DBDMA interrupts, and saves/restores DBDMA controller registers across syscore suspend.

## Important APIs, Types, And Functions
Exported APIs include `au1xxx_ddma_get_nextptr_virt()`, `au1xxx_ddma_add_device()`, `au1xxx_ddma_del_device()`, `au1xxx_dbdma_chan_alloc()`, `au1xxx_dbdma_set_devwidth()`, `au1xxx_dbdma_ring_alloc()`, `au1xxx_dbdma_put_source()`, `au1xxx_dbdma_put_dest()`, `au1xxx_dbdma_get_dest()`, `au1xxx_dbdma_stop()`, `au1xxx_dbdma_start()`, `au1xxx_dbdma_reset()`, `au1xxx_get_dma_residue()`, `au1xxx_dbdma_chan_free()`, `au1xxx_dbdma_dump()`, and `au1xxx_dbdma_put_dscr()`.

Important state includes `dbdma_gptr`, `dbdma_initialized`, `dbdev_tab`, `chan_tab_ptr[]`, `au1xxx_dbdma_spin_lock`, CPU-specific device tables for Au1550/Au1200/Au1300, `DBDEV_TAB_SIZE`, and `alchemy_dbdma_pm_data`. The init path is `alchemy_dbdma_init()` as a `subsys_initcall()`, which calls `dbdma_setup()` for supported CPU types.

## Control Flow
Initialization allocates a 64-entry device table, copies the first 32 built-in device descriptors for the selected CPU, marks the custom half free, disables/configures the DBDMA block, enables interrupts, requests the single DBDMA IRQ, and registers syscore suspend/resume ops. Drivers can add custom device IDs, allocate a channel for source/destination IDs, allocate a descriptor ring, queue buffers by setting descriptor addresses/counts/flags, and start the hardware. Doorbell writes notify the DMA engine after descriptors are made valid.

Interrupt handling reads the global interrupt status, selects the first set channel with `__ffs()`, clears that channel's interrupt, calls the optional channel callback, and advances `cur_ptr`. Stop disables the channel and waits for halt status. Reset rewinds get/put/current pointers and clears descriptor valid/software status bits. Channel free stops hardware, frees the descriptor allocation, clears device in-use bits, drops the channel table entry, and frees the channel metadata.

## State And Persistence
The file persists global device reservations, channel allocations, descriptor rings, hardware channel registers, callback pointers, and custom device table entries. Descriptor memory is allocated from DMA-capable memory and uses physical pointer fields for hardware. On noncoherent parts, buffer and descriptor cache maintenance is explicit before/after queueing. Suspend snapshots global config and each channel's six register words, halts channels, disables interrupts, and restores those registers on resume.

## Dependencies And Integration Points
It depends on Alchemy DBDMA register/header definitions, DMA coherency state from `dma_default_coherent`, cache maintenance helpers, IRQ core, syscore PM, KSEG1 MMIO mapping, and driver clients that use `au1xxx_dbdma_*` APIs. `platform.c` registers Ethernet MAC resources with MACDMA windows, and peripheral drivers use command IDs from the CPU-specific device tables.

## Risks
The channel ID ABI is a casted pointer-to-`chan_tab_ptr` entry stored in a 32-bit `u32`, which assumes 32-bit kernel address semantics. Several exported APIs trust `chanid` and descriptor pointers without validation. Channel allocation releases source/destination flags without a lock on one failure path, and queue functions assume only one producer per channel despite comments about multiple callers. `dbdma_interrupt()` handles only the first pending bit, so simultaneous channel interrupts depend on retriggering. Cache maintenance is manual and easy to get wrong for noncoherent or stale-data erratum parts. Suspend waits indefinitely for halt bits in syscore suspend, unlike `au1xxx_dbdma_stop()` which has a timeout.

## Test Signals
Build Au1550, Au1200, and Au1300 configurations and confirm DBDMA initializes and requests the expected IRQ. Driver-level tests should allocate channels for UART/PSC/SD/AES/MAC/custom devices, allocate rings with aligned descriptors, queue source and destination buffers, verify callbacks and residue, stop/reset/restart channels, and free channels without leaks. Stress tests should cover simultaneous channel interrupts, descriptor-ring-full returns, invalid device IDs, custom add/delete exhaustion, noncoherent cache paths, and suspend/resume while channels are active.
