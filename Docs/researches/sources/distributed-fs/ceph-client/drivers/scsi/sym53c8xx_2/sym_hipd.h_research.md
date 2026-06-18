# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_hipd.h

## Purpose

`sym_hipd.h` is the main hardware-private contract for the Symbios/LSI 53C8xx and 53C1010 SCSI host adapter driver. It defines the script-visible memory layouts, software state structures, MMIO access helpers, DMA scatter/gather builders, and allocator interfaces used by the rest of the `sym53c8xx_2` driver. The file is not a standalone implementation; it is the shape agreement between the Linux SCSI glue, firmware/SCRIPTS engine, NVRAM policy, and DMA allocator.

## Important APIs, Types, And Functions

Important constants include host status values (`HS_IDLE`, `HS_BUSY`, `HS_COMPLETE`, `HS_SEL_TIMEOUT`, `HS_COMP_ERR`), software interrupt reasons (`SIR_*`), extended error bits (`XE_*`), negotiation status (`NS_SYNC`, `NS_WIDE`, `NS_PPR`), device/host policy flags (`SYM_DISC_ENABLED`, `SYM_TAGS_ENABLED`, `SYM_AVOID_BUS_RESET`), queue sizing (`SYM_CONF_MAX_QUEUE`, `MAX_QUEUE`), and DMA addressing-mode masks.

Key hardware access macros are `INB/INW/INL`, `OUTB/OUTW/OUTL`, offset variants, bit set/clear helpers, `OUTL_DSP()`, and `OUTONB_STD()`. These wrap `ioread*()`/`iowrite*()` against `np->s.ioaddr` and add memory barriers before restarting the SCRIPTS processor.

The main types are `struct sym_trans` for negotiated transfer parameters, `struct sym_tcb` and `struct sym_lcb` for target and LUN state, `struct sym_ccb` for per-command state, `struct sym_dsb` for the script-visible data structure block, and `struct sym_hcb` for host adapter state. `struct sym_ccbh`, `struct sym_tcbh`, and `struct sym_lcbh` are explicitly laid out headers copied or directly loaded by SCRIPTS depending on chip features. Allocator-facing types include `m_pool_ident_t`, `struct sym_m_vtob`, and `struct sym_m_pool`.

The exported driver methods declared here include firmware binding (`sym_find_firmware()`, `sym_fw_bind_script()`), host/interrupt control (`sym_start_up()`, `sym_interrupt()`, `sym_reset_scsi_bus()`), command lifecycle (`sym_get_ccb()`, `sym_free_ccb()`, `sym_queue_scsiio()`, `sym_abort_scsiio()`), target/LUN lifecycle (`sym_alloc_lcb()`, `sym_free_lcb()`), and host allocation/attach (`sym_hcb_attach()`, `sym_hcb_free()`).

## Control Flow And State

The structures expose the runtime flow expected by the driver. A Linux `scsi_cmnd` is wrapped by a `sym_ccb`; its first member is `struct sym_dsb`, which is addressed by the chip DSA register. The DSB contains the script entry points, phase mismatch contexts, selection tables, message/CDB/sense table moves, and the scatter/gather move table. The host keeps free, busy, and completion CCB queues plus hashed CCB lookup by DSA bus address.

Target state is split into `sym_tcb` and `sym_lcb`. The target block holds desired and last-printed transfer parameters, NVRAM/user flags, negotiated command limits, and pointers to LUN structures. The LUN block maintains task tables, busy tagged/untagged counters, tag allocation buffers, optional device queueing state, and command reordering counters. `sym_lp()` hides the LUN 0 fast path versus allocated multi-LUN table.

`sym_hcb` is persistent per-adapter state. It stores saved and runtime chip register values, script RAM/main-memory addresses, firmware callback pointers, queue producer/consumer positions, controller capabilities, DMA mode state, abort buffers, and 64-bit DMA segment maps where enabled. The SCRIPTS processor observes several of these fields directly, so layout and byte order conversions are part of the ABI.

## Dependencies And Integration Points

This header depends on Linux memory/DMA/MMIO facilities, SCSI core types, and many driver-private definitions from surrounding `sym53c8xx_2` headers such as register layouts, firmware address tables, table move/select records, and OS-specific `sym_shcb` fields. It integrates with `sym_malloc.c` through `__sym_calloc_dma()`, `__sym_mfree_dma()`, and `__vtobus()`, and with NVRAM code by storing `usrflags`, `usr_period`, `usr_width`, and `usrtags` in each target.

The DMA scatter/gather builder has three compile-time modes. Mode 0 writes a 32-bit bus address and length. Mode 1 packs address bits 32-39 into the high byte of the size field. Mode 2 uses chip DMA segment registers and `sym_lookup_dmap()` to map 64-bit upper address bits into a segment selector. These fields are consumed by firmware/SCRIPTS, so incorrect packing causes silent data corruption.

## Risks And Test Signals

The largest risk is ABI drift between C layouts and SCRIPTS offsets. Comments state that CCB/TCB/LCB headers and phase mismatch contexts must remain at specific offsets, and several fields are read by chip scripts with limited arithmetic. Any structure edit needs compile-time layout review and hardware/firmware tests.

Other risks are DMA address truncation in the wrong `SYM_CONF_DMA_ADDRESSING_MODE`, missing memory barriers before script restart, queue size misconfiguration beyond a page, and stale global header copies on chips without `FE_LDSTR`. Useful tests are boot/probe on each supported chip class, heavy tagged queue I/O, disconnect/reselect stress, sync/wide/PPR negotiation, 64-bit DMA boundary tests, abort/reset paths, and debug-flag traces for allocation, negotiation, queue, result, and phase behavior.
