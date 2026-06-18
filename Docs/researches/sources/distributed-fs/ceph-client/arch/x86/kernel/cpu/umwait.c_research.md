# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/umwait.c

## Purpose
Provides systemwide control for Intel WAITPKG `UMWAIT` behavior through `IA32_UMWAIT_CONTROL`, CPU hotplug callbacks, suspend/resume restoration, and sysfs knobs.

## Important APIs, Types, And Functions
`umwait_control_cached` stores the desired control value; `orig_umwait_control_cached` preserves BIOS/hardware state. `umwait_update_control_msr()` writes the MSR. `umwait_cpu_online()` and `umwait_cpu_offline()` program or restore CPUs. Sysfs attributes `enable_c02` and `max_time` live under `cpu/umwait_control`.

## Control Flow
`umwait_init()` exits unless `WAITPKG` is present, saves the original MSR, registers CPU hotplug state, registers syscore resume, and creates the sysfs group. Sysfs writes parse and validate input, take `umwait_lock`, update the cached control value, then call `on_each_cpu()` to propagate the MSR. Resume writes the cached value on the boot CPU; APs are handled by hotplug.

## State, Persistence, And Dependencies
State persists in cached globals and per-CPU MSR contents. Offline CPUs are restored to original MSR values. It depends on CPU hotplug, syscore suspend, CPU bus sysfs, MSR definitions, and WAITPKG capability.

## Integration Points
Exposes runtime power/latency policy to userspace and cooperates with CPU online/offline and system resume.

## Risks
Concurrent sysfs writes and CPU bring-up are race-prone; interrupts are disabled in online callback to order cached reads against IPIs. Invalid `max_time` bits return `-EINVAL`. Sysfs creation failure still leaves MSR defaults programmed.

## Test Signals
`/sys/devices/system/cpu/umwait_control/enable_c02` and `max_time` should reflect writes, reject invalid masks, and survive CPU hotplug and suspend/resume.
