# Research: subset-b-004693

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_macsec.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_macsec.c

Purpose: implements hardware MACsec support for selected Microsemi/Microchip VSC85xx PHYs, mainly VSC856X/VSC8582/VSC8584. It programs the PHY MACsec ingress and egress classifier/security-association machinery, installs Linux `macsec_ops`, handles SecY/SA lifecycle callbacks from the MACsec core, and services packet-number rollover interrupts.

Important APIs and functions:
- `vsc8584_macsec_init()` is the exported initialization entry used by `mscc_main.c`. It initializes the private flow list, clears `priv->secy`, attaches `phydev->macsec_ops`, and runs the hardware block initialization for supported PHY IDs.
- `vsc8584_macsec_phy_read()` and `vsc8584_macsec_phy_write()` are the low-level 32-bit accessors over the PHY MACsec CSR indirection page. They select `MSCC_PHY_PAGE_MACSEC`, program target/bank selection registers, poll the command bit, and restore the prior MDIO page.
- `__vsc8584_macsec_init()` initializes ingress/egress MACsec blocks, host/line MACs, flow-control buffer settings, and processor protocol mode. It must run with the MDIO lock held by its caller.
- The `vsc8584_macsec_ops` table maps kernel MACsec operations to this driver's handlers for device open/stop, SecY add/update/delete, RXSC/RXSA operations, and TXSA operations.
- `vsc8584_macsec_flow()`, `vsc8584_macsec_transformation()`, and flow enable/disable helpers are the core programming routines for SAM match entries, flow-control action words, and transformation records.
- `vsc8584_handle_macsec_interrupt()` detects egress PN rollover, disables the affected TX flow, and calls `macsec_pn_wrapped()`.

Control flow: initialization resets both MACsec banks, enables clocks, configures classification/VLAN parsing/default actions, configures MAC pause/FCS/preamble behavior, enables the flow-control buffer, and switches the processor to protocol mode 4. When a SecY is added, `priv->secy` is set, default unmatched handling is tightened when validation is enabled, and two default MKA bypass flows for `ETH_P_PAE` are installed. RXSA/TXSA additions allocate a hardware flow from the relevant ingress/egress bitmap, configure match selectors, write a transformation record with AES key material plus derived GHASH key, then enable the SAM entry if the SA is active. Updates disable the flow first, rewrite match/action state, and re-enable. Deletions disable and free flows. Device open/stop toggles all flows without deleting state.

State and persistence: all durable driver-side state is in `struct vsc8531_private`: one active `macsec_secy *`, a list of `struct macsec_flow`, and ingress/egress bitmaps with 16 entries each. Hardware state is programmed into PHY CSR banks and persists until reset or explicit reconfiguration. Transformation records contain live MACsec keys and PN/replay state in hardware; only `flow->has_transformation`, flow index, SA pointers, match flags, and action flags are retained in software. The code does not support multiple SecYs per PHY. PN update through `ctx->sa.update_pn` is rejected for both RX and TX updates.

Dependencies and integration points: depends on phylib, the kernel MACsec core (`<net/macsec.h>`), AES helpers (`aes_prepareenckey()`, `aes_encrypt()`), and register definitions in `mscc.h`, `mscc_mac.h`, `mscc_macsec.h`, and `mscc_fc_buffer.h`. It is reached from `vsc8584_config_init()` in `mscc_main.c`; MACsec interrupts are enabled through `vsc8584_config_macsec_intr()` and dispatched by `vsc8584_handle_interrupt()`. PTP integration is compile-time visible through `CONFIG_NETWORK_PHY_TIMESTAMPING`, because host MAC packet-interface config adds a MACsec bypass PTP stall-clock value when PHY timestamping is enabled.

Risks and edge cases:
- The low-level MACsec read/write helpers poll for command completion but do not return an error on timeout; reads still return whatever data registers contain and writes silently proceed. Fault injection around stuck CSR commands would be valuable.
- `vsc8584_handle_macsec_interrupt()` assumes `priv->secy` is valid when a MACsec rollover interrupt arrives. Interrupt routing before `add_secy` or after `del_secy` could dereference a null SecY if hardware still reports rollover.
- Transformation record writes cast `u8 *` key and derived hkey buffers to `u32 *`, so byte order and alignment assumptions matter. This mirrors hardware expectations but should be tested on strict-alignment architectures or audited against kernel unaligned-access rules.
- Flow lookup matches only association number and bank, not SCI for RX; if multiple RXSCs reuse association numbers, deletion/update paths can target the wrong flow.
- Only 16 ingress and 16 egress flows are available; exhaustion returns `-ENOMEM` and should be visible to MACsec configuration tests.

