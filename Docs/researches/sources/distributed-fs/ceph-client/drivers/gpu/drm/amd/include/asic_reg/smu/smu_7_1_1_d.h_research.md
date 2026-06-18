# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smu/smu_7_1_1_d.h

### Purpose
`smu_7_1_1_d.h` is the generated register-address contract for the AMD SMU 7.1.1 block used by the VI/Iceland GPU path. It exports numeric `#define` constants for direct MMIO registers (`mm...`) and indirect SMC/SMU register addresses (`ix...`) so driver code can address clocks, power management, firmware scratch/status, thermal sensors, GPIO pads, ROM access, fuses, DPM tables, and memory-controller tables without embedding raw literals.

### Important APIs, Types, And Functions
This header defines no functions or C types; its API surface is 1099 preprocessor constants protected by `SMU_7_1_1_D_H`. Important register families include `mmSMC_IND_INDEX_*`/`mmSMC_IND_DATA_*` and `mmSMU_IND_INDEX_*`/`mmSMU_IND_DATA_*` indirect windows, `mmSMC_MESSAGE_*`, `mmSMC_RESP_*`, and `mmSMC_MSG_ARG_*` firmware mailbox registers, `ixCG_*` clock and thermal registers, `ixSMU_*` firmware/status/input registers, `ixMCARB_DRAM_TIMING_TABLE_*`, `ixMC_REGISTERS_TABLE_*`, `ixDPM_TABLE_*`, `ixSOFT_REGISTERS_TABLE_*`, `ixPM_FUSES_*`, `ixSMU_PM_STATUS_*`, `ixPWR_*` and `ixSCLK_*` power controls, `ixLCAC_*` leakage/CAC controls, and `ixROM_*`/`ixROM_SW_DATA_*` ROM access registers.

### Control Flow
There is no executable control flow in this file. Runtime flow is created by include sites that pass these constants to register helpers. In this tree, `amdgpu/vi.c` includes the file and uses constants such as `mmSMC_IND_INDEX_11`, `mmSMC_IND_DATA_11`, `mmSMC_IND_INDEX_4`, `mmSMC_IND_DATA_4`, `ixCGTT_ROM_CLK_CTRL0`, `ixROM_INDEX`, and `ixROM_DATA` for SMU-indirect and ROM access. `pm/powerplay/smumgr/iceland_smumgr.c` includes it and uses `SMC_IND` access plus `FIRMWARE_FLAGS`, `mmSMC_IND_INDEX_0`, `mmSMC_IND_DATA_0`, and `SMC_IND_ACCESS_CNTL` to wait on firmware state and transfer data through auto-incrementing indirect registers.

### State, Persistence, And Dependencies
The header has no in-memory state and persists nothing by itself. It describes persistent hardware state: writes to mailbox, DPM, thermal, ROM, fuse, and power registers can affect SMU firmware behavior and device power/clock state until hardware, firmware, or driver code changes it. It depends on companion generated mask headers, especially `smu_7_1_1_sh_mask.h`, for field masks and shifts used with these addresses. Consumers also depend on AMDGPU/PowerPlay register access helpers such as `RREG32`, `WREG32`, `WREG32_NO_KIQ`, `cgs_write_register`, `PHM_WRITE_FIELD`, and indirect-field wait macros.

### Integration Points
The file is part of the ASIC register include set under `include/asic_reg/smu`, alongside SMU 7.1.0, 7.1.2, 7.1.3, and 8.0 variants. It is selected by the VI/Iceland code paths where the register layout differs from neighboring ASICs. The SMC mailbox definitions integrate with PowerPlay firmware command paths, the indirect-window definitions integrate with ROM and firmware memory access paths, and the DPM/PM/thermal register tables provide the numeric base for higher-level SMU manager policy code.

### Risks
The main risk is numeric drift from the hardware specification: a wrong address can write an unrelated hardware register, break firmware handshakes, misread thermal/power state, or corrupt ROM/SMC indirect accesses. Several address families are dense sequential tables, so off-by-one generation errors are plausible and hard to catch by review. Similar macro names across ASIC versions make wrong-header inclusion dangerous. The duplicate indirect aliases, including indexed `mmSMC_IND_INDEX_*` and block-prefixed aliases, require consumers to choose the window expected by the hardware sequence. Direct writes to DPM, PM, thermal, fuse, and ROM control registers are high impact and should remain behind established driver helpers.

### Test Signals
Useful signals are compile coverage of `vi.c` and `iceland_smumgr.c`, boot/probe on an Iceland/SMU 7.1.1 GPU, successful SMU firmware load and response polling, ROM reads through `vi.c`, PowerPlay DPM table programming, thermal/fan telemetry sanity, suspend/resume with power-gating state intact, and register-trace comparison against known-good SMU 7.1.1 hardware documentation. Static checks should ensure this header is paired with `smu_7_1_1_sh_mask.h` and not substituted with adjacent SMU 7.1.x variants.
