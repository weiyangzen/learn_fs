# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/npu6_regs.c

Purpose: provides NPU6 static hardware information for AMD XDNA, largely reusing the NPU4-family register layout, runtime configs, DPM table, firmware features, and SMU DPM implementation.

Important data: defines NPU6 BAR indices/bases, public/MP0/MP1/SRAM addresses, `npu6_dev_priv`, and exported `dev_npu6_info`. The private table uses firmware path `amdnpu/17f0_10/`, NPU4 default runtime configs, NPU4 clock and feature tables, natural column alignment, 16 contexts, and `npu4_set_dpm()`. Device info identifies vbnv `RyzenAI-npu6` and KMQ type.

Control flow: selected for PCI device `0x17f0` revision `0x20`; common AIE2 probe/start/PM/query paths use the offsets and tables.

State and persistence: immutable device tables only.

Dependencies: NPU4 shared tables, AIE2 common ops, Linux sizes, DRM UAPI.

Risks: firmware path reuse with `17f0_10` is intentional only if NPU6 firmware packaging matches; otherwise probe firmware request fails or loads incompatible firmware. Register table copy/paste errors would break PSP/SMU/mailbox.

Test signals: revision 0x20 hardware bind, firmware request path, BAR offset validation, DPM power changes, context limit enforcement, and query metadata consistency.