Test signals: exercise `ip macsec` add/update/delete for SecY, RXSC, RXSA, and TXSA; verify MKA frames bypass encryption on ingress and egress; validate strict/check/disabled modes and unmatched frame behavior; verify active/inactive SA enablement; drive PN rollover to ensure TXSA is disabled and the MACsec core is notified; run with `CONFIG_MACSEC` both enabled and disabled to validate stubs in `mscc.h`; inspect ethtool counters and packet forwarding before and after PHY reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_macsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_macsec.h -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_macsec.h

Purpose: defines the MACsec hardware programming model used by `mscc_macsec.c`: security-association flow limits, transformation control bits, destination ports, drop/action modes, validation modes, CSR target banks, the `struct macsec_flow` software representation, and register/bitfield macros for the MACsec classifier, flow controller, context records, counters, interrupts, and MTU checks.

Important APIs/types:
- `MSCC_MS_MAX_FLOWS` caps each ingress and egress bank at 16 SAM entries.
- `enum macsec_bank` maps abstract block names (`MACSEC_INGR`, `MACSEC_EGR`, `HOST_MAC`, `LINE_MAC`, `FC_BUFFER`, processor banks) to the target IDs consumed by the CSR accessors.
- `struct macsec_flow` is the key software object for one hardware flow. It stores the list node, bank, hardware index, association number, priority, ingress or egress SA pointer, match flags for SCI/tagged/untagged/EtherType, optional EtherType, action flags, destination port, and whether transformation context has been installed.
- The `CONTROL_*` and `CTRYPTO_ALG_*`/`AUTH_ALG_*` macros encode transformation record word 0 for AES-CTR plus AES-GHASH MACsec operation.
- Register macros such as `MSCC_MS_SAM_MISC_MATCH(x)`, `MSCC_MS_SAM_MASK(x)`, `MSCC_MS_SAM_FLOW_CTRL(x)`, and `MSCC_MS_XFORM_REC(x, y)` provide indexed access to classifier and transformation tables.

Control flow enabled by this header: callers build a SAM match word from `MSCC_MS_SAM_MISC_MATCH_*`, a mask word from `MSCC_MS_SAM_MASK_*`, and an action word from `MSCC_MS_SAM_FLOW_CTRL_*`; then they activate entries through `MSCC_MS_SAM_ENTRY_SET1` or clear them through `MSCC_MS_SAM_ENTRY_CLEAR1`. Transformation records are 32-word-spaced with `MSCC_MS_XFORM_REC()`, allowing the C file to serialize control, context ID, encryption key, derived auth key, PN/replay window, SCI, and zero fill. Default non-match handling is configured with `MSCC_MS_SAM_NM_FLOW_NCP` and `MSCC_MS_SAM_NM_FLOW_CP`.

State and persistence: this header does not allocate state itself, but its `struct macsec_flow` layout defines the in-memory state kept under `vsc8531_private.macsec_flows`. The hardware register defines describe state that persists in the PHY until reset or explicit writes: enabled clocks, SAM entries, flow-control words, counter mode, MTU limits, context records, and interrupt masks/status.

Dependencies and integration points: includes `<net/macsec.h>` for MACsec SA pointer types. It is included by `mscc_macsec.c` and indirectly tied to `mscc.h`, whose private structure stores flow lists and SecY state behind `CONFIG_MACSEC`. Many macros are paired with register-bank access logic in `vsc8584_macsec_phy_read/write()`.

