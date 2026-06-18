# subset-b-004636 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/farch.c -->
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

Persistent driver-owned hardware state includes:

- `efx->next_buffer_table`, special buffer indices, and buffer table entries for TX/RX/event queues.
- Queue counters such as `write_count`, `insert_count`, `notified_count`, `added_count`, `removed_count`, `scatter_n`, and `flush_pending`.
- Atomic flush counters on `efx`: `active_queues`, `rxq_flush_pending`, and `rxq_flush_outstanding`.
- Interrupt error throttling in `int_error_count` and `int_error_expire`.
- RSS state in `efx->rss_context.rx_indir_table`.
- Filter state in `efx->filter_state`, including occupied bitmaps, software filter specs, per-type search limits, and default filter entries.
- Multicast hash and unicast filter mode cached on `efx`.

The file explicitly persists filter state across hardware reset by keeping software copies and replaying them in `efx_farch_filter_table_restore()`. Queue hardware state is rebuilt through probe/init paths. `efx_farch_finish_flr()` exists because reset can leave flush counters stale when completion events were never delivered.

## Dependencies and Integration Points

This implementation depends heavily on:

- `farch_regs.h` for register offsets, table sizes, field locations, descriptor formats, and event encodings.
- `io.h` for locked 128-bit CSR/SRAM access and special unlocked page-register doorbells.
- `filter.h` for generic filter specs, match flags, priorities, and RX/TX flags.
- `bitfield.h` macros such as `EFX_POPULATE_OWORD_*`, `EFX_SET_OWORD_FIELD`, and `EFX_QWORD_FIELD`.
- Common driver structures and helpers in `net_driver.h`, `efx.h`, `rx_common.h`, `tx_common.h`, and `nic.h`.
- Siena-specific helpers such as `efx_siena_alloc_buffer()`, `efx_siena_free_buffer()`, `efx_siena_xmit_done()`, `efx_siena_rx_packet()`, `efx_siena_fast_push_rx_descriptors()`, `efx_siena_schedule_reset()`, MCDI event handling, and optional SR-IOV hooks.
- Linux kernel PCI, IRQ, netdevice, bitmap, rwsem, spinlock, atomic, waitqueue, RFS, and multicast address APIs.

## Risks and Edge Cases

- MMIO ordering is critical. Descriptor writes require `wmb()` before hardware doorbells, while special buffer and CSR writes depend on the BIU locking model in `io.h`.
- Register programming is hardware-revision sensitive. Incorrect `farch_regs.h` offsets or field widths can silently corrupt unrelated hardware state.
- Flush completion depends on event delivery. The code has fallback TX polling and FLR counter repair, but RX flush failures or missing wakeups can still force timeout/reset.
- Filter hash probing can fail with `-EBUSY`; hint filters intentionally use a short search limit, while required filters may probe deeper.
- Priority and auto-filter restoration are subtle. Removing a filter with `EFX_FILTER_FLAG_RX_OVER_AUTO` restores an automatic default rather than clearing the entry.
- RX scatter and descriptor pointer validation protect packet assembly, but unexpected event order schedules a disabling reset.
- Fatal interrupt handling disables PCI bus mastering and can permanently disable the NIC after repeated internal errors.
- SR-IOV changes SRAM partitioning and flush behavior; VF buffer table limits can reduce configured VF count.

## Test Signals

Useful validation signals include successful probe/init/remove cycles, register self-test success from `efx_farch_test_registers()`, TX completion progress through `efx_siena_xmit_done()`, RX packet delivery with expected checksum flags and scatter behavior, clean queue teardown without `failed to flush` logs, successful FLR/restart without stale flush counters, interrupt test events landing on the expected CPU, RSS indirection round trips, filter insert/get/remove/list behavior including default filter restoration, ARFS hint expiry under `CONFIG_RFS_ACCEL`, and absence of fatal interrupt/reset logs under stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/farch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/farch_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/farch_regs.h

