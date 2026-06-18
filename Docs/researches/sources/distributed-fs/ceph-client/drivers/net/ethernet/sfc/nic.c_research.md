# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/nic.c

Purpose: this file provides generic NIC helpers for coherent DMA buffers, interrupt hookup/teardown, register dumping, and hardware statistics conversion.

Important APIs: `efx_nic_alloc_buffer()` and `efx_nic_free_buffer()` allocate/free coherent DMA; `efx_nic_event_present()`, `efx_nic_event_test_start()`, and `efx_nic_irq_test_start()` support self-tests; `efx_nic_init_interrupt()` requests MSI-X/MSI or legacy IRQs and optionally builds an RFS CPU rmap; `efx_nic_fini_interrupt()` frees them. `efx_nic_get_regs_len()` and `efx_nic_get_regs()` implement ethtool register dumps. `efx_nic_describe_stats()`, `efx_nic_copy_stats()`, `efx_nic_update_stats()`, and `efx_nic_fix_nodesc_drop_stat()` support ethtool statistics.

Control flow: interrupt setup branches on interrupt mode. MSI paths request an IRQ per channel and unwind partial success on failure; legacy requests a shared IRQ once. Stats copying uses firmware generation words around a memcpy to avoid torn DMA reads, retrying briefly then zeroing on failure. Register dumping walks revision-filtered register and table descriptors.

State and dependencies: state affected includes `efx->irqs_hooked`, `net_dev->rx_cpu_rmap`, channel IRQ registrations, `last_irq_cpu`, `event_test_cpu`, `stats_buffer`, and RX no-descriptor drop accumulators. Dependencies include PCI DMA APIs, Linux IRQ APIs, CPU rmap, SFC register access helpers, firmware stats layouts, and `struct efx_nic_type` interrupt callbacks.

Risks and tests: risks include IRQ unwind correctness, stale CPU rmap state, DMA generation races, register-table size mismatches, and stats leaking uninitialized data. Test signals include interrupt selftests, open/close under MSI-X/MSI/legacy modes, ethtool register dumps, stats under concurrent DMA updates, and error-injection for IRQ request and DMA allocation failures.
