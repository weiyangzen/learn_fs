## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/vgetcpu.c

Purpose: includes the common vDSO `getcpu()` implementation for the 32-bit image.

Important dependency: `#include "common/vgetcpu.c"` provides `__vdso_getcpu` and weak `getcpu`.

Control flow: runtime behavior is the common implementation: read CPU/node and return zero.

State/persistence: no local state; uses shared vDSO CPU/node data.

Integration points: vdso32 linker script, libc `getcpu`, scheduler/NUMA data, and fake 32-bit build configuration.

Risks: ABI signature must match 32-bit callers. Test signals include 32-bit getcpu selftests and CPU migration/NUMA checks.
