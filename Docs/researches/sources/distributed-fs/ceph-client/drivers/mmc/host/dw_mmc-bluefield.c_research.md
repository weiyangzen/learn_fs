# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-bluefield.c

Purpose: provides Mellanox/NVIDIA BlueField-specific glue for the Synopsys DesignWare MMC controller. It supplies fixed sample/drive phase programming and a firmware-mediated eMMC reset hook to the shared DW MMC platform wrapper.

Important APIs and functions: `dw_mci_bluefield_set_ios` programs `UHS_REG_EXT` sample and drive fields. `dw_mci_bluefield_hw_reset` invokes ARM SMCCC SMC `BLUEFIELD_SMC_SET_EMMC_RST_N`. `dw_mci_bluefield_probe` calls `dw_mci_pltfm_register` with `bluefield_drv_data`.

Control flow: platform matching on `mellanox,bluefield-dw-mshc` selects `bluefield_drv_data`. During shared DW `set_ios`, the BlueField hook overwrites sample and drive fields with constants. During MMC hardware reset, the shared core delegates to the BlueField hook, which asks firmware to toggle RST_N and logs failure if the SMC result is nonzero.

State and persistence: no driver-private state is allocated. Register phase settings persist only in controller registers while powered, and reset behavior is delegated to secure firmware.

Dependencies and integration points: depends on `dw_mmc.h`, `dw_mmc-pltfm.h`, platform devices, OF matching, PM ops from the shared DW core, and ARM SMCCC firmware availability.

Risks: phase values are fixed rather than board- or timing-specific. Reset success depends on firmware implementing the SMC ABI. The reset function has unusual extra indentation but no functional effect. There is no runtime PM wrapper beyond the shared DW ops.

Test signals: BlueField DT probe, phase-register inspection after `set_ios`, eMMC hardware reset testing through MMC core, SMC return-code logging, and shared DW transfer tests.
