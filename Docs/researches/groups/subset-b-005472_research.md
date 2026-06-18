# subset-b-005472 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-qcom.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-qcom.c

## Purpose
`ufs-qcom.c` is the Qualcomm platform variant driver for the Linux UFS host controller core. It binds the generic `ufshcd` engine to Qualcomm controller registers, PHY sequencing, reset wiring, interconnect bandwidth voting, inline crypto through Qualcomm ICE, MCQ/ESI support, power management, clock scaling, test-bus diagnostics, and high-speed link tuning.

## Important APIs, Types, And Functions
The exported platform entry points are the `platform_driver` named `ufshcd-qcom`, the `ufs_qcom_probe()`/`ufs_qcom_remove()` pair, and two variant operation tables: `ufs_hba_qcom_vops` for normal platform-controlled PHY/power sequencing and `ufs_hba_qcom_sa8255p_vops` for firmware-managed systems. Core callbacks include `ufs_qcom_init()`, `ufs_qcom_exit()`, `ufs_qcom_hce_enable_notify()`, `ufs_qcom_link_startup_notify()`, `ufs_qcom_pwr_change_notify()`, `ufs_qcom_setup_clocks()`, suspend/resume callbacks, `ufs_qcom_device_reset()`, `ufs_qcom_clk_scale_notify()`, MCQ callbacks, and TX equalization/FOM callbacks.

Inline encryption is wired through `ufs_qcom_ice_init()` and `ufs_qcom_crypto_ops`, which adapt blk-crypto operations to `qcom_ice_*()` key programming, eviction, wrapped-key import/generation/preparation, and software-secret derivation. MCQ support uses `ufs_qcom_mcq_config_resource()`, `ufs_qcom_op_runtime_config()`, `ufs_qcom_get_outstanding_cqs()`, and `ufs_qcom_config_esi()`. Link diagnostics use `ufs_qcom_dump_dbg_regs()`, `ufs_qcom_dump_testbus()`, and `ufs_qcom_testbus_config()`.

## Control Flow And State
Probe selects a variant ops table from OF/ACPI match data and calls `ufshcd_pltfrm_init()`. During `ufshcd` initialization, `ufs_qcom_init()` allocates `struct ufs_qcom_host`, binds it with `ufshcd_set_variant()`, obtains optional reset, PHY, lane clocks, reset GPIO, interconnect paths, controller revision, ICE, and test-bus defaults, then advertises UFSHCD capabilities and quirks. The HCE PRE path resets the controller and powers/calibrates the PHY, then enables lane clocks; POST verifies Hibern8, enables controller/UniPro clock gating, enables ICE, and configures ICE allocator registers.

Power-mode negotiation delegates to `ufshcd_negotiate_pwr_params()` with Qualcomm host limits. PRE power-change may enable the device reference clock, configure adaptation for v4+ hardware, tune TX equalizer for Samsung quirks, and update `phy_gear` during initial max-gear negotiation. POST caches `host->dev_req_params`, updates interconnect bandwidth from the negotiated gear/lane/rate table, and disables the device reference clock when leaving HS mode. Clock scaling forces Hibern8 around timer/core-clock DME reprogramming and updates ICC votes after scaling.

Persistent runtime state lives in `struct ufs_qcom_host`: PHY pointer, lane-clock array and enable flag, ICE handle, controller revision, device reset GPIO, cached power parameters, host parameters, selected PHY gear, ESI enabled flag, saved TX EQ setting, interconnect handles, and test-bus selection. No disk persistence exists; all state is reconstructed at probe and revalidated across PM callbacks.

## Dependencies And Integration Points
This file depends on the UFS core (`ufshcd`, UniPro attributes, quirks, MCQ helpers), the platform glue in `ufshcd-pltfrm.c`, Linux PHY, reset, GPIO, interconnect, PM OPP/devfreq, platform MSI, blk-crypto, and Qualcomm ICE. OF match data differentiates generic Qualcomm, SM8550/SM8650, and SA8255P behavior. ACPI match `"QCOM24A5"` supports non-DT systems. Device quirks are fixed up for SK Hynix, WDC, and Samsung devices.

## Risks And Edge Cases
Most failures are timing-sensitive hardware sequencing failures: Hibern8 polling timeout, unsupported core clock frequencies, incorrect OPP index-to-clock mapping, missing named resources, ICE capability mismatch, platform MSI allocation failures, and device reset timing. `ufs_qcom_fw_managed_device_reset()` uses a static `is_boot`, which is simple but global to the driver instance model. MCQ/ESI paths assume Qualcomm-specific queue offsets and vendor registers. EOM/FOM and TX equalization are gated to specific v7 hardware because they directly manipulate high-speed M-PHY attributes.

## Test Signals
Useful coverage includes boot/probe on DT and ACPI platforms, missing optional reset GPIO and missing optional ICE, HCE PRE/POST ordering, suspend/resume with active, Hibern8, and off links, device reset pulse tests, OPP clock scaling at every supported UniPro frequency, ICC bandwidth votes for PWM/HS gear and lane combinations, MCQ queue operation and ESI interrupt delivery/fallback, crypto keyslot programming and eviction, debug dump paths in task and atomic contexts, and HS-G6 TX equalization/FOM tuning on supported v7 controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-qcom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-qcom.h -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-qcom.h

## Purpose
`ufs-qcom.h` is the private interface and register map for the Qualcomm UFS host variant. It defines vendor register offsets, bit masks, UniPro vendor attributes, controller revision helpers, reset helpers, MCQ address layout, ICE allocator constants, EOM/FOM scan coordinates, and the Qualcomm host-private data structures consumed by `ufs-qcom.c`.

## Important APIs, Types, And Macros
Important data types are `struct ufs_qcom_host`, `struct ufs_qcom_drvdata`, `struct ufs_hw_version`, `struct ufs_qcom_testbus`, and `struct ufs_eom_coord`. `ufs_qcom_host` carries the per-controller runtime state: PHY, `ufs_hba`, negotiated device parameters, lane clocks, interconnect paths, ICE handle, capabilities, device reference-clock MMIO and mask, hardware version, reset controls, device reset GPIO, host parameters, selected PHY gear, ESI state, and saved TX EQ settings.

The header exposes inline helpers `ufs_qcom_get_controller_revision()`, `ufs_qcom_assert_reset()`, `ufs_qcom_deassert_reset()`, and `ufs_qcom_get_debug_reg_offset()`, plus the non-static declaration `ufs_qcom_testbus_config()`. Register/mask definitions cover `REG_UFS_*`, debug windows, Hibern8 counters, MCQ layout, ICE configuration, clock-cycle attributes, and QCOM-specific quirks.

## Control Flow And State
The header itself has no execution path, but it shapes the driver flow. Controller revision is read from `REG_UFS_HW_VERSION` and split into major/minor/step. Reset helpers set or clear `UFS_PHY_SOFT_RESET` and perform dummy reads for posted-write ordering. Debug register offset selection depends on controller major version, mapping older 2.x controllers to a different vendor register window.

The EOM coordinate table `sw_rx_fom_eom_coords_g6` is static constant state used by the software RX FOM scan for HS-G6. ICE allocator constants describe how AES cores are shared between RX/TX traffic mixes when the controller supports vendor ICE allocator programming.

