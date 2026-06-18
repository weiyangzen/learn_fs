<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_ipcutil.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_ipcutil.c

Purpose: legacy character-device utility wrapper around the SCU IPC core. It exposes privileged ioctls for userspace to read, write, and update SCU power-controller registers through `/dev` major registration named `intel_mid_scu`.

Important APIs/types/functions: `struct scu_ipc_data` carries register count, up to five addresses, up to five data bytes, and one mask. `scu_reg_access()` dispatches ioctl commands to SCU IPC core APIs. `scu_ipc_ioctl()` enforces `CAP_SYS_RAWIO` and copies data to/from userspace. Open obtains a singleton SCU IPC device with `intel_scu_ipc_dev_get()`; release puts it.

Control flow: module init allocates a dynamic char major. Open is single-user guarded by `scu_lock` and fails with `-EBUSY` if already open or `-ENODEV` if no core device exists. Ioctl copies the full command structure, validates capability, dispatches, and copies results back. Release clears the global handle.

State/persistence: global `scu` stores the held IPC device while the char device is open; `major` stores the dynamic char major. Register writes affect SCU/PMIC hardware, not driver state.

Dependencies/integration: depends on the SCU IPC core exported APIs, Linux char device registration, user access helpers, and raw IO capability checks.

Risks: powerful raw register access is intentionally privileged. Count validation rejects 0, 3, and >4 despite arrays sized for five, matching legacy ABI expectations but surprising callers. The command constants contain a historical typo prefix `INTE_`.

Test signals: open should fail without an SCU provider and allow only one opener; ioctls should require `CAP_SYS_RAWIO`; read ioctls should update the userspace data array; invalid counts and unknown commands should return `-EINVAL` or `-ENOTTY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_ipcutil.c -->
