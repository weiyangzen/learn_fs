# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mman.h

Purpose: adds PowerPC architecture-specific mmap protection validation and VM flag calculation for SAO and memory protection keys.

Important APIs/types/functions: on PPC64 non-vDSO builds, `arch_calc_vm_prot_bits(prot, pkey)` maps `PROT_SAO` to `VM_SAO` and pkeys to VM flags; `arch_validate_prot(prot, addr)` rejects unknown bits and validates `PROT_SAO` against CPU SAO support and LPAR policy.

Control flow: mmap/mprotect paths call validation before installing VMA protections and call flag calculation when building `vm_flags`.

State and persistence: no state is stored. VMA flags persist in `vm_area_struct` after calculation.

Dependencies and integration points: includes UAPI mman, CPU feature checks, firmware features, mm, and pkeys. Integrates PowerPC-specific memory ordering attributes with generic mmap.

Risks: accepting unsupported `PROT_SAO` can create mappings with invalid semantics; rejecting valid pkey or SAO combinations can break userspace ABI. vDSO builds intentionally skip these helpers.

Test signals: mmap/mprotect tests for SAO on supported/unsupported CPUs, LPAR configurations with and without `CONFIG_PPC_PROT_SAO_LPAR`, pkeys selftests, and vDSO build checks.
