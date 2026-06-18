# sources/distributed-fs/ceph-client/drivers/ptp/ptp_vmw.c

Purpose: implements a read-only PTP hardware clock for VMware's ACPI-advertised precision clock virtual device. It exposes the guest-visible VMware precision clock as a Linux `ptp_clock` named `ptp_vmw`, allowing time consumers to read a hypervisor supplied nanosecond counter.

Important APIs/types/functions: `ptp_vmw_pclk_read()` issues `vmware_hypercall3(VMWARE_CMD_PCLK_GETTIME)` and assembles a 64-bit nanosecond value from high/low words. `ptp_vmw_gettime()` converts that value with `ns_to_timespec64()`. The `ptp_clock_info` table implements only `.gettime64`; `.adjtime`, `.adjfine`, `.settime64`, and `.enable` all return `-EOPNOTSUPP`. `ptp_vmw_acpi_probe()` registers the PTP clock and the ACPI match table binds `VMW0005`.

Control flow: module init refuses to load unless `x86_hyper_type` reports VMware, then registers a platform driver. ACPI/platform probing registers the PTP clock and stores the ACPI companion pointer. Runtime reads go directly through the VMware hypercall. Removal unregisters the PTP clock; module exit unregisters the platform driver.

State and persistence: state is limited to two module globals, the ACPI device pointer and registered `ptp_clock`. There is no persistent configuration, no clock adjustment state, and no suspend/resume handling in this file.

Dependencies and integration: depends on x86 VMware hypervisor detection, VMware hypercall ABI, ACPI platform matching, and the PTP clock framework. It integrates as a virtual device, not as Ceph/distributed-storage logic despite its source-tree location.

Risks and test signals: the driver trusts the hypervisor command ABI and maps any nonzero hypercall return to `-EIO`. It cannot discipline or set time, so consumers must tolerate read-only PTP behavior. Test signals are VMware guest boot with `VMW0005`, `/dev/ptp*` registration, successful `PTP_CLOCK_GETTIME`, graceful absence on non-VMware hosts, and unregister behavior on device removal.