Risks and edge cases:
- Bit definitions overlap intentionally across ingress and egress interpretations, for example `MSCC_MS_SAM_FLOW_CTRL_PROTECT_FRAME` and `MSCC_MS_SAM_FLOW_CTRL_REPLAY_PROTECT` both use bit 16. Callers must use them only with the correct bank.
- The typo-style names `CTRYPTO_ALG_*` and `AUTH_ALG_AES_GHAS` are part of the local API; renaming requires coordinated code changes.
- Wide shift macros accept unbounded arguments, so callers must validate values before shifting into hardware fields.
- Register constants are dense and hardware-specific; a single incorrect address affects security behavior more than ordinary link setup.

Test signals: compile coverage under `CONFIG_MACSEC=y`; static analysis for field-width overflow; MACsec packet tests for each flow action/validation mode; interrupt tests for `MACSEC_INTR_CTRL_STATUS_ROLLOVER`; and cross-check against the VSC8584 MACsec register map for table offsets and bit positions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_macsec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_main.c

Purpose: this is the main Microsemi/Microchip VSC85xx PHY driver. It registers phylib drivers for multiple VSC850x/VSC85xx parts, implements common copper PHY behavior, package-level initialization for multi-port devices, firmware patching for embedded 8051 microcontrollers, host SerDes setup, LED and ethtool stats support, Wake-on-LAN, MDIX/downshift tunables, interrupt handling, and integration with the MACsec/PTP helper files.

Important APIs and functions:
- `vsc85xx_probe_common()` allocates `struct vsc8531_private`, configures package joining, stats, LEDs, optional PTP probing, and DT/default LED modes.
- `vsc85xx_config_init()`, `vsc8584_config_init()`, and `vsc8514_config_init()` are the main per-family initialization paths.
- `phy_base_read/write()`, `vsc85xx_csr_read/write()`, `vsc8584_cmd()`, `phy_update_mcb_s6g()`, and `phy_commit_mcb_s6g()` are exported helpers used by PTP, MACsec, and SerDes code.
- `vsc8584_config_pre_init()`, `vsc8574_config_pre_init()`, and `vsc8514_config_pre_init()` apply package-wide analog tuning, firmware patching, microcontroller reset/deassert sequences, and SerDes preparation.
- `vsc8584_handle_interrupt()` dispatches timestamp FIFO interrupts, MACsec rollover interrupts, and link-change events for PTP/MACsec-capable packages.
- The `vsc85xx_driver[]` table binds PHY IDs to callbacks, capabilities, probe routines, and optional remove/link-change hooks.

Control flow: probe allocates private state, optionally computes edge-rate magic from DT, discovers package/base addresses, joins a phylib package, initializes PTP package-wide state once, then registers per-PHY PTP timestamper state when supported. During config init, simple single-PHY devices run RGMII delay setup, MAC interface selection, edge-rate programming, device-specific TR/EEE sequences, soft reset, and LED programming. Multi-port devices take the MDIO bus lock and execute package-wide pre-init only once via `phy_package_init_once()`, including broadcast writes, firmware CRC validation and patching, microcontroller reset control, LCPLL reset, host SerDes mode selection, and COMA release. After unlocking, VSC8584-class devices initialize MACsec, initialize PTP, select copper/SGMII operation, apply RGMII delay programming, soft reset, and LED modes.

State and persistence: `struct vsc8531_private` stores LED modes, stats accumulators, package address, PTP/MACsec pointers, locks, RX timestamp queue, and per-PHY base timestamp address. `struct vsc85xx_shared_private` stores the package-shared GPIO lock. Hardware state includes selected MDIO page, firmware in patch RAM, microcontroller reset/patch vector state, host SerDes mode, CSR/MCB register contents, interrupt masks, LED behavior, WOL MAC/password registers, RGMII delays, and PHY counters. Stats are read-and-accumulated because the hardware counters are narrow and likely clear or roll; the driver returns cumulative software totals.

Dependencies and integration points: integrates with phylib (`struct phy_driver`, page read/write callbacks, package helpers, interrupts, tunables, in-band caps), firmware loader (`request_firmware()` for VSC8584/VSC8574 firmware blobs), OF/DT properties for edge rate and legacy LED modes, Linux LED netdev triggers, ethtool stats/WOL APIs, and the local helper modules `mscc_macsec.c`, `mscc_ptp.c`, and `mscc_serdes.c`. Several low-level functions require the MDIO bus lock and emit diagnostics if called unlocked.