## Dependencies And Integration Points
The header depends on `<ufs/ufshcd.h>`, Qualcomm ICE, Linux reset APIs, and UFS/UniPro bit definitions supplied elsewhere. It is tightly coupled to `ufs-qcom.c`, which consumes all register offsets and structures. Its MCQ constants integrate with the core MCQ operation-register layout, and its device-quirk bits extend the shared UFS device quirk namespace.

## Risks And Edge Cases
Register definitions are silicon contracts; wrong offsets or masks can corrupt unrelated controller state. The local `ceil(freq, div)` macro is simple and could collide if included more broadly, but this private header is only intended for the QCOM driver. Static EOM coordinates encode a narrow tuning model for HS-G6 and should not be reused blindly for other controller revisions.

## Test Signals
Compile coverage should verify all masks and inline helpers against available UFS core definitions. Runtime evidence comes indirectly from QCOM probe, reset, debug dump, MCQ, ICE, EOM/FOM, and clock-scaling tests. Register dump comparisons across v2/v3+ hardware validate the version-dependent debug-offset helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-qcom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-renesas.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-renesas.c

## Purpose
`ufs-renesas.c` is the Renesas R-Car UFS platform variant for `renesas,r8a779f0-ufs`. It supplies the SoC-specific PHY/controller initialization sequences, firmware/calibration handling, runtime PM clock bracketing, DMA mask restriction, and debug register dumping needed before the generic UFS core can bring up the link.

## Important APIs, Types, And Functions
The private state is `struct ufs_renesas_priv`, containing optional firmware, a selected `pre_init` function, a one-time `initialized` flag, and eight calibration bytes read from NVMEM. The main variant callbacks are `ufs_renesas_init()`, `ufs_renesas_exit()`, `ufs_renesas_hce_enable_notify()`, `ufs_renesas_setup_clocks()`, `ufs_renesas_set_dma_mask()`, and `ufs_renesas_dbg_register_dump()`.

The file has many small helpers for indirect register access and PHY programming: `ufs_renesas_write_800_80c_poll()`, `ufs_renesas_write_phy()`, `ufs_renesas_set_phy()`, reset indirect writes, timer disable/restore, and compensation/slicer programming. Two pre-init sequences are selected: `ufs_renesas_r8a779f0_es10_pre_init()` fallback and `ufs_renesas_r8a779f0_pre_init()` for firmware plus calibration.

## Control Flow And State
Probe calls `ufshcd_pltfrm_init()` with `ufs_renesas_vops`. `ufs_renesas_init()` allocates private state, sets `UFSHCD_QUIRK_HIBERN_FASTAUTO`, checks SoC revision fallback rules, attempts to load `r8a779f0_ufs.bin`, reads the `calibration` NVMEM cell, and chooses either the calibrated firmware path or the ES1.0 fallback path. HCE enable notification runs the selected pre-init only once, during PRE_CHANGE, then marks `initialized`.

The initialization sequence writes controller vendor registers through `0xd0/0xd4` windows, polls completion bits, temporarily disables timers, applies many PHY indirect settings, optionally writes firmware words into PHY memory, then restores timer state. Runtime state is memory-only and released at driver exit with `release_firmware()`.

## Dependencies And Integration Points
The driver integrates with the platform UFS glue, firmware loader, NVMEM, SoC revision matching, runtime PM, big-endian/local register access helpers, and the generic UFS core. It constrains DMA with a 32-bit coherent mask. Its DT match table covers `renesas,r8a779f0-ufs`.

## Risks And Edge Cases
The pre-init code is register-sequence sensitive and largely opaque; failures may only show as link startup failures. Firmware and calibration failures intentionally fall back to ES1.0 init, which keeps the device usable but may be suboptimal for later silicon. `ufs_renesas_hce_enable_notify()` sets `initialized` even for non-PRE statuses after the first call, so callback ordering from the core matters. Poll failures log errors but helper functions often continue, making hardware bring-up diagnostics dependent on later failures.

