<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/pnic.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/pnic.c

Purpose: Provides media negotiation and link monitoring for Lite-On LC82C168 PNIC chips used by the shared Tulip driver.

Important APIs and functions: `pnic_do_nway()` interprets the PNIC PHY status register at 0xB8, chooses `dev->if_port`, updates `tp->nwayset`, duplex, CSR12, CSR6, and restarts RX/TX when the mode changes. `pnic_lnk_change()` handles `TPLnkFail` and `TPLnkPass` interrupts by toggling CSR7 masks, restarting internal autonegotiation, or delegating to `tulip_check_duplex()` for external MII. `pnic_timer()` is the periodic media timer used from `tulip_tbl`.

Control flow: `tulip_core.c` assigns `pnic_lnk_change` for `HAS_PNICNWAY` and uses `pnic_timer` as the chip media timer. Link interrupts call `pnic_lnk_change()`. Timer ticks check whether interrupt masking has been temporarily cleared, then either validate MII duplex or inspect CSR12/CSR5/0xB8 for non-MII media fallback.

State and persistence: Uses `tp->csr6`, `tp->nwayset`, `tp->full_duplex`, `tp->medialock`, `dev->if_port`, `dev_trans_start()`, and `tp->timer`. No disk persistence. Hardware state is kept in CSR6, CSR7, CSR12, and PNIC register 0xB8.

Dependencies and integration: Depends on shared Tulip status bits, media capability flags, `tulip_restart_rxtx()`, `tulip_refill_rx()`, and `tulip_tbl[chip_id].valid_intrs`. It is tightly integrated with `interrupt.c`, which may leave CSR7 disabled on work overflow and rely on this timer path to refill RX and restore interrupts.

Risks: Link state transitions rely on raw magic constants and timing against `dev_trans_start()`. The timer disables and enables IRQ around RX refill when CSR7 is zero, which must remain consistent with interrupt handler assumptions. Internal PNIC autonegotiation must not run when external MII is selected.

Test signals: Validate 10/100 and half/full negotiation, remote fault recovery, medialock behavior, CSR7-zero overflow recovery, external MII duplex checking, and repeated link fail/pass interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/pnic.c -->