Risks and edge cases:
- Package initialization touches shared registers and uses broadcast writes; incorrect base address detection can affect every PHY in a package.
- Firmware patching failure is sometimes downgraded to a warning, leaving the device in a "non-optimal" state that still probes.
- `vsc85xx_csr_read()` returns `0xffffffff` on timeout, which can be indistinguishable from a valid all-ones register value to careless callers.
- Interrupt setup calls MACsec and PTP interrupt configuration unconditionally, relying on compile-time stubs for disabled features.
- LED DT handling diverges depending on a child `leds` node: when present, legacy properties are ignored and defaults are forced so LED class devices can own policy.
- Some initialization paths are highly order-sensitive around microcontroller reset, patch vectors, and SerDes calibration.

Test signals: boot/probe each supported PHY ID and interface mode; verify package init runs once under concurrent PHY probing; test firmware absent, bad CRC, and successful patch flows; validate SGMII/QSGMII/RGMII interface selection; exercise interrupts with link, MACsec, and timestamp sources; confirm WOL programming and wake; inspect ethtool stats accumulation; test LED class hardware-control get/set and brightness; verify suspend/resume and remove unregister PTP resources on PTP-capable drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_ptp.c

Purpose: implements IEEE 1588/PTP hardware timestamping and PHC support for VSC8584-family PHYs. It configures the PHY's shared 1588 processor, ingress/egress analyzer engines, timestamp FIFO, local time counter, latency compensation, and kernel `mii_timestamper`/`ptp_clock_info` integration.

Important APIs and functions:
- `vsc8584_ptp_probe_once()` initializes package-shared GPIO locking; `vsc8584_ptp_probe()` allocates per-PHY PTP state, queues, GPIO handle, mii timestamper hooks, and registers the PHC.
- `vsc8584_ptp_init()` runs hardware initialization for supported PHY IDs through `__vsc8584_init_ptp()`.
- `vsc8584_ptp_deinit()` unregisters the PHC and purges RX/TX queues.
- `vsc8584_config_ts_intr()` enables timestamp FIFO interrupts; `vsc8584_handle_ts_interrupt()` acknowledges and dispatches FIFO-add and FIFO-overflow events.
- `vsc85xx_hwtstamp_set/get()`, `vsc85xx_txtstamp()`, `vsc85xx_rxtstamp()`, and `vsc85xx_ts_info()` are the kernel timestamping interface.
- `vsc85xx_adjfine()`, `vsc85xx_adjtime()`, `vsc85xx_gettime()`, and `vsc85xx_settime()` implement PHC operations.

Control flow: timestamp CSR access goes through `vsc85xx_ts_read_csr()` and `vsc85xx_ts_write_csr()`, which select the base PHY of a two-port 1588 processor and choose hardware block IDs for ingress, egress, or processor based on whether the current PHY is the base port. Probe sets `phydev->default_timestamp`, installs mii timestamp callbacks, and registers a PTP clock. Hardware init configures the 1588 input clock once for the base pair, disables predictors, selects the 250 MHz internal LTC clock, configures LTC sequence/error, delay FIFO depth, accuracy calibration, rewriter behavior, FIFO signature layout, interface control, latency compensation, analyzer split-flow mode, and default comparators for Ethernet/IP/PTP. HWTSTAMP set disables predictors, bypasses unused ingress/egress paths, resets FIFO, configures L2 or IPv4/UDP comparator chains, enables selected PTP flows, then re-enables predictors.

TX timestamping: `txtstamp` queues outgoing SKBs unless timestamping is disabled or one-step Sync should be rewritten in hardware. Egress FIFO interrupts call `vsc85xx_get_tx_ts()`, which reads FIFO entries, computes a 16-byte signature from the PTP sequence ID/domain/message type/destination MAC, matches queued SKBs, and completes hardware TX timestamps. FIFO overflow purges queued TX SKBs and resets the FIFO.

RX timestamping: ingress hardware writes a nanosecond value into the PTP reserved field. `rxtstamp` extracts the PTP header for L2 or IPv4/UDP mode, stores the nanoseconds in the SKB control block, queues the SKB, and schedules PHC auxiliary work. `vsc85xx_do_aux_work()` snapshots current PHC time, combines seconds with the embedded nanoseconds, handles second wrap, writes `skb_hwtstamps`, and reinjects the SKB through `netif_rx()`.

