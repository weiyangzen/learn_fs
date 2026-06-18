<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/vgetcpu.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/vdso/vgetcpu.c

### Purpose
`vgetcpu.c` provides the LoongArch vDSO fast path for `getcpu()`.

### Important APIs, Types, And Functions
Functions are `read_cpu_id()` and `__vdso_getcpu(unsigned int *cpu, unsigned int *node, void *unused)`.

### Control Flow
`read_cpu_id()` uses `rdtime.d` on 64-bit or `rdtimel.w` on 32-bit with `$zero` time output to read the CPU id. `__vdso_getcpu()` writes the CPU id if `cpu` is non-null and writes the node from `vdso_u_arch_data.pdata[cpu_id].node` if `node` is non-null.

### State, Persistence, And Dependencies
State is read from hardware and the vDSO architecture data page. Dependencies include LoongArch time/CPU-id instruction semantics and `vdso_u_arch_data`.

### Integration Points
Exported by `vdso.lds.S` as `__vdso_getcpu` for libc/userspace.

### Risks
CPU id must index a valid vDSO pdata entry. Migration during the call can return a CPU/node pair that is momentarily stale, which is normal for getcpu-style fast paths but must stay within ABI expectations.

### Test Signals
Run `getcpu()` userspace tests under CPU migration, CPU hotplug, and NUMA systems; compare syscall fallback values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/vgetcpu.c -->
