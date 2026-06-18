# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/farch.c

## Purpose

`farch.c` implements Falcon-architecture hardware support shared by Falcon/SFC4000 revisions for descriptor rings, event queues, interrupts, queue flushing, descriptor-cache setup, RX RSS indirection, and hardware filters. It is the low-level data-path engine used by the `falcon_a1_nic_type` and `falcon_b0_nic_type` operation tables in `falcon.c`.

The file translates generic driver objects (`struct ef4_tx_queue`, `struct ef4_rx_queue`, `struct ef4_channel`, `struct ef4_filter_spec`) into Falcon register-table entries and DMA-visible ring formats. It also consumes Falcon event queue entries and dispatches them to the generic TX/RX completion, reset, refill, and filter machinery.

## Important APIs, Types, And Functions

Special-buffer helpers (`ef4_alloc_special_buffer()`, `ef4_init_special_buffer()`, `ef4_fini_special_buffer()`, `ef4_free_special_buffer()`) allocate DMA buffers for descriptor/event rings, reserve buffer-table IDs from `efx->next_buffer_table`, and write/clear Falcon buffer table entries.

TX APIs include `ef4_farch_tx_probe()`, `ef4_farch_tx_init()`, `ef4_farch_tx_write()`, `ef4_farch_tx_limit_len()`, `ef4_farch_tx_fini()`, and `ef4_farch_tx_remove()`. `ef4_farch_tx_write()` converts software TX buffers into hardware qword descriptors, advances `write_count`, uses a write memory barrier, then either pushes the first descriptor or rings the TX doorbell.

RX APIs include `ef4_farch_rx_probe()`, `ef4_farch_rx_init()`, `ef4_farch_rx_write()`, `ef4_farch_rx_fini()`, `ef4_farch_rx_remove()`, and `ef4_farch_rx_defer_refill()`. RX initialization programs descriptor queue table entries with event queue label, buffer base, size, scatter/jumbo behavior, and iSCSI digest bits. RX writes build qword descriptors for newly added buffers and update the hardware write pointer.

Flush and FLR APIs include `ef4_farch_fini_dmaq()`, `ef4_farch_finish_flr()`, `ef4_farch_do_flush()`, `ef4_farch_flush_tx_queue()`, `ef4_farch_flush_rx_queue()`, and helpers for flush wakeup/completion. They coordinate TX and RX descriptor queue flush commands, flush completion events, generated drain events, retry of failed RX flushes, and cleanup after FLR where events may never arrive.

Event APIs include `ef4_farch_ev_probe()`, `ef4_farch_ev_init()`, `ef4_farch_ev_process()`, `ef4_farch_ev_read_ack()`, `ef4_farch_ev_fini()`, `ef4_farch_ev_remove()`, `ef4_farch_ev_test_generate()`, and `ef4_farch_generate_event()`. Event processing decodes RX, TX, generated, driver, and global events, clears consumed events to all-ones, updates `eventq_read_ptr`, and returns RX budget consumption.

Interrupt APIs include `ef4_farch_irq_enable_master()`, `ef4_farch_irq_disable_master()`, `ef4_farch_irq_test_generate()`, `ef4_farch_fatal_interrupt()`, `ef4_farch_legacy_interrupt()`, and `ef4_farch_msi_interrupt()`. These control the top-level interrupt enable register, schedule channel processing, detect fatal/non-event interrupt sources, and disable bus mastering on serious system errors.

Common hardware init functions include `ef4_farch_test_registers()`, `ef4_farch_fpga_ver()`, `ef4_farch_init_common()`, and `ef4_farch_rx_push_indir_table()`. `ef4_farch_init_common()` sets descriptor-cache SRAM bases/sizes, programs the interrupt-status DMA address, enables fatal interrupt sources, and configures TX DMA arbitration/pacing.

