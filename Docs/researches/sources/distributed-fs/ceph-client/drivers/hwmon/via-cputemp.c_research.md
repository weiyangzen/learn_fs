# sources/distributed-fs/ceph-client/drivers/hwmon/via-cputemp.c

## Purpose
x86 hwmon driver exposing VIA/Centaur CPU core temperature via model-specific registers, with optional CPU VID reporting on selected C7 models.

## Important APIs, Types, and Functions
`struct via_cputemp_data` stores hwmon device, CPU id, MSR addresses, VRM, and name. `temp_show()` reads the temperature MSR on the target CPU with `rdmsr_safe_on_cpu()`. `cpu0_vid_show()` reads VID MSR and converts with `vid_from_reg()`. CPU hotplug callbacks create and remove per-CPU platform devices. `via_cputemp_init()` registers the platform driver and dynamic CPUHP state after matching supported VIA CPU IDs.

## Control Flow
Module init first checks `x86_match_cpu()`, registers a platform driver, then installs CPU hotplug callbacks. When a CPU comes online, a platform device named `via_cputemp` is allocated for that CPU id; probe chooses MSR addresses by family/model, verifies temperature MSR access, creates sysfs attributes, optionally adds `cpu0_vid`, and registers hwmon. CPU down-prep unregisters the matching platform device.

## State and Persistence
State is per-online-CPU and exists only while the CPU platform device is registered. Readings are never cached; each sysfs read performs an MSR read on the relevant CPU. The pdev list persists module-wide under a mutex to coordinate hotplug removal.

## Dependencies and Integration Points
Depends on x86 Centaur CPU IDs, CPU hotplug framework, platform devices, MSR accessors, legacy hwmon sysfs groups, and `hwmon-vid`. It integrates with hwmon through `hwmon_device_register()` and manual sysfs group creation.

## Risks
Temperature conversion assumes the low 24 bits of EAX are degrees Celsius and reports millidegrees. If MSR access fails after probe, reads return `-EAGAIN`. The code is VIA-specific and intentionally rejects unsupported models. Hotplug bookkeeping must avoid list leaks if platform device allocation/addition fails. Optional VID only appears when both model MSR and VRM detection are available.

## Test Signals
Test CPU ID matching, model-to-MSR selection, probe failure on MSR read error, CPU online/offline lifecycle, optional `cpu0_vid` creation/removal, per-core labels, module init path without hotplug CPU support, and read error propagation.
