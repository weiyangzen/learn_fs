# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_ptp.c

Purpose: Provides low-level Ethernet PTP hardware operations for QED. It enables/disables timestamping hardware, configures packet filters, reads RX/TX timestamps and the PHC counter, and adjusts clock frequency via NIG drift-counter registers.

Important APIs/types/functions: `qed_ptp_ops_pass` exports `cfg_filters`, `read_rx_ts`, `read_tx_ts`, `read_cc`, `adjfreq`, `enable`, and `disable`. `qed_ptcdev_to_resc()`, `qed_ptp_res_lock()`, and `qed_ptp_res_unlock()` map ports to MCP resource locks. Timestamp readers consume NIG host/tx timestamp buffer registers and clear valid bits. `qed_ptp_hw_cfg_filters()` maps `QED_PTP_FILTER_*` and TX mode into NIG rule masks. `qed_ptp_hw_adjfreq()` converts ppb into drift period/value/direction.

Control flow: Enable acquires a PTT, stores it in `p_hwfn->p_ptp_ptt`, acquires the per-port MCP lock or falls back to first-PF ownership for old firmware, resets RX/TX PTP rules, enables timestamping, enables PDA timestamp output, resets the free-running counter through chip-specific registers, disables drift, and clears stale timestamp buffers. Disable releases the MCP lock, resets rules, disables RX/TX PTP, releases the stored PTT, and clears the pointer. Filter configuration writes RX and TX masks and enables based on selected protocol family. Frequency adjustment searches 1..7 ns adjustment values for the best approximation and programs drift registers after reset.

State and persistence: The main persistent state is `p_hwfn->p_ptp_ptt`, held between enable and disable, plus hardware NIG timestamp/filter/drift registers and MCP resource-lock ownership.

Dependencies/integration: Depends on QED hardware register accessors, MCP resource locking, PTT management, chip-family helpers (`QED_IS_BB_B0`, `QED_IS_AH`), PTP enums from the Ethernet API, and numerous `NIG_REG_*` addresses from `qed_reg_addr.h`.

Risks: Holding a PTT across the enabled lifetime makes cleanup ordering important. Old MFW lock fallback grants ownership only to early PFs by `abs_pf_id`, so multi-PF behavior differs by firmware. `qed_ptp_hw_disable()` assumes `p_ptp_ptt` is valid. The ppb algorithm has special handling for 1 ppb and integer limits. Filter masks are magic constants and easy to regress.

Test signals: Enable/disable on supported and unsupported PFs, MFW lock grant/deny/unsupported paths, all RX filter modes with TX on/off, invalid filter rejection, RX/TX timestamp valid-bit handling and clear, PHC read monotonicity, positive/negative/zero/1 ppb adjustment, and chip-specific free-counter reset paths.
