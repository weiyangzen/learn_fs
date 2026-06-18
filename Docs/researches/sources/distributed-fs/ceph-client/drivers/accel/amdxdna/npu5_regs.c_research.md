# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/npu5_regs.c

Purpose: provides NPU5 PCI-revision static device information by reusing NPU4-family runtime configuration, DPM clocks, firmware features, register layout pattern, and hardware ops with an NPU5 firmware path and exported `dev_npu5_info`.

Important data: defines NPU5 BAR indices/bases and public/MP0/MP1/SRAM register addresses mirroring NPU4-family layout. `npu5_dev_priv` uses `amdnpu/17f0_11/`, `npu4_default_rt_cfg`, `npu4_dpm_clk_table`, `npu4_fw_feature_table`, natural column alignment, 16 context limit, and `npu4_set_dpm()`. `dev_npu5_info` exposes vbnv `RyzenAI-npu5`, KMQ device type, 64 MiB device memory, and AIE2 ops.

Control flow: PCI probe selects this table for device `0x17f0` revision `0x11`. The common AIE2 path consumes it exactly like NPU4.

State and persistence: static const data only.

Dependencies: shared NPU4 tables exported from `npu4_regs.c`, AIE2 common code, and SMU/PSP offset enums.

Risks: because it reuses NPU4 tables, any NPU5-specific firmware/runtime difference must be represented here or in shared tables before enabling. Firmware path mismatch would fail firmware request.

Test signals: probe revision 0x11, firmware loading from `17f0_11`, management mailbox startup, DPM operations through NPU4 SMU commands, and sysfs vbnv/device type.
