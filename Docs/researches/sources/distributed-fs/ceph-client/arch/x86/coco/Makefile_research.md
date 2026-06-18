# sources/distributed-fs/ceph-client/arch/x86/coco/Makefile

Purpose: builds common x86 confidential-computing support and conditionally includes TDX and SEV subdirectories.

Important APIs and state: removes `-pg` from `core.o`, disables KASAN for `core.o`, adds `-fno-stack-protector`, always builds `core.o`, and conditionally descends into `tdx/` and `sev/`.

Control flow: make-time only.

Dependencies and integration: controls instrumentation suitability for early/noinstr CoCo capability code and selects vendor-specific subtrees by config.

Risks and test signals: instrumentation in CoCo core could violate noinstr/early constraints. Test with profiling/sanitizer configs and both `CONFIG_INTEL_TDX_GUEST` and `CONFIG_AMD_MEM_ENCRYPT` combinations.
