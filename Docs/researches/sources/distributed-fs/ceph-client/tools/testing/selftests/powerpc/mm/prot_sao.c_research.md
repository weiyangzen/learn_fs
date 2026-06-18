<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/prot_sao.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/prot_sao.c

Purpose: Tests support for `PROT_SAO` mappings on processors that advertise Strong Access Ordering capability.

Important APIs and types: Defines `SIZE`, `test_prot_sao()`, and `main()`. Uses `mmap`, `mprotect`, `memset`, `munmap`, and `PPC_FEATURE_ARCH_2_06` style capability checks through `utils.h`.

Control flow: `test_prot_sao()` maps memory with ordinary permissions, applies SAO protection when supported, writes to the region, and validates kernel acceptance/rejection paths.

State and persistence: Only a temporary mapping is modified.

Dependencies and integration points: Depends on `<asm/cputable.h>`, powerpc SAO support, and the shared harness.

Risks: SAO is hardware/configuration-specific and may skip on many systems. The test is mostly ABI coverage for `mprotect` flag validation.

Test signals: Pass indicates `PROT_SAO` is accepted and usable where advertised, or skipped where unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/prot_sao.c -->