## Purpose

`farch_regs.h` is the hardware ABI map for Falcon/Siena architecture devices. It defines MMIO register offsets, table base addresses, row counts, row strides, bitfield low-bit positions, bitfield widths, and enumerated values for Falcon A, Falcon B, and Siena C revisions. Driver code uses these constants with the bitfield and IO helpers to construct register values, descriptors, event decoders, and filter table entries.

The file is declarative: it contains no executable functions and no mutable state. Its correctness is foundational for all Falcon/Siena hardware access.

## Important APIs, Types, and Constants

The naming convention encodes object type and hardware revision:

- `FR_*` names are MMIO register or table addresses.
- `FRF_*` names are register bitfields.
- `FSE_*` and `FFE_*` names are enumerated field values.
- `FSF_*` names describe host-memory structures such as events and descriptors.
- `FPCR_*` and `FPCRF_*` describe Falcon B0 PCIe core indirect registers.
- Suffixes such as `AZ`, `BZ`, `CZ`, `AA`, `BB`, and `AB` describe the first and last hardware revisions where the definition applies.

Major register groups include:

- Interrupt control and status: `FR_AZ_INT_EN_KER`, `FR_AZ_INT_ADR_KER`, `FR_BZ_INT_ISR0`, `FR_AZ_FATAL_INTR_KER`, and `FSF_AZ_NET_IVEC_FATAL_INT`.
- Global reset, debug, GPIO, SRAM, and memory parity registers.
- Event queue registers and tables: `FR_BZ_EVQ_RPTR`, `FR_AZ_DRV_EV`, `FR_AZ_EVQ_CTL`, `FR_BZ_TIMER_TBL`, `FR_BZ_EVQ_PTR_TBL`, and event code fields.
- Buffer table registers: `FR_AZ_BUF_TBL_CFG`, `FR_AZ_BUF_TBL_UPD`, full/half buffer table addresses, and buffer descriptor fields.
- RX/TX descriptor update and pointer tables: `FR_BZ_RX_DESC_UPD_P0`, `FR_BZ_TX_DESC_UPD_P0`, `FR_BZ_RX_DESC_PTR_TBL`, `FR_BZ_TX_DESC_PTR_TBL`, and queue enable/size/flush fields.
- RX/TX datapath configuration, descriptor cache, filter control, RSS, and pacing registers.
- MAC, GMAC, XGMAC, MDIO, XAUI/XGXS, VLAN, and statistics control registers.
- RX/TX filter tables: `FR_BZ_RX_FILTER_TBL0`, `FR_CZ_RX_MAC_FILTER_TBL0`, `FR_CZ_TX_FILTER_TBL0`, and `FR_CZ_TX_MAC_FILTER_TBL0`.
- Host-memory event and descriptor layouts: `DRIVER_EV`, `EVENT_ENTRY`, `RX_EV`, `TX_EV`, `RX_KER_DESC`, `TX_KER_DESC`, `RX_USER_DESC`, and `TX_USER_DESC`.

Pseudo-registers and aliases near the end adapt awkward hardware layouts to driver use, such as:

- `FR_AZ_RX_DESC_UPD_DWORD_P0` and `FR_AZ_TX_DESC_UPD_DWORD_P0`, which select only the high dword used by the fast-path doorbell.
- Combined field aliases for SRAM bank/size and wide MAC address fields.
- `FSF_AZ_DRV_GEN_EV_MAGIC`, which is used by generated test/refill/drain events.
- `FS_BZ_RX_PREFIX_HASH_OFST` and `FS_BZ_RX_PREFIX_SIZE`, which describe the RX prefix format.

## Control Flow

There is no runtime control flow in this header. Its constants are consumed by control flow elsewhere:

