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
