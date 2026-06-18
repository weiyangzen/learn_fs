# sources/distributed-fs/ceph-client/arch/s390/include/asm/perf_event.h

Purpose: This header provides s390 perf-event definitions for CPU measurement facilities, sample register setup, and architecture-specific perf callbacks.

Important APIs/types/functions: `PMU_F_*` state/error flags, `cpumf_cf_event_group()`, `cpumf_events_sysfs_show()`, event attribute macros, `perf_arch_instruction_pointer()`, `perf_arch_misc_flags()`, `perf_arch_bpf_user_pt_regs`, `struct perf_sf_sde_regs`, and `perf_arch_fetch_caller_regs()` are provided.

Control flow: Perf PMU code exposes counter facility events via sysfs, records instruction pointer/misc flags from pt_regs, and can synthesize caller regs with current frame pointer for sampling.

State and persistence: Persistent state is perf PMU/event state and sysfs attributes; the header defines flags and helpers, not storage.

Dependencies and integration points: It depends on Linux perf events, devices, s390 stacktrace frame layout, and ptrace register formats. It also integrates with PAI and CPU measurement facility drivers.

Risks and test signals: Incorrect sample flags can misclassify guest/user/kernel samples. Tests should include perf list/sysfs events, CPU counter sampling, BPF perf regs access, guest sample indicators, and callchain capture.
