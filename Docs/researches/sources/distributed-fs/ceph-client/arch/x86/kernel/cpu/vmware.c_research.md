# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/vmware.c

## Purpose
Detects VMware guests, selects hypercall transport, configures paravirtual time and steal-time accounting, and supplies encrypted-guest hypercall glue.

## Important APIs, Types, And Functions
`vmware_hypercall_slow()` implements I/O-port, `vmcall`, or `vmmcall` hypercalls. `vmware_platform()` detects CPUID/DMI VMware presence. `vmware_platform_setup()` reads TSC/bus frequencies, sets calibration hooks, and installs paravirt ops. `vmware_paravirt_ops_setup()` configures sched clock and steal clock. Optional exports include `vmware_tdx_hypercall()` and SEV-ES GHCB prepare/finish callbacks. `x86_hyper_vmware` registers the hypervisor.

## Control Flow
Detection prefers CPUID hypervisor vendor `VMwareVMware`, selecting hypercall mode from feature leaf `0x40000010`; legacy DMI falls back to port probing. Setup asks the hypervisor for frequency, overrides TSC and LAPIC calibration, handles SNP non-EFI MP table parsing, enables paravirt clock/steal-time if supported, disables IO-APIC timer checks, and forces TSC reliability caps. CPU hotplug registers per-CPU steal-time pages, and reboot disables them.

## State, Persistence, And Dependencies
Persistent state includes `vmware_tsc_khz`, `vmware_hypercall_mode`, per-CPU decrypted steal-time pages, paravirt static keys, clock conversion data, and modified x86 platform hooks. It depends on hypervisor CPUID leaves, VMware command ABI, APIC/timer code, paravirt, TDX, SEV-ES, and encrypted-memory attributes.

## Integration Points
Integrated through `hypervisor_x86`, `x86_platform` calibration hooks, `pv_info`, `pv_steal_clock`, `smp_ops`, CPU hotplug, reboot notifiers, and confidential-computing runtime hypercall callbacks.

## Risks
Incorrect detection can execute unsafe hypercalls. Steal-time registration depends on stable decrypted physical addresses. TDX and SEV-ES paths must preserve register ABI exactly. Forcing TSC reliable bypasses watchdog checks by trusting the hypervisor.

## Test Signals
VMware guests should report hypercall mode and TSC frequency, skip timer instability warnings, expose steal-time when available, handle CPU hotplug/reboot cleanly, and pass TDX/SEV-ES hypercall ABI tests where configured.
