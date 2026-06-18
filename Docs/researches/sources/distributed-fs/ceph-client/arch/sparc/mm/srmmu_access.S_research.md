# sources/distributed-fs/ceph-client/arch/sparc/mm/srmmu_access.S

Purpose: provides small assembly accessors for SRMMU control registers that can be runtime-patched between Sun SRMMU and LEON ASI encodings.

Important APIs/functions: defines `srmmu_get_mmureg()`, `srmmu_set_mmureg()`, `srmmu_set_ctable_ptr()`, `srmmu_set_context()`, `srmmu_get_context()`, `srmmu_get_fstatus()`, and `srmmu_get_faddr()`. The `LEON_PI` and `SUN_PI_` macros select the actual load/store ASI instruction sequence.

Control flow: each function performs a single MMU register load or store and returns through `retl`. `srmmu_set_ctable_ptr()` shifts and masks the physical context-table pointer before writing `SRMMU_CTXTBL_PTR`; context and fault accessors use the corresponding SRMMU register offsets.

State and persistence: this file does not own memory state; it reads and mutates CPU MMU registers. Effects persist only in hardware state until the next register write or reset.

Dependencies and integration points: used heavily by `srmmu.c`, trap/fault handling, and CPU-specific setup code. It depends on `pgtsrmmu.h`, `asi.h`, and the LEON one-instruction patch mechanism.

Risks: wrong ASI patching makes every MMU control access hit the wrong register space. Context-table pointer shifting must match SRMMU encoding. These routines are tiny but central to boot and fault handling.

Test signals: boot both LEON and non-LEON SRMMU kernels, confirm context switching, fault status reporting, and context-table installation work, and verify runtime patch sections are applied before normal MMU use.