- `farch.c` uses queue table constants to initialize, flush, and tear down RX/TX/event queues.
- `farch.c` decodes `FSF_AZ_EV_CODE`, `FSF_AZ_RX_EV_*`, `FSF_AZ_TX_EV_*`, and driver event subcodes in event processing.
- Filter insertion in `farch.c` uses filter table offsets, row counts, strides, and fields to build hardware entries and update search-limit registers.
- `io.h` uses the descriptor update aliases to constrain page-mapped write helpers to legal register offsets.

## State and Persistence Behavior

The header has no state and performs no persistence. It defines the address and bit layout of state that lives in device registers, SRAM tables, host-memory descriptors, event queues, and the MSI-X tables. Any persistence behavior is implemented by caller code that rewrites these locations after reset.

## Dependencies and Integration Points

`farch_regs.h` is included by `farch.c` and other Siena/Falcon hardware-specific files. It assumes the bitfield macros can combine each `*_LBN` and `*_WIDTH` pair into extracts and populated words. It also integrates with compile-time checks in the C code, for example verifying descriptor update register aliases or table row counts against array sizes.

The header is tightly coupled to the hardware manuals. It is also coupled to the driver's revision model: the same source needs to support Falcon A1, Falcon B0, and Siena A0 differences without runtime string parsing or generated metadata.

## Risks and Edge Cases

- A wrong offset, stride, row count, field position, or width can cause driver writes to target the wrong CSR or to encode invalid hardware commands.
- Some definitions overlap by revision. Callers must choose revision-appropriate constants through NIC type data and compile-time checks.
- Pseudo-register aliases intentionally depend on specific register layouts. If a base address changes, the fast-path high-dword doorbell aliases must change too.
- Several hardware blocks expose wide fields split into low/high aliases. Callers must use the intended split definitions for 48-bit MAC fields and combined size fields.
- Event and descriptor layouts are consumed on hot paths; incorrect definitions would manifest as packet loss, checksum misclassification, spurious resets, or queue hangs rather than ordinary compile failures.

## Test Signals

Meaningful signals are indirect: successful compilation of all `EFX_*FIELD*` macro uses, passing register self-tests, correct queue initialization, valid RX/TX event decoding, working filter insertion/removal, RSS table round trips, interrupt test delivery, and clean reset/reprobe cycles. Hardware or emulation tests that exercise all supported revisions are especially important because many constants are revision-specific.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/farch_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/filter.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/filter.h

## Purpose

`filter.h` defines the generic hardware filter specification contract used by the Solarflare driver. It gives common code and hardware-specific backends a shared representation for RX/TX filters, match fields, priorities, flags, encapsulation types, queue targets, RSS behavior, VLANs, MAC addresses, IP addresses, and ports.

The file also provides inline initializers and setters that keep callers from manually assembling inconsistent `struct efx_filter_spec` values.

## Important APIs, Types, and Functions

Core enums:

- `enum efx_filter_match_flags` declares match dimensions such as remote/local host, remote/local port, local/remote MAC, EtherType, VLAN IDs, IP protocol, local MAC I/G bit, and encapsulation type.
- `enum efx_filter_priority` orders replacement policy: hint, auto, manual, and required.
- `enum efx_filter_flags` declares RX RSS, RX scatter, RX-over-auto, RX direction, and TX direction flags.
- `enum efx_encap_type` represents no encapsulation, VXLAN, NVGRE, GENEVE, and an IPv6 outer-frame flag.

Primary data structure:

- `struct efx_filter_spec` is a packed logical filter description with bitfields for match flags, priority, direction/behavior flags, DMA queue ID, RSS context user ID, VLAN IDs, local/remote MACs, EtherType, protocol, IPv4/IPv6 local and remote hosts, ports, and encapsulation type.

Constants:

- `EFX_FILTER_RX_DMAQ_ID_DROP` is the special RX queue target used for drop filters.
- `EFX_FILTER_VID_UNSPEC` marks an unspecified outer VLAN in Ethernet-local filter setters.

Inline helpers:

- `efx_filter_init_rx()` zeroes a spec, sets priority, RX flags, RSS context zero, and target RX queue.
- `efx_filter_init_tx()` zeroes a spec and creates a required TX filter targeting a TX queue.
- `efx_filter_set_ipv4_local()` sets an IPv4 local 2-tuple match.
- `efx_filter_set_ipv4_full()` sets an IPv4 4-tuple match.
- `efx_filter_set_eth_local()` sets local MAC and/or outer VLAN matching.
- `efx_filter_set_uc_def()` and `efx_filter_set_mc_def()` create default unicast and multicast/broadcast filters based on the local MAC I/G bit.
- `efx_filter_set_encap_type()` and `efx_filter_get_encap_type()` manage optional encapsulation matching.

## Control Flow

The header has only inline construction helpers. Normal caller flow is:

1. Call `efx_filter_init_rx()` or `efx_filter_init_tx()` to zero and direction-initialize a spec.
2. Call one or more setters to add match dimensions.
3. Pass the completed spec to a NIC-specific insertion operation such as the Falcon/Siena implementation in `farch.c`.

The setters are additive: they OR match flags and fill corresponding fields. `efx_filter_set_eth_local()` rejects the empty case where both VID and address are unspecified.

## State and Persistence Behavior

`filter.h` owns no global state. Each `efx_filter_spec` is caller-owned stack or heap data. Persistence is handled by hardware-specific code that stores accepted specs in per-NIC filter tables and replays them after reset. In the Siena Falcon-architecture implementation, `farch.c` converts these generic specs into `efx_farch_filter_spec` entries under `efx->filter_state`.

## Dependencies and Integration Points

The header depends on Linux types, Ethernet address definitions, byte-order helpers, `htons()`, and `ether_addr_copy()`. It is consumed by generic driver features such as receive mode programming, ethtool/NFC-like filter management, accelerated RFS, SR-IOV/user-level networking paths, and NIC-specific backends.

The comments document hardware capability differences: Falcon supports a smaller IPv4 RX filter set, Siena supports RX/TX IPv4 and MAC/default filters, and later hardware can support firmware-controlled IPv4/IPv6, VLAN, MAC, I/G, and encapsulated filters.

## Risks and Edge Cases

- Callers must initialize specs with the provided init functions; otherwise stale fields may be interpreted by hardware backends.
- `match_flags` combinations are not universally supported. Backends may return `-EPROTONOSUPPORT`, `-EINVAL`, or related errors for legal-looking but unsupported combinations.
- `rss_context` has user-level semantics where zero means the default driver RSS context, not necessarily a firmware context ID.
- `EFX_FILTER_FLAG_RX_OVER_AUTO` is backend-owned. External callers setting it directly could break auto-filter restoration semantics.
- The struct stores room for IPv6 addresses and encapsulation, but Falcon/Siena code in this subset only accepts narrower IPv4/MAC/default combinations.

## Test Signals

Useful tests include initializer zeroing checks, setter field/match flag checks, rejection of empty Ethernet-local filters, round-trip conversion through hardware-specific get operations, priority replacement behavior in the backend, RX RSS/scatter flag propagation, default unicast/multicast filter behavior, and unsupported match combinations returning stable errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/io.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/io.h

## Purpose

`io.h` provides low-level MMIO and SRAM access helpers for the Solarflare driver. For Falcon/Siena hardware it encodes the Bus Interface Unit locking rules needed for wide 128-bit CSR and 64-bit SRAM access, while allowing special descriptor and event doorbell writes to avoid unnecessary locking on fast paths.

The file is a safety boundary between higher-level hardware code and raw `__raw_read*()`/`__raw_write*()` operations.

## Important APIs, Types, and Functions

Configuration macros:

- `EFX_USE_QWORD_IO` is enabled on 64-bit builds and allows naturally sized 64-bit IO for wide writes/reads.
- `EFX_USE_PIO` is enabled only on x86_64 with write-combining support.
- `EFX_DEFAULT_VI_STRIDE` and `EF100_DEFAULT_VI_STRIDE` define per-VI page register strides.