State and persistence: `struct vsc85xx_ptp` stores the registered PHC, the PHY pointer, TX queue, current TX type/RX filter, and configured flag. `struct vsc8531_private` stores `mii_timestamper`, `phc_lock`, `ts_lock`, `rx_skbs_list`, `load_save` GPIO, `input_clk_init`, and timestamp base address. The shared package state is the GPIO lock. Hardware retains LTC time, comparator configuration, FIFO contents, interrupt masks/status, analyzer mode, latency values, and predictor settings.

Dependencies and integration points: depends on phylib timestamping, `ptp_clock_kernel`, `ptp_classify`, GPIO descriptors, SKB queues, and register definitions from `mscc_ptp.h` and `mscc.h`. `mscc_main.c` calls probe/init/deinit/config interrupt handlers and link-change latency updates. MACsec affects latency tables and delay FIFO depth at compile time through `CONFIG_MACSEC`.

Risks and edge cases:
- CSR read/write polling loops count a small fixed number of BIU polls and do not propagate explicit timeout errors.
- RX timestamp reconstruction only carries nanoseconds in the packet and borrows seconds from current PHC time, so delayed processing near a second boundary is sensitive to the wrap heuristic.
- TX FIFO signature matching can discard SKBs whose PTP header cannot be parsed and can leave unmatched SKBs queued until later FIFO entries.
- Only PTP v2 L2 event and IPv4/UDP L4 event filters are supported; IPv6 and non-event filters return `-ERANGE`.
- `vsc8584_ptp_deinit()` assumes `vsc8531->ptp` exists on devices that install the remove hook.
- Shared load/save GPIO sequencing relies on every user honoring the package `gpio_lock`.

Test signals: use `ethtool -T`, `hwstamp_ctl`, `phc2sys`, and `ptp4l` in L2 and IPv4/UDP modes; validate one-step Sync rewriting and two-step FIFO completion; force FIFO overflow and verify queue purge; test link speed changes and latency reload; verify PHC get/set/adjfine/adjtime; test with and without MACsec compiled in; inspect IRQ handling for FIFO add with global PHY interrupt status equal to zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_ptp.h

Purpose: defines the VSC85xx 1588/PTP register map, analyzer comparator fields, local time counter fields, FIFO formats, PTP command encodings, and software structures consumed by `mscc_ptp.c`.

Important APIs/types:
- BIU indirection macros (`MSCC_PHY_TS_BIU_ADDR_CNTL`, `BIU_ADDR_EXE`, `BIU_BLK_ID()`, `BIU_CSR_ADDR()`) define how the C file reads and writes 1588 CSR blocks through the base PHY.
- Processor registers describe interface control, analyzer mode, LTC load/save/adjust, predictor enable bits, latency registers, delay FIFO depth, timestamp FIFO control, rewriter controls, serial TOD behavior, and accuracy calibration status.
- Analyzer register groups define Ethernet, IP, MPLS, OAM/PTP, and PTP flow enable/match/mask/action registers. `COMP_MAX_FLOWS` is 8 for generic comparators; `PTP_COMP_MAX_FLOWS` is 6 for PTP flows.
- `enum ptp_cmd` maps hardware rewrite/save commands such as `PTP_WRITE_1588`, `PTP_WRITE_NS`, and the software sentinel `PTP_SAVE_IN_TS_FIFO`.
- `struct vsc85xx_ptphdr` is a packed PTP header view used to parse or update packet fields.
- `struct vsc85xx_ts_fifo` models one egress timestamp FIFO entry as nanoseconds, 48-bit seconds, and a 16-byte signature.
- `struct vsc85xx_ptp` stores per-PHY PHC/timestamper runtime state.

Control flow enabled by this header: `mscc_ptp.c` uses the macros to build comparator chains from Ethernet to PTP directly for L2 (`ETH_P_1588`) or through IPv4/UDP to PTP for L4 event traffic. Flow action macros encode whether ingress writes nanoseconds into packet reserved bytes, whether egress rewrites one-step timestamps, or whether egress saves a timestamp/signature into the FIFO. LTC macros encode PHC load/save and frequency/offset adjustment. FIFO macros let the interrupt handler detect empty/overflow/level conditions and reset the FIFO.