## Test Signals
Test on ES1.0/ES1.1 fallback and non-fallback R-Car hardware, with and without firmware and NVMEM calibration. Validate HCE enable is one-shot across error recovery, runtime PM get/put pairing in clock setup, 32-bit DMA mask configuration, link startup after firmware load, and debug dump availability for vendor registers around `0xc0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-renesas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-rockchip.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-rockchip.c

## Purpose
`ufs-rockchip.c` is the Rockchip UFS platform variant, currently matching RK3576. It wires the generic UFS host core to Rockchip reset controls, clocks, memory-mapped HCI/MPHY GRF registers, device reset GPIO, RK3576 PHY initialization, and runtime/system PM behavior.

## Important APIs, Types, And Functions
The main variant table is `ufs_hba_rk3576_vops`, with `.init`, `.device_reset`, `.hce_enable_notify`, and `.phy_initialization`. `ufs_rockchip_common_init()` maps named resources (`hci_grf`, `mphy_grf`, `mphy`), obtains reset controls, enables `ref_out` and bulk clocks, acquires reset GPIO, and binds `struct ufs_rockchip_host` to the HBA. `ufs_rockchip_rk3576_phy_init()` programs UniPro/M-PHY DME attributes and direct MPHY registers. PM entry points wrap `ufshcd_runtime_suspend/resume` and `ufshcd_system_suspend/resume`.

## Control Flow And State
Probe looks up variant ops from OF match data and calls `ufshcd_pltfrm_init()`. RK3576 init sets UFSHCD quirks/capabilities for timeout handling, BKOPS, deep sleep, clock scaling, and WriteBooster, sets default runtime/system PM levels to level 5, and performs common resource setup. HCE PRE resets the controller; HCE POST resets/enables DME and runs PHY initialization. The PHY path toggles M-PHY config mode, writes lane-specific TX/RX timing and power-saving values, writes common and per-lane MPHY registers, then configures CPort link-up attributes.

Runtime state is held in `struct ufs_rockchip_host`: MMIO bases, reset GPIO/control, enabled clocks, and HBA backpointer. Suspend disables `ref_out` and may keep the genpd on depending on PM level; resume reenables `ref_out`, resets the controller for runtime resume, then returns control to the UFS core.

## Dependencies And Integration Points
The driver depends on platform resources named by DT, Linux reset/clock/GPIO/PM-domain APIs, `ufshcd-pltfrm`, UFS UniPro attributes, and the register definitions in `ufs-rockchip.h`. OF compatible `rockchip,rk3576-ufshc` supplies the RK3576 variant table.

## Risks And Edge Cases
Most DME writes in `ufs_rockchip_rk3576_phy_init()` ignore return codes, so partial PHY programming can be reported only later as link failure. Required reset GPIO and named MMIO resources make DT correctness critical. PM handling must coordinate `ref_out` with genpd state and UFS core suspend levels; a mismatch can strand the link or over-power the domain. There is no remove-time custom cleanup beyond managed resources and `ufshcd_pltfrm_remove()`.

## Test Signals
Use RK3576 hardware boot tests, DT resource-name validation, HCE PRE/POST link startup, runtime suspend/resume with PM levels below and at level 5, system suspend with `device_set_awake_path()`, reset GPIO pulse observation, and link stability under clock scaling and WriteBooster-enabled workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-rockchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-rockchip.h -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-rockchip.h

## Purpose
`ufs-rockchip.h` is the private register and state definition header for the Rockchip UFS host variant. It defines lane selector IDs, vendor DME attributes, direct MPHY register offsets, MPHY config mode values, endian/debug attributes, the Rockchip host state structure, and small MMIO helper macros.

## Important APIs, Types, And Macros
Important constants include `SEL_TX_LANE*`, `SEL_RX_LANE*`, `VND_TX_*`, `VND_RX_*`, `CMN_REG*`, `TRSV*_REG*`, `MPHY_CFG`, and `MIB_T_DBG_CPORT_*`. `struct ufs_rockchip_host` stores the HBA pointer, `ufs_phy_ctrl`, `ufs_sys_ctrl`, `mphy_base`, reset GPIO, reset control array, `ref_out_clk`, bulk clocks, and a `caps` field. `ufs_sys_writel()`, `ufs_sys_readl()`, `ufs_sys_set_bits()`, and `ufs_sys_ctrl_clr_bits()` wrap raw MMIO access.

## Control Flow And State
The header has no independent flow. Its definitions are consumed by `ufs-rockchip.c` during RK3576 PHY initialization and reset/clock setup. The state structure is allocated during variant init and then consulted by HCE, device reset, and PM callbacks.

## Dependencies And Integration Points
The header assumes Linux I/O accessors and UFS core types are available through the including C file. The lane selector and register constants must match RK3576 M-PHY hardware documentation. It is private to the Rockchip driver and not an exported UFS subsystem interface.

## Risks And Edge Cases
Register offsets and values are hardware-specific and not self-describing. The MMIO macros perform relaxed raw access without validation; callers must pass mapped bases and valid offsets. The `caps` field is currently not used in the C file, so future changes should either use it deliberately or avoid accumulating dead state.

## Test Signals
The header is tested through successful RK3576 compile and runtime PHY bring-up. Register programming can be validated by readback/debug instrumentation around the MPHY offsets and by link startup stability across both lanes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-rockchip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-sprd.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-sprd.c

## Purpose
`ufs-sprd.c` is the Unisoc/Sprd UFS platform variant for `sprd,ums9620-ufs`. It supplies reset, syscon, regulator, secure-monitor crypto enablement, PHY SRAM/calibration programming, Hibern8 reference-clock control, and variant operations for the generic UFS core.

## Important APIs, Types, And Functions
The driver uses `struct ufs_sprd_host` and `struct ufs_sprd_priv` from `ufs-sprd.h`. Common helpers parse reset controls, syscon phandles, and regulators; `ufs_sprd_common_init()` allocates host state, binds match-data private ops, sets UFS capabilities/quirks, and parses DT. N6-specific callbacks include `ufs_sprd_n6_init()`, `sprd_ufs_n6_hce_enable_notify()`, `ufs_sprd_n6_phy_init()`, `sprd_ufs_n6_h8_notify()`, `ufs_sprd_n6_device_reset()`, and `ufs_sprd_suspend()`.

## Control Flow And State
Probe retrieves the OF match entry and passes its embedded variant ops to `ufshcd_pltfrm_init()`. N6 init enables the MPHY regulator and, if crypto remains advertised, calls `ufs_sprd_n6_key_acc_enable()` to enable key-register access via an ARM SMCCC SiP call after ensuring HCE is set. HCE PRE sets PHY SRAM flags in syscon, resets the host, and retries crypto access; HCE POST initializes PHY DME attributes, waits for SRAM init completion via syscon polling, applies lane AFE calibration writes, enables MPHY, and records UniPro version.

The power-change notify configures initial adaptation when UniPro is at least 1.8. Hibern8 notify disables UIC completion interrupt before enter and controls AON APB reference-clock/PLL bits around enter/exit. Suspend disables auto-Hibern8 timer under the host lock during PRE_CHANGE. Runtime state includes reset controls, syscon regmaps, regulator handles, HBA backpointer, and cached UniPro version.

## Dependencies And Integration Points
The driver depends on DT match data, syscon/regmap, reset controls named `"controller"` and `"device"`, regulator `"vdd-mphy"`, ARM SMCCC, UFS core PM/link callbacks, and vendor DME attributes in `ufs-sprd.h`. It advertises clock gating, crypto, and WriteBooster to the core, with crypto dynamically disabled if secure firmware refuses key access.

## Risks And Edge Cases
`ufs_sprd_n6_key_acc_enable()` loops around HCE enable and may clear crypto capability on failure; this affects blk-crypto availability for the lifetime of the HBA. PHY init depends on a 10-iteration millisecond-scale SRAM done poll and ignores many DME set return values. Hibern8 notification masks UIC completion interrupts and toggles reference clocks, so incorrect callback ordering can produce missed completions or inaccessible HCI state.

## Test Signals
Validate probe with all DT phandles present, regulator enable failure paths, SMCCC crypto success/failure, HCE PRE/POST sequencing, PHY SRAM timeout handling, Hibern8 enter/exit with reference-clock scope checks, suspend auto-Hibern8 timer clearing, and power-mode changes on UniPro 1.8+ devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-sprd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-sprd.h -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-sprd.h

## Purpose
`ufs-sprd.h` is the private definitions header for the Unisoc UFS host driver. It collects vendor DME attributes, syscon offsets/bits, the ARM SMCCC function ID for storage crypto key access, enum indexes for reset/syscon/regulator arrays, and the Sprd host/private structures.

## Important APIs, Types, And Macros
Key macros include `RXSQCONTROL`, `CBRATESEL`, `CBCREG*`, `CBREFCLKCTRL2`, `VS_MPHYDISABLE`, AON APB reference-clock/PLL bits, and `SPRD_SIP_SVC_STORAGE_UFS_CRYPTO_ENABLE`. `enum SPRD_UFS_RST_INDEX`, `enum SPRD_UFS_SYSCON_INDEX`, and `enum SPRD_UFS_VREG_INDEX` provide stable array positions. `struct ufs_sprd_priv` stores named reset controls, syscon regmaps, regulators, and an embedded `ufs_hba_variant_ops`; `struct ufs_sprd_host` stores the active HBA, private SoC descriptor, optional debug MMIO, and cached UniPro version.

## Control Flow And State
The header does not execute code. The array-index enums drive DT parsing and N6 callback access in `ufs-sprd.c`. The embedded variant ops allow OF match data to point at the ops member and recover the containing SoC descriptor with `container_of()`.

## Dependencies And Integration Points
This header integrates with Linux reset, regmap, regulator, ARM SMCCC, and UFS core types through its including C file. It is private to `ufs-sprd.c`; no symbols are exported from it.

## Risks And Edge Cases
The `container_of()` match-data pattern depends on OF data pointing exactly to `ufs_hba_sprd_vops`. Any new SoC entry must keep array indexes aligned with callback assumptions. The SMCCC call value is a firmware ABI and must match secure monitor implementation.

## Test Signals
Compile tests should catch missing UFS/SMCCC constants. Runtime tests should validate the N6 descriptor arrays resolve every named DT resource and that crypto enable calls reach firmware with the expected function ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufs-sprd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufshcd-dwc.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/ufshcd-dwc.c

## Purpose
`ufshcd-dwc.c` provides shared helper logic for UFS hosts built around the Synopsys DesignWare Core. It programs the DWC clock divider, verifies link-up state, configures local and peer UniPro CPort/application connection attributes, and exports a link-startup notify callback for DWC-based platform drivers.

## Important APIs, Types, And Functions
Two symbols are exported: `ufshcd_dwc_dme_set_attrs()` and `ufshcd_dwc_link_startup_notify()`. `ufshcd_dwc_dme_set_attrs()` applies an array of `struct ufshcd_dme_attr_val` with `ufshcd_dme_set_attr()`. `ufshcd_dwc_link_startup_notify()` is intended for use as a UFS variant `.link_startup_notify` callback. Private helpers are `ufshcd_dwc_program_clk_div()`, `ufshcd_dwc_link_is_up()`, and `ufshcd_dwc_connection_setup()`.

## Control Flow And State
During PRE_CHANGE link startup, the driver writes `DWC_UFS_REG_HCLKDIV_DIV_125` to the DWC `HCLKDIV` register and invokes variant PHY initialization through `ufshcd_vops_phy_initialization()`. During POST_CHANGE, it reads `VS_POWERSTATE`; if the link is up it marks the HBA link active, then applies a static sequence of local and peer DME attributes to establish device IDs, peer IDs, CPort flags/mode, traffic class, and connection state.

No persistent private state is stored in this file. All state updates are made directly in the UFS core HBA or in UniPro attributes.

## Dependencies And Integration Points
The helpers depend on UFS core DME accessors, UniPro attribute IDs, and DWC register definitions from `ufshci-dwc.h`. They are exported for other DWC host drivers to reuse rather than registering a bus driver themselves.

## Risks And Edge Cases
The fixed 125 MHz divider and static CPort setup may be inappropriate for DWC integrations with different reference clocks or firmware-preconfigured connections. `ufshcd_dwc_link_is_up()` returns `1` rather than a negative errno on link-down, so callers should treat any nonzero as failure. DME attribute programming stops on first error, leaving a partially configured connection.

## Test Signals
Test with DWC-based hardware by observing PRE clock-divider write, PHY initialization callback execution, POST `VS_POWERSTATE` link-up detection, and successful traffic after connection setup. Negative tests should inject DME failures and link-down status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufshcd-dwc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufshcd-dwc.h -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/ufshcd-dwc.h

## Purpose
`ufshcd-dwc.h` declares the DesignWare UFS helper interface and shared RMMI/M-PHY constants used by DWC-based UFS host drivers.

## Important APIs, Types, And Macros
The public declarations are `ufshcd_dwc_link_startup_notify()` and `ufshcd_dwc_dme_set_attrs()`. `struct ufshcd_dme_attr_val` packages a DME attribute selector, value, and peer/local target flag for batch writes. The header also defines RMMI attributes such as `CBREFCLKCTRL2`, `CBCRCTRL`, and `CBCREG*`, M-PHY state attributes `MTX_FSM_STATE` and `MRX_FSM_STATE`, per-lane M-PHY register macros, and TX/RX FSM state enums.

## Control Flow And State
The header has no flow or storage. It defines the structure format consumed by `ufshcd_dwc_dme_set_attrs()` and symbolic constants consumed by DWC integrations during PHY/link setup.

## Dependencies And Integration Points
It includes `<ufs/ufshcd.h>` for UFS types and is paired with `ufshcd-dwc.c` and `ufshci-dwc.h`. DWC host variants can include it to reuse exported helpers and M-PHY constants.

## Risks And Edge Cases
Constants describe DWC M-PHY/RMMI behavior and may not apply to non-DWC controllers. The `peer` field is a small integer matching the DME peer/local convention; callers must provide the correct value.

## Test Signals
Compile tests validate ABI with `ufshcd-dwc.c`. Runtime use is covered by DWC link startup tests and any host driver that batches DME attribute programming with `struct ufshcd_dme_attr_val`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufshcd-dwc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufshcd-pci.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/ufshcd-pci.c

## Purpose
`ufshcd-pci.c` is the PCI bus glue for UFS host controllers. It maps PCI BAR resources, allocates and initializes `ufs_hba`, selects vendor-specific variant operations for QEMU and Intel platforms, manages PCI runtime/system PM, and implements Intel-specific DSM reset, LTR latency tolerance, debugfs, quirks, crypto enablement, and link-resume handling.

## Important APIs, Types, And Functions
The file registers `ufshcd_pci_driver` with `ufshcd_pci_probe()` and `ufshcd_pci_remove()`. `struct intel_host` stores ACPI DSM function bits, active/idle LTR cache, saved system PM level, debugfs root, and optional reset GPIO. Intel helper families include DSM (`intel_dsm_init()`, `intel_dsm()`), link and LCC callbacks, LKF power-change/device-quirk logic, LTR/debugfs (`intel_ltr_set()`, `intel_add_debugfs()`), reset (`ufs_intel_device_reset()`), common init/exit, and per-platform init functions for CNL/EHL/LKF/ADL/MTL.

QEMU MCQ support is implemented by `ufs_qemu_get_hba_mac()`, `ufs_qemu_mcq_config_resource()`, and `ufs_qemu_op_runtime_config()`. The PCI ID table maps Red Hat/QEMU and multiple Intel device IDs to variant ops.

## Control Flow And State
Probe enables the PCI device, sets bus mastering, maps BAR0 with `pcim_iomap_region()`, allocates an HBA, assigns variant ops from `id->driver_data`, and calls `ufshcd_init()`. Remove forbids runtime PM, grabs the device without resume, and removes the HBA.

Intel common init enables runtime autosuspend, allocates `intel_host`, probes ACPI DSM support, chooses DSM reset or reset GPIO, exposes PM QoS latency tolerance, and creates debugfs LTR files. Platform-specific init adds quirks and caps: EHL/CNL handle broken auto-Hibern8, LKF adds crypto and reset-focused PM levels, ADL performs link startup once and WriteBooster, MTL adds crypto/WriteBooster with shallower PM levels. Resume exits Hibern8 if necessary or forces link-off for full recovery. System suspend preparation temporarily raises Intel non-s2idle suspend to power-off level 5 and restores the saved level on complete.

## Dependencies And Integration Points
This file depends on PCI core, runtime PM, PM QoS, suspend state, debugfs, ACPI DSM, GPIO descriptors, and UFS core APIs. Intel ACPI DSM GUID functions provide reset capability discovery and execution. QEMU MCQ integration reads standard MCQ config offsets from emulated registers.

## Risks And Edge Cases
If no variant ops are supplied for a PCI ID, the HBA falls back to no vendor ops, which may be acceptable only for standard controllers. Intel reset behavior depends on DSM result semantics or optional active-low GPIO. LTR writes are made under runtime PM get/put and update cached debugfs values; failures in PM resume could affect latency requests. Suspend preparation mutates `hba->spm_lvl` and must restore it on both failure and completion. QEMU MCQ uses a fixed stride of 48 and assumes emulated offset registers are valid.

## Test Signals
Test PCI probe/remove, BAR mapping, runtime PM enable/disable, QEMU MCQ operation queues, Intel DSM discovery/reset, GPIO reset fallback, debugfs LTR readback, PM QoS latency writes, s2idle versus non-s2idle suspend behavior, Hibern8 resume failure recovery, LKF lane/TACTIVATE quirks, and crypto enablement after HCE on LKF/MTL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufshcd-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufshcd-pltfrm.c -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/ufshcd-pltfrm.c

## Purpose
`ufshcd-pltfrm.c` is the common platform-bus glue for UFS host drivers. It parses DT clocks, regulators, lane counts, OPP tables, and gear/rate limits; provides host/device power-mode negotiation defaults; maps platform MMIO/IRQ resources; allocates and initializes the generic UFS HBA; and handles platform remove.

## Important APIs, Types, And Functions
Exported APIs are `ufshcd_populate_vreg()`, `ufshcd_negotiate_pwr_params()`, `ufshcd_parse_gear_limits()`, `ufshcd_init_host_params()`, `ufshcd_pltfrm_init()`, and `ufshcd_pltfrm_remove()`. Private helpers parse clock info from `freq-table-hz`, regulator phandles/current limits for `vdd-hba`, `vcc`, `vccq`, and `vccq2`, `lanes-per-direction`, and `operating-points-v2`.

## Control Flow And State
Variant platform drivers call `ufshcd_pltfrm_init(pdev, vops)`. It maps resource 0, obtains IRQ 0, allocates an HBA, stores variant ops, parses clocks and regulators, initializes lanes per direction, parses OPP data if present, and calls `ufshcd_init()`. After successful core initialization it marks runtime PM active and enables runtime PM. Remove obtains the HBA from platform drvdata, resumes it synchronously, calls `ufshcd_remove()`, disables runtime PM, and drops the no-idle PM reference.

Clock parsing supports two mutually exclusive models. `freq-table-hz` provides per-clock min/max pairs matched to `clock-names`; `operating-points-v2` configures OPP with indexed clocks and backfills min/max frequencies from the OPP table. Host parameter initialization supplies two lanes, HS-G3, PWM-G4, FAST HS, SLOW PWM, Rate B, and HS desired mode. Negotiation chooses power mode, lanes, gear, and rate from the intersection of host policy and device maximums.

## Dependencies And Integration Points
The file depends on OF, Linux clocks, regulators through UFS core vreg structures, PM OPP, platform devices, runtime PM, UniPro constants, and the generic `ufshcd` core. It is used by Qualcomm, Renesas, Rockchip, Unisoc, and other platform UFS drivers.

## Risks And Edge Cases
`operating-points-v2` and `freq-table-hz` are explicitly incompatible. DT clock count and frequency-array length mismatches fail probe. Missing regulator phandles are treated as always-on, while present-but-invalid regulator properties fail. Negotiation returns `-ENOTSUPP` when host requires HS but the device does not support it. Optional `limit-hs-gear` and `limit-gear-rate` can silently constrain performance if DT is wrong.

## Test Signals
Test DT variants with no clocks, `freq-table-hz`, and OPP tables; malformed clock arrays; missing and present regulators; lane-count defaults; gear/rate limit properties; negotiation across HS/PWM device capabilities; runtime PM enablement after probe; and remove-time PM/HBA teardown ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufshcd-pltfrm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufshcd-pltfrm.h -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/ufshcd-pltfrm.h

## Purpose
`ufshcd-pltfrm.h` declares the shared platform-bus UFS glue API and the `struct ufs_host_params` policy structure used by platform variants to negotiate link power mode, gear, lanes, and HS rate.

## Important APIs, Types, And Macros
The header defines `UFS_PWM_MODE`, `UFS_HS_MODE`, and `struct ufs_host_params`, which records preferred PWM/HS RX/TX gear, lane counts, PWM/HS power modes, HS rate, and desired working mode. It declares `ufshcd_negotiate_pwr_params()`, `ufshcd_init_host_params()`, `ufshcd_parse_gear_limits()`, `ufshcd_pltfrm_init()`, `ufshcd_pltfrm_remove()`, and `ufshcd_populate_vreg()`.

## Control Flow And State
The header contains no executable flow. Platform drivers allocate or embed `struct ufs_host_params`, initialize it through `ufshcd_init_host_params()`, optionally apply DT limits, and pass it into negotiation during power-mode changes. Probe/remove helpers are called directly by platform bus drivers.

## Dependencies And Integration Points
It includes `<ufs/ufshcd.h>` for HBA, variant ops, vreg, and power attribute types. It is the interface boundary between generic platform parsing in `ufshcd-pltfrm.c` and SoC-specific UFS drivers such as QCOM, Renesas, Rockchip, and Sprd.

## Risks And Edge Cases
The structure assumes symmetric policy is usually desired but exposes separate RX/TX fields; variant drivers must keep them coherent if hardware only supports symmetric operation. Wrong desired mode or gear limits can make negotiation fail or force a lower-performing link.

## Test Signals
Compile all platform variants against the declarations. Runtime tests should exercise default host-parameter initialization, DT gear/rate limit parsing, and power-mode negotiation callbacks in each platform driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufshcd-pltfrm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufshci-dwc.h -->
# sources/distributed-fs/ceph-client/drivers/ufs/host/ufshci-dwc.h

## Purpose
`ufshci-dwc.h` defines DesignWare UFSHCI-specific host-controller register offsets, clock-divider values, and selector indexes used by DWC helper code and DWC host variants.

## Important APIs, Types, And Macros
The header provides `enum dwc_specific_registers` with `DWC_UFS_REG_HCLKDIV`, `enum clk_div_values` with 62.5/125/200 MHz encoded divider values, and `enum selector_index` for lane TX/RX selector indexes.

## Control Flow And State
The header is declarative only. `ufshcd-dwc.c` uses `DWC_UFS_REG_HCLKDIV` and `DWC_UFS_REG_HCLKDIV_DIV_125` during link startup PRE_CHANGE.

## Dependencies And Integration Points
It is paired with `ufshcd-dwc.c` and `ufshcd-dwc.h`. DWC host integrations can include it when they need DWC-specific register constants distinct from generic UFSHCI registers.

## Risks And Edge Cases
Divider enum values are encoded as hexadecimal MHz equivalents and assume the controller's expected representation. Integrations with different HCLK requirements must not blindly use the 125 MHz default.

## Test Signals
Runtime validation is the DWC clock-divider write during link startup and successful link bring-up. Static tests should ensure no generic UFSHCI code accidentally depends on DWC-only constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ufs/host/ufshci-dwc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/uio/Kconfig

## Purpose
`drivers/uio/Kconfig` declares the Userspace I/O subsystem menu and the build-time configuration options for UIO core and in-tree UIO drivers. It controls whether `/dev/uioN` support and specific PCI, platform, Hyper-V, DFL, and eLBC/GPCM wrappers are built.

## Important Options
`UIO` is the top-level tristate and depends on `MMU`. Child options include `UIO_CIF`, `UIO_PDRV_GENIRQ`, `UIO_DMEM_GENIRQ`, `UIO_AEC`, `UIO_SERCOS3`, `UIO_PCI_GENERIC`, `UIO_NETX`, `UIO_FSL_ELBC_GPCM`, optional `UIO_FSL_ELBC_GPCM_NETX5152`, `UIO_MF624`, `UIO_HV_GENERIC`, `UIO_DFL`, and `UIO_PCI_GENERIC_SVA`. Dependencies gate bus or feature availability, such as `PCI`, `HAS_DMA`, `FSL_LBC`, `HYPERV_VMBUS`, `FPGA_DFL`, and `IOMMU_SVA`.

## Control Flow And State
Kconfig has no runtime flow. Its state is the kernel configuration, which drives compilation and module availability. Help text documents the userspace responsibility common to UIO: kernel code exposes interrupts and memory, while device-specific policy and acknowledgement are typically handled by userspace.

## Dependencies And Integration Points
The options feed `drivers/uio/Makefile` through `CONFIG_*` symbols. They integrate with broader kernel subsystems by depending on bus and hardware framework symbols.

## Risks And Edge Cases
Because UIO exposes device memory and interrupt control to userspace, enabling generic options can be a security and stability decision rather than a pure driver selection. Some help URLs are historical. `UIO_PCI_GENERIC_SVA` advertises Shared Virtual Addressing and should be enabled only when IOMMU SVA support and the target security model are understood.

## Test Signals
Use `olddefconfig`/`allyesconfig` style compile coverage for dependency correctness, module-name checks against `Makefile`, and boot/module-load tests for selected drivers. Configuration tests should verify unavailable dependencies hide or disable the corresponding driver options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/uio/Makefile

## Purpose
`drivers/uio/Makefile` maps UIO Kconfig symbols to object files for the UIO core and individual UIO drivers.

## Important Entries
`obj-$(CONFIG_UIO) += uio.o` builds the core. Each child config maps directly to a driver object, including `uio_cif.o`, `uio_pdrv_genirq.o`, `uio_dmem_genirq.o`, `uio_aec.o`, `uio_sercos3.o`, `uio_pci_generic.o`, `uio_netx.o`, `uio_mf624.o`, `uio_fsl_elbc_gpcm.o`, `uio_hv_generic.o`, `uio_dfl.o`, and `uio_pci_generic_sva.o`.

## Control Flow And State
There is no runtime control flow. Kbuild evaluates the `CONFIG_*` symbols and either links objects built-in, builds modules, or omits them.

## Dependencies And Integration Points
The Makefile depends on Kconfig symbol names matching object names and source files in the same directory. It integrates with the kernel build system's `obj-*` convention.

## Risks And Edge Cases
Stale entries cause build failures if the source file is absent or Kconfig symbol is renamed. Formatting is mostly standard, though the `UIO_MF624` and `UIO_PCI_GENERIC_SVA` lines use different spacing, which is harmless.

## Test Signals
Build UIO core and each module as `m` and built-in where dependencies allow. Check that every enabled Kconfig option produces the documented module object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio.c -->
# sources/distributed-fs/ceph-client/drivers/uio/uio.c

## Purpose
`uio.c` is the Userspace I/O core. It creates the `uio` character-device major and class, registers `/dev/uioN` devices for provider drivers, exposes maps and port regions in sysfs, delivers interrupt events through blocking reads/poll/fasync, supports userspace IRQ masking through writes, and maps provider-declared memory regions into userspace.

## Important APIs, Types, And Functions
Exported APIs are `uio_event_notify()`, `__uio_register_device()`, `__devm_uio_register_device()`, and `uio_unregister_device()`. Important internal types are `struct uio_map`, `struct uio_portio`, and `struct uio_listener`. The file operations are `uio_open()`, `uio_release()`, `uio_read()`, `uio_write()`, `uio_poll()`, `uio_mmap()`, and `uio_fasync()`.

Sysfs support includes device attributes `name`, `version`, and `event`, per-map attributes `name`, `addr`, `size`, `offset`, and per-port attributes `name`, `start`, `size`, `porttype`. Memory mapping supports `UIO_MEM_PHYS`, `UIO_MEM_IOVA`, `UIO_MEM_LOGICAL`, `UIO_MEM_VIRTUAL`, `UIO_MEM_DMA_COHERENT`, and provider-specific `mmap_prepare`.

## Control Flow And State
Module init allocates a character-device region for `UIO_MAX_DEVICES`, creates a `cdev`, and registers the `uio` class. Provider registration allocates a `struct uio_device`, assigns a minor through `idr`, creates the device, adds map/port sysfs objects, and requests a threaded IRQ unless the provider uses custom/no IRQ. The hard IRQ handler calls the provider handler and wakes the threaded handler on `IRQ_HANDLED`; the thread increments `idev->event`, wakes waiters, and sends SIGIO.

Open pins the device and owner module, allocates a listener with the current event count, and calls provider `open`. Read requires a 32-bit count, blocks until `idev->event` changes, then copies the new event count. Write requires a 32-bit value and calls provider `irqcontrol`. Mmap validates the map index encoded in `vm_pgoff`, requested size, and memory type before remapping physical, logical/vmalloc, DMA coherent, or provider-custom memory.

State is protected by `minor_lock` for the IDR and `idev->info_lock` for provider data lifetime. Unregister removes sysfs, frees IRQ, nulls `idev->info`, wakes readers with hangup, frees the minor, and unregisters the device while open file references can drain later.

## Dependencies And Integration Points
The core depends on Linux device class/cdev/idr/kobject/sysfs infrastructure, wait queues, fasync, IRQ threading, DMA mapping, VM fault/remap helpers, and `linux/uio_driver.h`. All UIO leaf drivers depend on these exported APIs and `struct uio_info`.

## Risks And Edge Cases
UIO intentionally exposes hardware to userspace, so provider correctness and permissions are critical. `uio_dev_del_attributes()` assumes map/port kobjects were created for every nonzero region. DMA coherent mapping is explicitly warned as discouraged. Providers must not free IRQ resources before unregister unless following the documented ordering. Event counters are 32-bit and can wrap; userspace should compare for inequality rather than monotonic distance.

## Test Signals
Test registration/unregistration with open FDs, blocking and nonblocking reads, poll/fasync, irqcontrol writes, custom IRQ/no IRQ devices, every memory type mmap path, sysfs map/port attributes, minor exhaustion, provider `open`/`release` errors, unregister wakeups returning errors, and module init/exit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_aec.c -->
# sources/distributed-fs/ceph-client/drivers/uio/uio_aec.c

## Purpose
`uio_aec.c` is a UIO PCI driver for the Adrienne Electronics Corporation VITC/LTC time-code device. It exposes the device's I/O port BAR to userspace and provides a small interrupt handler that validates and acknowledges device interrupt state enough for UIO event delivery.

## Important APIs, Types, And Functions
The PCI ID table matches vendor `0xaecb`, device `0x6250`. `probe()` allocates `struct uio_info`, enables the PCI device, requests regions, maps BAR0 with `pci_iomap()`, fills `info->port[0]`, installs `aectc_irq()`, registers the UIO device, and enables/masks device interrupts. `remove()` disables interrupts, reads the mailbox to drop IRQ state, unregisters UIO, releases regions, disables PCI, and unmaps.

## Control Flow And State
The IRQ handler reads `INTA_DRVR_ADDR`; if interrupts are enabled and active, it reads `MAILBOX` and returns `IRQ_HANDLED`, allowing the UIO core to notify userspace. Userspace is expected to write to the device port to request subsequent interrupts. Driver state is the `uio_info` stored in PCI drvdata and the BAR mapping in `info->priv`.

## Dependencies And Integration Points
The driver depends on PCI core, I/O port/MMIO accessors, and UIO core registration. It uses a UIO port region rather than `uio_mem`, so userspace needs port I/O tooling rather than normal mmap.

## Risks And Edge Cases
Error paths return `-ENODEV` broadly, losing precise failure causes. Interrupt handling is shared and device-specific; false positives can disturb shared IRQ lines if register semantics are misunderstood. Remove ordering disables interrupts before unregister, which is necessary because userspace controls much of device behavior.

## Test Signals
Test PCI probe/remove, sysfs port attributes, interrupt enable/mask registers, shared IRQ filtering, mailbox read acknowledgement, userspace re-enable behavior, and cleanup after failed BAR mapping or UIO registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_aec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_cif.c -->
# sources/distributed-fs/ceph-client/drivers/uio/uio_cif.c

## Purpose
`uio_cif.c` is a UIO PCI driver for Hilscher CIF Profibus and DeviceNet cards behind a PLX9030 bridge. It exposes BAR0 and BAR2 as physical UIO mappings and supplies an IRQ handler that disables PLX INT1 until userspace handles the device.

## Important APIs, Types, And Functions
The PCI ID table matches PLX9030 devices with Hilscher subvendor and Profibus/DeviceNet subdevices. `hilscher_pci_probe()` enables PCI, requests regions, maps BAR0 internally for interrupt control, publishes BAR0 and BAR2 in `uio_info.mem`, sets a product-specific `info->name`, and registers UIO with shared IRQ handler `hilscher_handler()`. Remove unregisters UIO, releases regions, disables PCI, and unmaps BAR0.

## Control Flow And State
The IRQ handler reads BAR0 `PLX9030_INTCSR`. If INT1 is both enabled and active, it clears `INTSCR_INT1_ENABLE` and returns `IRQ_HANDLED`; otherwise it returns `IRQ_NONE`. UIO core then increments the event counter. Userspace is responsible for device-level acknowledgement and re-enabling.

## Dependencies And Integration Points
The driver depends on PCI, PLX bridge register layout, UIO core, and userspace CIF protocol handling. It integrates through `/dev/uioN` plus `maps/map0` and `maps/map1`.

## Risks And Edge Cases
Only BAR0 is internally mapped, so interrupt control assumes PLX INTCSR is in BAR0. Shared IRQ filtering must be exact. The driver does not provide an `irqcontrol` callback, so re-enable likely requires userspace MMIO writes to BAR0. Probe error paths also return `-ENODEV` for multiple causes.

## Test Signals
Validate both supported subdevices, BAR sysfs map sizes, interrupt disable on INT1, shared IRQ non-ownership returning `IRQ_NONE`, userspace interrupt re-enable, and remove while userspace mappings are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_cif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_dfl.c -->
# sources/distributed-fs/ceph-client/drivers/uio/uio_dfl.c

## Purpose
`uio_dfl.c` is a generic UIO driver for selected Intel FPGA DFL features. It exposes a DFL feature's MMIO resource to userspace without IRQ support.

## Important APIs, Types, And Functions
`uio_dfl_probe()` allocates `struct uio_info`, names it `uio_dfl`, describes one `UIO_MEM_PHYS` mapping from `ddev->mmio_res` with page alignment and offset, sets `irq = UIO_IRQ_NONE`, and registers it with `devm_uio_register_device()`. The DFL ID table matches several FME and PORT feature IDs, including Ethernet group, HSSI subsystem, vendor-specific, and IOPLL user clock.

## Control Flow And State
Probe is the only driver flow; devres handles unregister on device teardown. There is no runtime private state beyond the managed UIO info and map metadata.

## Dependencies And Integration Points
The driver depends on the FPGA DFL bus and UIO core. Userspace accesses the DFL feature through the UIO mmap and must implement any device semantics itself.

## Risks And Edge Cases
No IRQs are exposed, so polling or userspace-specific synchronization is required. The page-alignment calculation exposes the full pages covering the DFL resource, with `offs` telling userspace where the feature begins; userspace must honor the offset and resource size.

## Test Signals
Test binding to each listed DFL feature ID, map offset/size correctness for unaligned resources, devm cleanup on unbind, and userspace mmap/read/write access to the expected feature registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_dfl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_dmem_genirq.c -->
# sources/distributed-fs/ceph-client/drivers/uio/uio_dmem_genirq.c

## Purpose
`uio_dmem_genirq.c` is a platform UIO driver that combines generic non-shared interrupt handling with fixed platform memory resources and dynamically allocated DMA-coherent memory regions. It is intended for devices whose detailed interrupt acknowledgement and device policy live in userspace.

## Important APIs, Types, And Functions
Private state is `struct uio_dmem_genirq_platdata`, containing the UIO info pointer, interrupt lock/flags, platform device, dynamic-region start/count, allocation mutex, and open refcount. The key callbacks are `uio_dmem_genirq_open()`, `uio_dmem_genirq_release()`, `uio_dmem_genirq_handler()`, `uio_dmem_genirq_irqcontrol()`, and `uio_dmem_genirq_probe()`.

## Control Flow And State
Probe accepts platform data or creates basic DT-derived `uio_info`, rejects provider-supplied handlers/shared IRQs, sets a 32-bit coherent DMA mask, discovers the first platform IRQ, converts memory resources to `UIO_MEM_PHYS` maps, appends dynamic `UIO_MEM_DMA_COHERENT` maps with `DMEM_MAP_ERROR` placeholder addresses, installs generic IRQ/open/release callbacks, enables runtime PM, and registers the UIO device with devres.

On first open, dynamic regions are allocated with `dma_alloc_coherent()`, their CPU and DMA addresses are stored in `uio_mem`, the refcount is incremented, and runtime PM resumes the device. On release, runtime PM idles the device and the last close frees all dynamic regions and restores `DMEM_MAP_ERROR`. The IRQ handler disables the IRQ once and sets `UIO_IRQ_DISABLED`; userspace writes call `irqcontrol` to enable or disable while preserving IRQ depth.

## Dependencies And Integration Points
The driver depends on platform resources or `uio_dmem_genirq_pdata`, DMA coherent allocation, runtime PM, IRQ trigger metadata, UIO core, and optional OF naming. It uses `IRQ_DISABLE_UNLAZY` for level-triggered IRQs because hardware acknowledgement happens in userspace.

## Risks And Edge Cases
The code assumes platform data exists for dynamic-region sizes even when a DT node creates `uioinfo`; DT users without pdata can hit invalid access depending on how the platform device is constructed. Dynamic allocation failures set map addresses to `DMEM_MAP_ERROR`, and userspace must not mmap before successful open. Shared interrupts are rejected. Refcounting protects allocation lifetime, but multiple users share the same dynamic buffers while open.

## Test Signals
Test fixed-only and fixed-plus-dynamic devices, first-open allocation, multi-open refcounting, last-close free, DMA mmap, runtime PM get/put pairing, level IRQ lazy-disable behavior, userspace irqcontrol toggling, nonblocking UIO reads, and invalid shared IRQ configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_dmem_genirq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_fsl_elbc_gpcm.c -->
# sources/distributed-fs/ceph-client/drivers/uio/uio_fsl_elbc_gpcm.c

## Purpose
`uio_fsl_elbc_gpcm.c` exposes a peripheral connected to a Freescale/NXP enhanced Local Bus Controller bank in GPCM mode through UIO. It validates and programs eLBC BR/OR registers, maps the peripheral memory window, optionally provides netX 51/52 interrupt support, and exposes sysfs attributes for controlled BR/OR tuning.

## Important APIs, Types, And Functions
Private state is `struct fsl_elbc_gpcm`, which stores the device, eLBC register base, bank number, display name, and optional type-specific init/shutdown/IRQ callbacks. Sysfs attributes `reg_br` and `reg_or` use `reg_show()` and `reg_store()`. DT parsing and validation are handled by `get_of_data()` and `check_of_data()`. Probe and remove are `uio_fsl_elbc_gpcm_probe()` and `uio_fsl_elbc_gpcm_remove()`. Optional netX support adds `netx5152_irq_handler()`, `netx5152_init()`, and `netx5152_shutdown()`.

## Control Flow And State
Probe requires the global FSL LBC controller registers, parses the child node resource, bank number, `elbc-gpcm-br`, `elbc-gpcm-or`, optional `device_type`, IRQ, and `uio_name`, then validates bank, mode, address mask, and base address. It checks whether the bank is already valid and compatible, warns if behavior bits change, writes OR then BR with forced base/GPCM/valid bits, maps the resource with `ioremap()`, fills UIO memory metadata, optionally installs a type-specific IRQ handler, runs type init, registers UIO, and stores drvdata.

`reg_store()` permits runtime BR/OR changes only when the effective base address, GPCM mode, and address mask remain stable. NetX IRQ handling checks enabled and active interrupt bits in the mapped DPM window, disables global interrupts, and leaves acknowledgement/re-enable to userspace. Remove unregisters UIO, calls type shutdown, and unmaps the resource.

## Dependencies And Integration Points
The driver depends on `FSL_LBC`, OF address/IRQ parsing, UIO core, eLBC register definitions, and optional `CONFIG_UIO_FSL_ELBC_GPCM_NETX5152`. It matches `fsl,elbc-gpcm-uio` DT nodes.

## Risks And Edge Cases
Programming BR/OR affects shared local-bus state, so DT validation and sysfs write restrictions are critical. The global `fsl_lbc_ctrl_dev` must be initialized before probe. Optional IRQs without a known type handler are ignored. NetX offsets and masks are type-specific and must not be used for generic peripherals.

## Test Signals
Test DT validation failures for bank, mode, size mask, and base address; already-configured bank compatibility; sysfs BR/OR allowed and rejected writes; generic no-IRQ devices; netX IRQ disable/init/shutdown; UIO mmap correctness; and remove cleanup after userspace has opened the device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_fsl_elbc_gpcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_hv_generic.c -->
# sources/distributed-fs/ceph-client/drivers/uio/uio_hv_generic.c

## Purpose
`uio_hv_generic.c` is a generic UIO driver for Hyper-V VMBus devices that are manually bound by dynamic ID. It exposes VMBus ring buffers, interrupt/monitor pages, and for network devices send/receive GPADL buffers to userspace, while translating VMBus channel callbacks into UIO events.

## Important APIs, Types, And Functions
Private state is `struct hv_uio_private_data`, embedding `struct uio_info`, the `hv_device`, an open refcount, receive/send buffers, GPADL descriptors, and map names. Key functions are `hv_uio_probe()`, `hv_uio_remove()`, `hv_uio_open()`, `hv_uio_release()`, `hv_uio_irqcontrol()`, `hv_uio_channel_cb()`, `hv_uio_rescind()`, `hv_uio_new_channel()`, `hv_uio_ring_mmap_prepare()`, and `hv_uio_cleanup()`.

## Control Flow And State
Probe allocates primary ring pages sized from the channel or 2 MiB default, sets channel read mode to ISR, fills UIO info with custom IRQ, open/release/irqcontrol callbacks, maps the TX/RX rings as `UIO_MEM_IOVA`, maps Hyper-V interrupt and monitor pages as logical memory, and for `HV_NIC` allocates large receive and send buffers, establishes GPADLs, and exposes them as virtual UIO maps named with GPADL handles. It registers UIO, creates ring sysfs compatibility files, and stores driver data.

Open increments a refcount; the first open installs rescind and subchannel callbacks and connects the primary ring. Release disconnects the primary ring on last close. VMBus events call `uio_event_notify()`. `irqcontrol` updates interrupt masks on the primary and all subchannels and signals the host when enabling on non-monitor channels. A rescind clears `info.irq`, notifies userspace so reads fail, and unregisters the VMBus device. Remove unregisters UIO, tears down GPADLs/buffers, removes ring sysfs, and frees rings.

## Dependencies And Integration Points
The driver depends on Hyper-V VMBus internals, UIO core, vmalloc, network device IDs for `HV_NIC`, GPADL setup/teardown, and dynamic VMBus driver IDs. It intentionally has no static ID table; userspace/admin scripts bind devices through sysfs.

## Risks And Edge Cases
The driver exposes low-level VMBus communication to userspace and can displace normal kernel drivers. Ring sysfs creation in probe is retained for compatibility despite race concerns. Buffer cleanup must respect decrypted GPADL state. Subchannel creation failures may leave only the primary channel usable. Rescind handling intentionally unregisters the device to keep VMBus offer state correct.

## Test Signals
Test dynamic ID bind/unbind, primary open/close refcounting, subchannel creation and ring sysfs mmap, UIO event delivery from primary and subchannels, irqcontrol masking/unmasking, NIC send/receive GPADL map naming and teardown, rescind behavior with blocked readers, and cleanup after partial GPADL allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_hv_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_mf624.c -->
# sources/distributed-fs/ceph-client/drivers/uio/uio_mf624.c

## Purpose
`uio_mf624.c` is a UIO PCI driver for the Humusoft MF624 data-acquisition card. It exposes the card's control/status, ADC/DAC/DIO, and counter/timer BARs to userspace and provides interrupt filtering plus userspace IRQ enable/disable control.

## Important APIs, Types, And Functions
The PCI ID table matches Humusoft MF624. `mf624_pci_probe()` enables PCI, requests regions, fills `uio_info`, maps BAR0/BAR2/BAR4 with `mf624_setup_mem()`, installs shared IRQ handler `mf624_irq_handler()`, installs `mf624_irqcontrol()`, registers UIO, and stores drvdata. `mf624_disable_interrupt()` and `mf624_enable_interrupt()` manipulate ADC, CTR4, and global PCI interrupt enable bits in BAR0 `INTCSR`.

## Control Flow And State
The IRQ handler reads `INTCSR`. If ADC interrupt is enabled and pending, it disables ADC/global interrupt and returns `IRQ_HANDLED`; if counter 4 is enabled and pending, it disables CTR4/global interrupt and returns handled; otherwise it returns `IRQ_NONE`. Userspace receives a UIO event, acknowledges hardware through mapped registers, then writes `1` to `/dev/uioN` to re-enable all supported interrupt sources or `0` to disable all. Remove disables all interrupts, unregisters UIO, releases PCI resources, disables the device, and unmaps all three BARs.

## Dependencies And Integration Points
The driver depends on PCI, UIO core, and device-specific BAR/register layout. Userspace is responsible for DAQ operation, interrupt acknowledgement, and source-specific policy using the mapped BARs.

## Risks And Edge Cases
The code trusts BAR0/BAR2/BAR4 despite a note that the datasheet's BAR description is unreliable. IRQ control only recognizes values 0 and 1 but returns success for other values without changing state. Shared IRQ filtering depends on enable and status bits being read consistently. Probe error paths return `-ENODEV` for several distinct failures.

## Test Signals
Test BAR mapping and sysfs map offsets/sizes, ADC and CTR4 interrupt filtering, userspace write-based irqcontrol, shared IRQ non-ownership, remove-time interrupt shutdown, and failure cleanup for partial BAR mapping or UIO registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_mf624.c -->