Raw access wrappers:

- `_efx_writeq()` and `_efx_readq()` perform raw 64-bit MMIO when available.
- `_efx_writed()` and `_efx_readd()` perform raw 32-bit MMIO.
- `efx_reg()` adds a NIC register base to a register offset.

Locked wide access:

- `efx_writeo()` writes a 128-bit CSR under `efx->biu_lock`.
- `efx_reado()` reads a 128-bit CSR under `efx->biu_lock`.
- `efx_sram_writeq()` and `efx_sram_readq()` access 64-bit SRAM entries through a caller-supplied mapping under the same lock.

Unlocked narrow/special access:

- `efx_writed()` and `efx_readd()` access 32-bit CSRs without taking `biu_lock`.
- `efx_writeo_table()` and `efx_reado_table()` index 128-bit CSR tables.
- `efx_paged_reg()` computes page-mapped register offsets from `page * efx->vi_stride + reg`.
- `efx_writeo_page()` writes the whole special RX/TX descriptor update register for allowed offsets only.
- `efx_writed_page()` writes allowed page-mapped 32-bit registers or high dwords of special descriptor update registers.
- `efx_writed_page_locked()` handles the TIMER_COMMAND page-zero BIU bug by locking only for page 0.

## Control Flow

The main control-flow decision is whether an operation must serialize with the BIU collector. Normal 128-bit CSR writes, wide CSR reads, and SRAM access take `efx->biu_lock`, emit the raw writes/reads in the correct order, and release the lock. Narrow 32-bit CSR access skips locking.

Page-register helpers first compute the page-mapped offset using `efx->vi_stride`. Macro wrappers add compile-time `BUILD_BUG_ON_ZERO()` validation so only known-safe register offsets are passed to special no-lock write paths.

## State and Persistence Behavior

The header owns no persistent state, but it mutates device register and SRAM state through MMIO. Its only driver state dependency is `efx->biu_lock`, `efx->membase`, `efx->reg_base`, `efx->vi_stride`, and debug logging fields. Correct lock use protects the BIU collector from interleaved wide writes that could lose data.

## Dependencies and Integration Points

`io.h` depends on Linux IO and spinlock APIs and on driver-defined `efx_nic`, `efx_oword_t`, `efx_qword_t`, and `efx_dword_t` types plus debug formatting macros. It is included by `farch.c` and other low-level NIC code that programs registers listed in `farch_regs.h`.

The helper contract is tightly coupled to hardware behavior:

- Falcon/Siena 128-bit CSRs are not host-atomic.
- The BIU buffers partial wide writes until all dwords are collected.
- Descriptor update registers have special high-dword semantics that permit fast-path write-pointer updates without full 128-bit locking.
- TIMER_COMMAND page 0 has a special bug that invalidates the collector unless locked.

## Risks and Edge Cases

- Using `efx_writed()` against a non-special part of a wide CSR can corrupt or discard BIU collector state.
- Omitting `biu_lock` for ordinary 128-bit CSR/SRAM access can interleave writes from different call sites and lose register updates.
- Using the page helpers with an incorrect `vi_stride` or illegal offset would target the wrong queue/register; the macro checks reduce but do not eliminate misuse.
- Architecture-specific 64-bit IO assumptions affect PIO and write-combining behavior.
- These helpers do not provide higher-level memory ordering for descriptor contents; callers such as `farch.c` still need explicit barriers before ringing doorbells.

## Test Signals

Test signals include clean register self-tests, stable queue initialization under concurrent channels, no lost writes during stress/repeated reset, correct TX/RX descriptor doorbell behavior, timer programming on page 0 without corrupting subsequent wide writes, successful operation on both 32-bit and 64-bit builds, and hardware debug logs showing expected register addresses and values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/io.h -->