State and persistence: the header declares both software queue/clock state (`struct vsc85xx_ptp`) and packed wire/hardware views. Hardware state described here persists in the 1588 processor until reset or reconfiguration. FIFO entries are consumed destructively by reading the last FIFO word. The software `configured` bit gates RX/TX timestamp callbacks after hwtstamp configuration.

Dependencies and integration points: requires phylib/PHY declarations, PTP clock types, SKB queue types, and kernel bit macros supplied by included users. It is tightly coupled to `mscc_ptp.c`; `mscc.h` forward-declares `struct vsc85xx_ptp` usage in private driver state and exposes PTP entry points conditionally under `CONFIG_NETWORK_PHY_TIMESTAMPING`.

Risks and edge cases:
- Many macros use literal bit masks instead of `FIELD_PREP`, so invalid values can spill into adjacent fields if callers do not constrain inputs.
- The packed bitfield `u64 secs:48` in `struct vsc85xx_ts_fifo` is compiler-layout-sensitive; the C file fills it byte by byte, so ABI assumptions should be validated on target architectures.
- PTP header parsing structures only model the fields needed by this implementation; unsupported PTP transports or IPv6 are outside this header's flow model.
- Delay constants such as `PTP_INGR_DELAY_FIFO_DEPTH_MACSEC` and `STALL_EGR_LATENCY()` encode hardware timing assumptions that must match MACsec/PTP pipeline changes.

Test signals: build with `CONFIG_NETWORK_PHY_TIMESTAMPING`; run sparse/packed-structure checks; validate CSR addresses against datasheet; exercise L2 and L4 hwtstamp modes; verify egress FIFO entry byte layout against actual hardware FIFO dumps; test PHC adjustment fields over positive and negative offsets/frequency corrections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_serdes.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_serdes.c

Purpose: implements the 6G SerDes/LCPLL calibration and configuration sequence for VSC85xx package PHYs. It provides the exported `vsc85xx_sd6g_config_v2()` routine used by `mscc_main.c` when configuring host SerDes in SGMII or QSGMII modes.

Important APIs and functions:
- `vsc85xx_sd6g_config_v2()` is the single external entry point. It orchestrates PLL detune/tune, RCPLL reset, input buffer calibration, FoJi frequency-offset calibration, mission-mode restore, MAC mode selection, and final PLL/lane reset release.
- `pll5g_detune()` and `pll5g_tune()` modify `PHY_S6G_PLL5G_CFG2` gain control around calibration.
- Helper writers such as `vsc85xx_sd6g_pll_cfg_wr()`, `vsc85xx_sd6g_common_cfg_wr()`, `vsc85xx_sd6g_des_cfg_wr()`, `vsc85xx_sd6g_ib_cfg*_wr()`, `vsc85xx_sd6g_misc_cfg_wr()`, `vsc85xx_sd6g_gp_cfg_wr()`, and DFT/PLL5G writers encode specific CSR writes.
- It uses `phy_update_mcb_s6g()` and `phy_commit_mcb_s6g()` from `mscc_main.c` to transfer CSR shadow state to/from MCB hardware.

Control flow: the sequence first selects the standard page and detunes/unlocks LCPLL. It resets RCPLL, commits base common/DES/IB configuration, starts the PLL FSM, and polls `PHY_S6G_PLL_STATUS` until calibration completes. It then releases digital reset with TX disabled, applies FoJi RX frequency offset, prepares and starts input-buffer calibration, toggles GP configuration for the required calibration cycles, polls `PHY_S6G_IB_STATUS0`, restores mission-mode IB settings, reenables TX, disables FoJi/DFT, and retunes/relocks LCPLL. Final configuration reads `MSCC_PHY_MAC_CFG_FASTLINK` to choose QSGMII or SGMII parameters, invokes the 8051 processor command for the selected MAC mode, updates LCPLL/S6G MCB state, writes final DES/IB/common settings, restarts the PLL FSM, waits for PLL completion again, releases lane reset, and commits.

