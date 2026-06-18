# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/farch.c

## Purpose

`farch.c` is the Falcon-architecture hardware implementation layer for the Solarflare Siena/SFC9000 network driver. It bridges the generic Siena net driver data structures (`efx_nic`, `efx_channel`, TX/RX queues, filter specs, reset state, RSS context, SR-IOV hooks) to Falcon/Siena MMIO registers, SRAM buffer tables, descriptor rings, event queues, interrupt paths, RSS indirection, and hardware filter tables.

The file is not a standalone device driver entry point. It is a backend selected through NIC type operations and called by common Siena code during probe, queue setup, datapath operation, reset, filter programming, and teardown.

## Important APIs, Types, and Functions

Hardware/register helpers:

- `efx_farch_test_registers()` performs destructive masked bit-sweep tests against a register list, preserving the original value on success and returning `-EIO` on mismatch.
- `efx_write_buf_tbl()`, `efx_init_special_buffer()`, `efx_fini_special_buffer()`, `efx_alloc_special_buffer()`, and `efx_free_special_buffer()` manage NIC buffer table mappings for descriptor and event queues.

TX path:

- `efx_farch_tx_probe()`, `efx_farch_tx_init()`, `efx_farch_tx_fini()`, and `efx_farch_tx_remove()` allocate, configure, disable, and free TX descriptor rings.
- `efx_farch_tx_write()` converts software TX buffers into `TX_KER_DESC` entries, uses `wmb()` before doorbells, and chooses descriptor push versus write-pointer notification.
- `efx_farch_tx_limit_len()` caps descriptors at 4 KiB boundaries.

RX path:

- `efx_farch_rx_probe()`, `efx_farch_rx_init()`, `efx_farch_rx_fini()`, and `efx_farch_rx_remove()` mirror TX lifecycle for RX descriptor rings.
- `efx_farch_rx_write()` builds RX descriptors up to `added_count`, publishes them with a write memory barrier, and rings the RX descriptor update doorbell.
- `efx_farch_rx_defer_refill()` injects a generated event so an otherwise idle event queue can refill RX descriptors.

Flush and reset:

- `efx_farch_fini_dmaq()` coordinates queue flush during DMA teardown unless the NIC is in EEH recovery.
- `efx_farch_do_flush()` starts TX flushes, batches RX flushes up to `EFX_RX_FLUSH_COUNT`, optionally asks SR-IOV firmware to flush RX queues, waits on `flush_wq`, and times out after 5 seconds.
- `efx_farch_finish_flr()` clears queue flush accounting after FLR recovery.

Events and interrupts:

- `efx_farch_ev_probe()`, `efx_farch_ev_init()`, `efx_farch_ev_fini()`, and `efx_farch_ev_remove()` manage event queue buffers and pointer table entries.
- `efx_farch_ev_process()` scans event entries until an all-ones empty marker or budget exhaustion, clears consumed events, and dispatches RX, TX, driver, generated, SR-IOV user, MCDI, and global events.
- `efx_farch_legacy_interrupt()` reads and acknowledges the legacy ISR, handles fatal interrupt state, schedules channel processing, and handles the known one-time zero ISR case.
- `efx_farch_msi_interrupt()` schedules a channel directly from MSI/MSI-X context.
- `efx_farch_fatal_interrupt()` disables bus mastering, disables interrupts, rate-limits repeated internal errors, and schedules either reset or disable.

Resource and common hardware setup:

- `efx_farch_rx_push_indir_table()` and `efx_farch_rx_pull_indir_table()` synchronize RSS indirection table rows.
- `efx_farch_dimension_resources()` partitions SRAM between channel buffer table entries, SR-IOV VFs, RX descriptor caches, and TX descriptor caches.
- `efx_farch_fpga_ver()` reads the Altera build register.
- `efx_farch_init_common()` programs descriptor cache bases/sizes, interrupt DMA address, fatal interrupt masks, TX prefetch/backoff behavior, TX push enablement, and pacing defaults.

Filter subsystem:

- Private types `efx_farch_filter_spec`, `efx_farch_filter_table`, and `efx_farch_filter_state` hold Falcon-specific filter state, hardware table metadata, search limits, software copies of filter specs, and a bitmap of occupied entries.
- `efx_farch_filter_table_probe()` allocates filter state, initializes RX IP, RX MAC, RX default, and TX MAC tables, seeds default RX filters, and pushes RX filter config.
- `efx_farch_filter_insert()`, `efx_farch_filter_remove_safe()`, `efx_farch_filter_get_safe()`, `efx_farch_filter_clear_rx()`, `efx_farch_filter_count_rx_used()`, and `efx_farch_filter_get_rx_ids()` provide the externally useful filter operations.
- `efx_farch_filter_table_restore()` rewrites software-persistent filter specs to hardware after reset.
- `efx_farch_filter_update_rx_scatter()` adjusts scatter flags for filters targeting local RX queues.
- `efx_farch_filter_rfs_expire_one()` conditionally expires accelerated RFS hint filters.
- `efx_farch_filter_sync_rx_mode()` updates software unicast-filter mode and multicast hash state from `net_device` flags and multicast addresses.

## Control Flow

Queue setup is a staged lifecycle. Probe allocates DMA-coherent special buffers and reserves buffer table IDs. Init writes those buffers into the NIC buffer table and programs descriptor pointer tables. Fast-path writers populate host-memory descriptors, issue memory barriers, then notify hardware through page-mapped descriptor update registers. Fini disables hardware pointer table entries and clears buffer table ranges. Remove frees host memory.

RX event control flow is descriptor-order sensitive. `efx_farch_ev_process()` dispatches RX events to `efx_farch_handle_rx_event()`, which validates descriptor pointer order and scatter state, handles partial or bad-index recovery, interprets checksum/classification bits, applies multicast mismatch discard logic, and completes packets through `efx_siena_rx_packet()`.

TX event flow consumes batched completions. `efx_farch_handle_tx_event()` calls `efx_siena_xmit_done()` when completion bits are present, rewrites the TX descriptor write pointer when the work queue FIFO is full, and schedules DMA reset on packet error.

Flush control flow starts all TX flushes, marks RX queues pending, then alternates between requesting available RX flushes and waiting for driver/generated drain events. Completion events either generate drain magic events or requeue failed RX flushes. If events are lost, TX table polling can synthesize missing TX drain events.

Filter insertion translates a generic `efx_filter_spec` into Falcon fields, selects a table, probes a hash collision chain for replacement or insertion space, applies priority rules, updates software state, writes the hardware entry, and pushes RX/TX search limit registers when the required probe depth grows.

## State and Persistence Behavior

Persistent driver-owned hardware state includes `efx->next_buffer_table`, special buffer indices, queue counters, atomic flush counters, interrupt error throttling, RSS indirection state, filter state, multicast hash state, and unicast filter mode. The file explicitly persists filter state across hardware reset by keeping software copies and replaying them in `efx_farch_filter_table_restore()`. Queue hardware state is rebuilt through probe/init paths. `efx_farch_finish_flr()` repairs stale flush counters after reset paths that lose completion events.

## Dependencies and Integration Points

This implementation depends on `farch_regs.h` for hardware layout, `io.h` for safe CSR/SRAM access, `filter.h` for generic filter specs, `bitfield.h` field macros, common driver structures in `net_driver.h`, `efx.h`, `rx_common.h`, `tx_common.h`, and `nic.h`, and Siena helpers for buffer allocation, packet completion, reset scheduling, MCDI, SR-IOV, and RFS.

## Risks and Edge Cases

MMIO ordering, descriptor barriers, and BIU locking are critical. Flush completion can time out if events are lost. Filter probing can return `-EBUSY`, and priority/auto-filter restoration is subtle. RX scatter and descriptor pointer validation intentionally schedule resets on serious ordering errors. Fatal interrupts disable bus mastering and can disable the NIC after repeated internal errors. SR-IOV changes SRAM partitioning and flush behavior.

## Test Signals

Useful validation signals include register self-test success, probe/init/remove cycles, TX completion progress, RX packet delivery with expected flags, clean queue teardown, FLR/restart without stale flush counters, interrupt test delivery, RSS indirection round trips, filter insert/get/remove/list behavior, ARFS hint expiry, and absence of fatal interrupt/reset logs under stress.
