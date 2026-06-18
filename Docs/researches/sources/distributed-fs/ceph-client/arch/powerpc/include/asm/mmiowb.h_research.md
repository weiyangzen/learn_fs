# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mmiowb.h

Purpose: provides PowerPC MMIO write-barrier integration for configurations using `CONFIG_MMIOWB`.

Important APIs/types/functions: `arch_mmiowb_state()` returns `&local_paca->mmiowb_state`, and `mmiowb()` maps to the full memory barrier `mb()`. The generic `mmiowb` header is included for common behavior.

Control flow: drivers or locking paths that need ordered MMIO writes invoke `mmiowb()`, which enforces ordering with a full barrier.

State and persistence: per-CPU MMIO write-barrier state lives in PACA; this header exposes its address but does not mutate it directly.

Dependencies and integration points: depends on compiler attributes, barrier primitives, PACA, and generic MMIO write-barrier infrastructure.

Risks: insufficient barriers can reorder device writes across locks; overly strong barriers can affect performance. PACA state is only available in appropriate kernel contexts.

Test signals: device-driver MMIO ordering tests, lock/unlock paths with MMIO writes, and build coverage with and without `CONFIG_MMIOWB`.
