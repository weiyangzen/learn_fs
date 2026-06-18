# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/npu4_regs.c

Purpose: provides NPU4-specific AMD XDNA register map and static hardware information, plus shared NPU4-family runtime config, DPM table, and firmware feature table used by later devices.

Important data: defines NPU4 public, MP0, MP1, SRAM mailbox, and aperture addresses; BAR indices/bases; `npu4_default_rt_cfg` for PDI app load, debug buffer, optional preemption, multiple clock-gating controls, force preempt, and frame-boundary preempt; `npu4_dpm_clk_table`; and `npu4_fw_feature_table` enabling NPU command, preemption, temporal-only, app-health, and all features by firmware major/minor. `npu4_dev_priv` selects natural column alignment, 16 contexts, NPU4 firmware path, SMU/PSP/SRAM offsets, and `npu4_set_dpm()`.

Control flow: selected for PCI device `0x17f0` revision `0x10`. AIE2 startup uses these offsets to map registers, start PSP/SMU, find firmware management channel info, and apply runtime configs based on feature mask.

State and persistence: const tables only; live state is in `amdxdna_dev_hdl`.

Dependencies: shared AIE2 ops, NPU4 SMU implementation, runtime config categories and feature bits.

Risks: feature table controls preemption/app-health availability and must match firmware protocol. Shared tables are reused by NPU5/NPU6, so changes affect multiple revisions.

Test signals: NPU4 probe, firmware major 6 minor boundary cases and major 7 all-feature path, preemption set/get, DPM/TOPS values, and BAR offset smoke tests.
