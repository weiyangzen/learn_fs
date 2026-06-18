## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/common/vgetcpu.c

Purpose: common vDSO implementation of `getcpu()` for fast userspace CPU/node lookup.

Important APIs/functions: `__vdso_getcpu(unsigned *cpu, unsigned *node, void *unused)` and weak alias `getcpu`. It calls `vdso_read_cpunode()`.

Control flow: the function reads CPU/node values from the vDSO processor data mechanism and returns zero. It ignores the legacy cache argument.

State/persistence: no local persistent state; it consumes kernel-maintained per-task/per-CPU data exposed through vDSO mechanisms.

Integration points: vDSO linker scripts, libc `getcpu`, scheduler CPU/node metadata, and `vdso/processor.h`.

Risks: stale or incorrectly mapped CPU/node data leads to wrong userspace locality decisions. ABI signature must remain stable. Test signals include vDSO getcpu selftests, CPU hotplug/migration stress, NUMA node validation, and symbol-version checks.
