# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/npu1_regs.c

Purpose: provides NPU1-specific AMD XDNA register offsets, firmware path/features, runtime config defaults, DPM clock table, hardware op selection, and exported `dev_npu1_info`.

Important data: defines NPU1 BAR indices/bases for register, mailbox, PSP, SMU, and SRAM apertures; maps SRAM firmware-alive and mailbox offsets; maps PSP scratch/interrupt/wait-mode registers; maps SMU scratch/interrupt registers. `npu1_default_rt_cfg` enables PDI app load mode, debug BO, and clock gating. `npu1_dpm_clk_table` lists MP-NPU/H clock pairs. Firmware feature table gates NPU command support by protocol version. `npu1_dev_priv` selects `npu1_set_dpm()`, no natural column alignment, six hardware contexts, and firmware path `amdnpu/1502_00/`.

Control flow: PCI probe selects this table for device `0x1502` revision `0x0`; AIE2 init consumes the BAR and private tables for PSP/SMU/mailbox/runtime configuration.

State and persistence: all data is const except runtime state stored elsewhere. Firmware path drives module firmware lookup.

Dependencies: AIE2 shared header, mailbox, DRM UAPI device type, Linux sizes.

Risks: one wrong offset prevents PSP, SMU, or management mailbox startup. Context limit and column alignment must match hardware/firmware constraints.

Test signals: probe NPU1 hardware, firmware protocol 5.7/5.8+ feature behavior, DPM table programming, runtime config application, sysfs vbnv/device type, and management channel SRAM offset validation.