Filter support is represented by private `struct ef4_farch_filter_spec`, `struct ef4_farch_filter_table`, and `struct ef4_farch_filter_state`. Public filter operations include `ef4_farch_filter_table_probe()`, `ef4_farch_filter_table_restore()`, `ef4_farch_filter_table_remove()`, `ef4_farch_filter_insert()`, `ef4_farch_filter_remove_safe()`, `ef4_farch_filter_get_safe()`, `ef4_farch_filter_clear_rx()`, `ef4_farch_filter_count_rx_used()`, `ef4_farch_filter_get_rx_id_limit()`, `ef4_farch_filter_get_rx_ids()`, `ef4_farch_filter_update_rx_scatter()`, optional RFS hooks, and `ef4_farch_filter_sync_rx_mode()`.

## Control Flow

Queue setup is probe/init/remove/fini split. Probe allocates host DMA memory for descriptor/event rings. Init pins those buffers into Falcon buffer tables and writes descriptor/event queue pointer tables. Runtime TX/RX writes fill ring memory, issue barriers, and update hardware write pointers. Fini clears hardware tables and buffer-table entries; remove frees host memory.

TX event handling (`ef4_farch_handle_tx_event()`) handles batched completions by label and descriptor pointer, rewrites write pointers when the work-queue FIFO reports full, and schedules DMA-error reset on packet errors. RX event handling (`ef4_farch_handle_rx_event()`) validates descriptor order and start-of-packet state, supports scatter fragments through `scatter_n`, classifies checksum flags, records errors not covered by MAC stats, discards bad or unmatched multicast packets, and hands completed packets to `ef4_rx_packet()`.

Flush flow starts in `ef4_farch_fini_dmaq()`: if not in recovery and bus mastering is enabled, the NIC type's `prepare_flush()` runs, all TX queues get flush commands, RX queues become pending, and `ef4_farch_do_flush()` submits up to four concurrent RX flushes until all active queues drain or a five-second timeout expires. Hardware flush-done events trigger generated drain events so the event queues are drained of residual completions before active queue count reaches zero.

Event processing loops until an all-ones empty event is found or the RX budget is consumed. Generated events implement internal control messages: test event CPU recording, deferred RX refill, RX drain, and TX drain. Driver events cover flush completions, event queue init, SRAM update, wakeup/timer notifications, RX recovery, and descriptor fetch errors. Global events are delegated to the NIC type, which lets `falcon.c` handle PHY/XMAC and RX recovery signals.

Interrupt flow is intentionally thin. Legacy interrupts read/ack the ISR, handle fatal status from the shared interrupt-status buffer, schedule per-channel tasklets for active event queues, and compensate for zero ISR reads by checking event presence. MSI interrupts schedule the context's channel directly and check fatal status only on the selected non-event IRQ level.

Filter insertion converts a generic `ef4_filter_spec` to Falcon format, chooses RX IP/RX MAC/RX default/TX MAC table, searches for replacement and free slots using the Falcon hardware hash/increment sequence, enforces priority and replace semantics, updates software bitmaps/spec arrays, pushes search-limit registers when depth grows, writes the hardware table entry, and returns an encoded filter ID. Removal and get decode user-visible IDs defensively before touching table state.

## State And Persistence Behavior

Descriptor and event ring state is DMA memory owned by queue/channel objects. Hardware persistence consists of buffer-table entries, descriptor queue pointer-table entries, event queue pointer/read-pointer entries, interrupt registers, and filter-table registers. These are volatile and are rebuilt after reset or queue reallocation.

Flush state uses `efx->active_queues`, `efx->rxq_flush_pending`, `efx->rxq_flush_outstanding`, per-RX `flush_pending`, and per-TX `flush_outstanding`. `ef4_farch_finish_flr()` explicitly clears this state after FLR because DMA failures can prevent normal completion events.

Filter state persists across hardware reset in software as `efx->filter_state`: per-table `used_bitmap`, `spec` arrays, `used` counts, and `search_limit[]`. `ef4_farch_filter_table_restore()` replays used entries into hardware and pushes RX/TX search-limit/default-filter configuration after reset. It is not persistent across driver unload.

