# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rpm.c

## Purpose
`rpm.c` implements CN10K RPM/RPM2 MAC operations behind the common CGX/RPM `mac_ops` interface. It reads and writes RPM CSRs for LMAC enablement, pause/PFC flow control, PTP timestamp prepending, internal loopback, statistics, FEC counters, FIFO sizing, MAC reset, and X2P reset handling. The RVU CGX mailbox layer calls these operations without needing to know whether the physical MAC is older CGX, RPM, or RPM2.

## Important APIs, Types, and Functions
- `rpm_mac_ops` and `rpm2_mac_ops` populate the common `struct mac_ops` callback table with RPM-specific register offsets, interrupt registers, feature limits, statistic counts, and function pointers.
- `is_dev_rpm2()` distinguishes CN10KB RPM2 from RPM.
- `rpm_get_mac_ops()` selects the correct ops table.
- `rpm_get_nr_lmacs()` and `rpm2_get_nr_lmacs()` derive active LMAC count from LMAC bitmap CSRs.
- `rpm_lmac_tx_enable()`, `rpm_lmac_rx_tx_enable()`, and `rpm_enadis_rx()` control MAC Tx/Rx enable bits.
- `rpm_lmac_enadis_pause_frm()`, `rpm_lmac_pause_frm_config()`, `rpm_lmac_get_pause_frm_status()`, and `rpm_lmac_enadis_rx_pause_fwding()` implement 802.3x pause behavior.
- `rpm_lmac_pfc_config()`, `rpm_lmac_get_pfc_frm_cfg()`, and `rpm_cfg_pfc_quanta_thresh()` implement priority flow control class masks and quanta registers.
- `rpm_get_rx_stats()`, `rpm_get_tx_stats()`, `rpm_stats_reset()`, and `rpm_get_fec_stats()` read latched counter pages and reset statistics.
- `rpm_lmac_internal_loopback()` and `rpmusx_lmac_internal_loopback()` configure PCS loopback, rejecting SGMII/QSGMII LPC modes.
- `rpm_lmac_ptp_config()` enables RX timestamp prepending and one-step timestamp mode.
- `rpm_lmac_reset()` resets PFC-related CSRs and clears loopback on PF-requested FLR; `rpm_x2p_reset()` gates MAC-to-NIX path reset.

## Control Flow
`rvu_cgx_init()` obtains MAC private data through CGX helpers and calls `get_mac_ops()`, which can return the tables defined here. From then on, mailbox handlers in `rvu_cgx.c` route MAC requests through the table. For example, a CGX/RPM start request calls `mac_rx_tx_enable`, pause requests call `mac_enadis_pause_frm`, PTP RX enable calls `mac_enadis_ptp_config`, and stats requests call `mac_get_rx_stats`/`mac_get_tx_stats`.

Most helpers validate the LMAC through `is_lmac_valid()` and then perform direct read-modify-write sequences using `rpm_read()`/`rpm_write()`, which delegate to CGX MMIO accessors. Statistic and FEC paths acquire `rpm->lock` because reading a low counter latches a shared high register. Flow-control configuration is layered: PFC quanta helpers update per-class pause timers, RPM/RPM2 backpressure helpers update the correct generation-specific override register, and public pause/PFC helpers update MAC command config bits.

## State and Persistence Behavior
Driver state lives in the shared RPM/CGX private object (`rpm_t`): PCI device, lock, FIFO length, LMAC bitmap, max LMAC count, MAC ops pointer, and per-LMAC link metadata. Hardware state persists in RPM CSRs until reset: command config bits, pause/PFC class registers, stats counters, FEC capture state, PTP prepend and one-step mode, loopback bits, and X2P reset. The driver does not persist configuration outside hardware and in-memory link state.

## Dependencies and Integration Points
The file depends on `cgx.h` and `lmac_common.h` for `rpm_t`, `struct mac_ops`, LMAC validation, firmware-interface command helpers, link mode data, and generic CGX read/write access. It is integrated by `rvu_cgx.c` through `get_mac_ops()` and by mailbox handlers that expose MAC control to PF/VF drivers. PTP configuration integrates with NPC parser timestamp shifting and MCS configuration through callers in `rvu_cgx.c`.

## Risks and Edge Cases
- Many functions return `-ENODEV` on invalid LMAC, but some void helpers silently return; callers should not assume a hardware write occurred.
- `rpm_lmac_tx_enable()` returns the previous Tx-enabled state rather than a conventional zero/negative status, which is intentional for its caller but easy to misuse.
- Flow-control paths must prevent conflicting 802.3x pause and PFC modes; this file depends on `rvu_cgx.c` permission and conflict checks for some cases.
- Statistic and FEC high-half registers are shared and must remain protected by `rpm->lock`; adding unlocked reads risks mixed counter values.
- RPM2 has different global/per-LMAC backpressure and PFC registers; wrong ops selection would corrupt unrelated register space.
- FIFO partition logic depends on LMAC bitmap and high-performance LMAC fields; unusual three-LMAC and eight-LMAC RPM2 layouts need coverage.

## Test Signals
- Exercise all `mac_ops` callbacks on RPM and RPM2 hardware or MMIO mocks.
- Verify invalid LMAC handling for each public helper.
- Validate pause/PFC enable, disable, class mask, quanta, and conflict behavior from mailbox callers.
- Read RX/TX/FEC statistics under concurrent access and confirm high/low halves are consistent.
- Run PTP RX enable/disable tests that also verify NPC parser shift and one-step mode side effects through the caller path.
- Test FLR/reset paths for PFC CSR reset, loopback clearing, RX disable before X2P reset, and X2P reset release.
