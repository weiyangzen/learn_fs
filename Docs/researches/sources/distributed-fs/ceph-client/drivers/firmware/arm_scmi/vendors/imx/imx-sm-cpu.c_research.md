# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/vendors/imx/imx-sm-cpu.c

Purpose: This file implements the NXP i.MX SCMI CPU vendor protocol for CPU start/stop, reset vector programming, and started-state query.

Important APIs/types/functions: `struct scmi_imx_cpu_info` stores CPU count. Ops are `cpu_reset_vector_set`, `cpu_start`, and `cpu_started`. `scmi_imx_cpu_protocol_attributes_get()` reads CPU count. `scmi_imx_cpu_attributes_get()` reads and logs each CPU name. `scmi_imx_cpu_validate_cpuid()` bounds-checks CPU IDs.

Control flow: Init reads protocol attributes, logs the number of CPUs, then loops over each CPU and reads attributes. Start/stop validates the CPU ID and chooses `SCMI_IMX_CPU_START` or `SCMI_IMX_CPU_STOP`. Reset-vector set validates CPU ID, builds flags for start/boot/resume, splits the 64-bit vector, and sends the command. Started query reads CPU info and treats run modes START and SLEEP as started.

State and persistence: Runtime private state stores the CPU count. Reset vectors and CPU run modes live in platform firmware/hardware. No persistent kernel storage is used.

Dependencies and integration points: It depends on SCMI protocol handle ops, public i.MX SCMI protocol types, and vendor protocol registration. It is meant for i.MX CPU management consumers.

Risks and edge cases: `SCMI_IMX_CPU_INFO_GET` xfer is initialized with rx size 0 while the code reads `t->rx.buf`, which relies on core max-rx behavior or may be a bug; this deserves targeted testing. Init fails if reading any CPU attributes fails, making partial firmware discovery fatal. Flag assembly mixes `cpu_to_le32(0)` with ORed `le32_encode_bits()` values, which is acceptable only if endian helpers produce compatible types.

Test signals: Test CPU count parsing, CPU attribute read loop, start/stop invalid and valid IDs, reset-vector flags combinations, started query for all run modes, and response sizing for `SCMI_IMX_CPU_INFO_GET`.
