# sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/rmi-core.c

Purpose: implements AMD SB-RMI/APML protocol operations and the userspace misc-device ioctl interface for mailbox, CPUID, MCA/MSR, and raw register transfers.

Important APIs and functions: `rmi_mailbox_xfer` is shared with hwmon. `create_misc_rmi_device` registers `/dev/sbrmi-<addr>`. Static ioctl helpers are `apml_mailbox_xfer`, `apml_cpuid_xfer`, `apml_mcamsr_xfer`, and `apml_rmi_reg_xfer`. CPUID/MSR helpers prepare protocol-specific bulk messages for revision 0x20 and extended revisions 0x21/0x31.

Control flow: ioctl dispatch copies a UAPI structure from userspace, runs the selected protocol under `data->lock`, and copies results back. Mailbox transfer writes command/data bytes to inbound registers, triggers firmware via software interrupt, polls `SBRMI_STATUS` for software alert, reads outbound data and firmware status, clears alert bits, and reports firmware errors as `-EPROTOTYPE` with `fw_ret_code`. CPUID and MCA/MSR transfers cache the RMI revision, write protocol payloads, poll hardware alert, bulk-read output, clear status, validate returned byte count/status, and update the input/output value.

State and persistence: `struct sbrmi_data` holds regmap, mutex, cached revision, max power limit, static address, and miscdevice metadata. Hardware mailbox state is transient; firmware-visible registers are cleared or overwritten per transfer.

Dependencies and integration points: depends on regmap, miscdevice, UAPI `amd-apml.h`, and transport setup from `rmi-i2c.c`. `rmi-hwmon.c` reuses mailbox commands for power telemetry.

Risks: this snapshot has missing braces after `if (ret < 0)` in CPUID error handling, causing `msg->cpu_in_out = 0` to run unconditionally. Raw register ioctl exposes arbitrary device register access to root-only misc users. Poll timeouts are fixed at two seconds and serialize all protocols through one mutex.

Test signals: ioctl ABI tests, firmware error-code propagation, timeout injection, revision 0x10/0x20/0x21/0x31 coverage, CPUID thread >127 handling, and hwmon mailbox concurrency tests.
