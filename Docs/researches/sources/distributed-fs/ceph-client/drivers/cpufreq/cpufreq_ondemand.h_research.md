# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_ondemand.h

Purpose: declares ondemand-specific policy state, tuners, and default I/O-busy selection helper layered on top of the shared DBS governor infrastructure.

Important APIs and control flow: `struct od_policy_dbs_info` embeds `policy_dbs_info` and adds low/high frequency delay fields plus `sample_type` for normal versus sub-sample operation. `to_dbs_info()` converts common policy data to ondemand data. `struct od_dbs_tuners` stores `powersave_bias`. `od_should_io_be_busy()` chooses the initial `io_is_busy` default, returning true on Intel x86 Family 6+ and false elsewhere.

State and persistence behavior: this header owns no standalone runtime state but defines the layout allocated by `od_alloc()` and accessed by `cpufreq_ondemand.c`. The `sample_type` bit and delay fields persist between DBS work invocations to implement powersave-bias frequency alternation.

Dependencies and integration points: depends on `cpufreq_governor.h` and, for x86 builds, CPU vendor/model helpers from `asm/cpu_device_id.h`. It provides the structure contract used by ondemand's sysfs and update paths.

Risks and test signals: risks include `container_of()` layout coupling, x86 default I/O-busy policy being a broad heuristic, and non-x86 platforms requiring userspace to opt into I/O-busy accounting if desired. Test signals include correct allocation size, bias sub-sample state preserved across updates, default `io_is_busy` value on Intel x86 versus ARM/other platforms, and no build issues with or without `CONFIG_X86`.