Runtime multicast and promiscuous mode state is captured by `ef4_farch_filter_sync_rx_mode()` in `efx->unicast_filter` and `efx->multicast_hash`, while actual MAC multicast hash register writes happen in `falcon.c`.

Synchronization uses memory barriers before doorbells/read-pointer acknowledgements, `spin_lock_bh(&efx->filter_lock)` for filter state, atomic counters for flush progress, and wait queues for flush completion. Interrupt handlers use `READ_ONCE(efx->irq_soft_enabled)` and schedule channel work rather than processing full queues in hard IRQ context.

## Dependencies And Integration Points

This file depends on Linux interrupt, PCI, module, seq-file, CRC32, and netdevice primitives plus Falcon driver headers `net_driver.h`, `bitfield.h`, `efx.h`, `nic.h`, `farch_regs.h`, `io.h`, and `workarounds.h`.

It is wired into `falcon.c` through the NIC type operation tables. It calls generic driver services such as `ef4_xmit_done()`, `ef4_rx_packet()`, `ef4_fast_push_rx_descriptors()`, `ef4_schedule_reset()`, `ef4_schedule_channel_irq()`, `ef4_try_recovery()`, `ef4_rss_enabled()`, and the register I/O helpers. Global event handling is delegated back through `efx->type->handle_global_event`.

Filter APIs are consumed by ethtool/RX/RFS paths through generic `ef4_filter_spec` operations. RSS indirection is populated by `falcon_b0_rx_push_rss_config()` in `falcon.c`. Queue sizes, register-table bases, interrupt mode, scatter capability, and filter-table availability depend on the selected Falcon revision in `struct ef4_nic_type`.

## Risks And Edge Cases

Ring and doorbell ordering is critical. Descriptors must be visible to DMA before write-pointer updates; event queue entries must be cleared before read acknowledgements. Missing barriers can produce stale DMA reads or repeated events.

Flush is inherently racy with DMA and reset. RX flush supports only four outstanding commands and may fail due to descriptor fetches, so retry/pending accounting must remain balanced. TX flush completion can be inferred by reading descriptor pointer tables when events are missing; this is essential for timeout recovery. Incorrect active queue accounting can permanently block queue reallocation.

RX event ordering and scatter handling are fragile. Bad indices may be benign partial packet truncations or serious event loss; the code distinguishes those cases and schedules RX recovery/disable when needed. Misclassifying packet-ok and checksum flags can lead to bad skb checksum state.

Fatal interrupt handling disables bus mastering and may disable the NIC after repeated errors within `EF4_INT_ERROR_EXPIRE`. It also handles EEH-style all-ones legacy ISR reads. Changes here can affect recovery from PCI errors and shared IRQ behavior.

Filter table search limits are a correctness and performance boundary. Search depth must be large enough to find installed filters but bounded to avoid hardware timeouts and software infinite loops. Default filters, auto filters, RX-over-auto replacement, priority checks, and encoded filter IDs all need to stay consistent with RX NFC and RFS expectations. The current `ef4_farch_filter_table_probe()` only initializes the RX IP table for Falcon B0 in this source; zero-sized tables intentionally cause unsupported filter classes to return `-EINVAL`.

## Test Signals

Self-test coverage includes `ef4_farch_test_registers()` bit-sweep validation and `ef4_farch_ev_test_generate()` generated event delivery. Runtime diagnostics include TX/RX descriptor fetch error events, dropped RX event logs, RX recovery event logs, fatal interrupt logs including memory parity status, flush timeout logs with active/pending/outstanding counts, and unexpected event-type logs.

Regression coverage should exercise TX descriptor push versus doorbell paths, RX scatter and bad-index paths, flush success/retry/timeout/FLR cleanup, legacy and MSI interrupt scheduling, fatal interrupt rate limiting, RSS indirection programming, filter insert/replace/remove/get/list/clear behavior, RFS expiry when enabled, and filter restore after reset.