State and persistence: no driver-private memory is retained by this file. Persistent state is entirely in PHY CSR/MCB hardware: PLL FSM config, common lane config, DES config, input-buffer calibration values, DFT/FoJi settings, GP toggles, MAC mode, and lane reset state. The function is intended to run during package/host-SerDes initialization with the MDIO bus already controlled by the caller.

Dependencies and integration points: includes `mscc_serdes.h` and `mscc.h`. It relies on `vsc85xx_csr_read/write()`, `phy_base_read/write()`, `phy_update_mcb_s6g()`, `phy_commit_mcb_s6g()`, and `vsc8584_cmd()` from `mscc_main.c`. It is called from `vsc8584_config_host_serdes()` and `vsc8514_config_host_serdes()`.

Risks and edge cases:
- This is a long, order-sensitive hardware recipe with many magic values from PHY characterization; small reordering or failed intermediate writes can leave the SerDes unusable.
- Poll loops use `PROC_CMD_NCOMPLETED_TIMEOUT_MS`; timeouts return `-ETIMEDOUT`, but prior hardware state is not rolled back.
- If `MSCC_PHY_MAC_CFG_FASTLINK` does not decode as QSGMII or SGMII, an error is logged but execution continues into later MCB update/configuration using the previous default variables, which may hide invalid interface setup.
- Helper `vsc85xx_sd6g_common_cfg_wr()` takes `pwd_tx` but does not encode it in the written value, which may be intentional or a stale parameter.
- The function assumes suitable locking context and package state from callers.

Test signals: boot VSC8514/VSC8584-class devices in SGMII and QSGMII modes; observe PLL and IB calibration completion; inject CSR/MCB write failures and timeouts; verify invalid MAC mode behavior; measure link bring-up and error counters after calibration; compare final register dumps to vendor reference sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_serdes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_serdes.h -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_serdes.h

Purpose: provides the small public interface and selected register offsets/bit positions for the VSC85xx 6G SerDes configuration helper.

Important APIs/types:
- `vsc85xx_sd6g_config_v2(struct phy_device *phydev)` is declared as the only callable API from this header.
- `PHY_S6G_PLL5G_CFG2_GAIN_MASK` and `PHY_S6G_PLL5G_CFG2_ENA_GAIN` support LCPLL detune/tune logic.
- DES bit-position macros and SerDes CSR offsets (`PHY_S6G_DES_CFG`, `PHY_S6G_IB_CFG0..4`, `PHY_S6G_GP_CFG`, `PHY_S6G_DFT_CFG0`, `PHY_S6G_IB_DFT_CFG2`) are used by `mscc_serdes.c` helper writers.

Control flow enabled by this header: `mscc_main.c` includes it to call the SerDes calibration function during host SerDes setup. `mscc_serdes.c` uses the register constants to construct CSR writes before committing them through the MCB helper API.

State and persistence: no software state is declared. All represented state is PHY hardware state written during SerDes calibration and retained until reset/reconfiguration.

Dependencies and integration points: depends on `struct phy_device` being visible to the including C file through `<linux/phy.h>`. The comment guard closes with `_MSCC_PHY_SERDES_H_` while the opening guard is `_MSCC_SERDES_PHY_H_`; this is only a comment mismatch, not a preprocessor issue.

Risks and edge cases:
- Only a subset of register constants is local to this header; other SerDes/MCB constants come from `mscc.h`, so changes must be coordinated across both headers.
- Because the header exposes only one high-level function, any additional SerDes mode would require expanding the API or adding mode selection inside `vsc85xx_sd6g_config_v2()`.

