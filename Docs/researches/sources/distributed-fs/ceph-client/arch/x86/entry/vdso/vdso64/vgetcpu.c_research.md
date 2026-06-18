## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vgetcpu.c

Purpose: includes common vDSO `getcpu()` for 64-bit and x32 images.

Important dependency: `#include "common/vgetcpu.c"`.

Control flow: runtime behavior reads CPU/node via `vdso_read_cpunode()` and returns zero.

State/persistence: no local state; consumes vDSO CPU/node data.

Integration points: 64-bit/x32 linker scripts, libc `getcpu`, scheduler/NUMA metadata, and vDSO mapping.

Risks: wrong symbol export or data mapping causes userspace locality errors. Test signals include x86_64/x32 getcpu tests and CPU hotplug/migration stress.