Test signals: compile coverage for all files including this header; run SGMII/QSGMII initialization paths; verify no include-order issue around `struct phy_device`; cross-check register offsets against the datasheet and `mscc.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_serdes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mxl-86110.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/mxl-86110.c

Purpose: implements the MaxLinear MXL86110/MXL86111 Gigabit Ethernet PHY driver. It provides extended-register access, Wake-on-LAN, LED hardware-control support, SyncE clock output defaults, RGMII delay configuration, MXL86111 bootstrap validation/page selection, fiber/SGMII in-band autonegotiation control, and phylib driver registration for both PHY IDs.

Important APIs and functions:
- `__mxl86110_read/write/modify_extended_reg()` and locked wrappers implement the two-step extended-register access through standard registers 0x1e/0x1f.
- `mxl86110_get_wol()` and `mxl86110_set_wol()` expose ethtool WOL magic-packet support and program the destination MAC plus WOL interrupt enable.
- LED callbacks `mxl86110_led_hw_is_supported()`, `mxl86110_led_hw_control_get/set()`, and `mxl86110_led_brightness_set()` implement LED class hardware triggers and forced brightness for up to three LEDs.
- `mxl86110_config_init()` configures SyncE clock output, RGMII delay, activity blinking, and broadcast settings for MXL86110.
- `mxl86111_probe()` validates supported bootstrap modes and selects UTP register space.
- `mxl86111_config_init()` applies SyncE, fiber speed or RGMII timing, PL P1 1.8 V tuning, LED blink, and broadcast settings.
- `mxl86111_config_inband()` toggles fiber-space autonegotiation and link timer auto-sensing; `mxl86111_inband_caps()` advertises in-band support for 100BASE-X, 1000BASE-X, and SGMII.

Control flow: extended-register helpers either assume the MDIO bus lock is already held or acquire it in wrappers. MXL86110 config init locks the bus, writes default SyncE clock output, configures RGMII delays based on `phydev->interface`, enables LED activity blink on all LEDs, disables broadcast EPA0, then unlocks. MXL86111 probe reads the chip mode from `COM_EXT_CHIP_CFG`, accepts UTP-to-SGMII and UTP-to-RGMII modes, marks `phydev->port = PORT_TP`, and forces UTP register page. MXL86111 config init shares common SyncE/LED/broadcast work, but chooses fiber speed for 100BASE-X/1000BASE-X/SGMII or RGMII delays for other interfaces. In-band config first modifies the fiber-space BMCR AN enable bit, then writes extended autosen/reset behavior and power-cycles forced-fiber mode when enabling in-band autoneg.

State and persistence: this driver does not allocate private runtime state. Persistent state is in PHY registers: selected extended register space, SyncE output source/enable, RGMII delay values, RXDLY override, WOL MAC and enable bits, LED mode/manual-force bits, broadcast behavior, fiber speed selection, and in-band autoneg bits. WOL uses the attached netdev MAC address at set time.

Dependencies and integration points: integrates with phylib via `struct phy_driver`, standard genphy suspend/resume/soft-reset helpers, LED hardware trigger APIs, ethtool WOL, device-tree/PHY interface modes, and paged phylib access for MXL86111 fiber/UTP spaces. It uses kernel bitfield helpers (`FIELD_PREP`, `FIELD_GET`) for selected register fields.

Risks and edge cases:
- `mxl86111_config_inband()` jumps to `out` and unlocks the MDIO bus if the initial `phy_modify_paged()` fails before the bus is locked. That error path appears to call `phy_unlock_mdio_bus()` without a matching lock.
- In `mxl86111_config_init()` default/RGMII path, `mxl86110_config_rgmii_delay()` already writes delays and returns 0 on success, then a second `__mxl86110_modify_extended_reg(..., set=ret)` can clear the RGMII delay fields. This looks like a likely logic bug.
- `mxl86111_probe()` rejects bootstrap modes other than UTP-to-SGMII and UTP-to-RGMII, so supported hardware wired for fiber/auto modes will not bind here.
- WOL setup requires `phydev->attached_dev`; enabling WOL before netdev attachment returns `-ENODEV`.
- LED control get ORs into `*rules` without clearing it first; callers normally provide zeroed storage, but stale bits would survive otherwise.
- Extended register access is not based on phylib `read_page/write_page` except for the MXL86111 page callbacks, so mixed locked/unlocked use must be audited carefully.

Test signals: probe both PHY IDs and supported bootstrap modes; test MXL86111 unsupported bootstrap rejection; validate RGMII delay registers after config for RGMII/RGMII_ID/RGMII_RXID/RGMII_TXID; exercise WOL enable/disable and magic wake; use LED class hardware-control get/set for all trigger bits; test in-band enable/disable on fiber/SGMII and failure injection on the first `phy_modify_paged()` path; verify SyncE output register contents; test suspend/resume and soft reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/mxl-86110.c -->
