# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/pkeys.c

Purpose: Implements PowerPC memory protection key discovery, default register policy, execute-only pkey support, KUAP/KUEP setup, and arch hooks for pkey access checks.

Important APIs and functions: `pkey_early_init_devtree()` discovers pkey support and initializes defaults. `setup_kuep()` and `setup_kuap()` program kernel user execution/access prevention. Under `CONFIG_PPC_MEM_KEYS`, hooks include `pkey_mm_init()`, `__arch_set_user_pkey_access()`, `execute_only_pkey()`, `__arch_override_mprotect_pkey()`, `arch_pte_access_permitted()`, `arch_vma_access_permitted()`, and `arch_dup_pkeys()`. Helpers parse device tree storage keys and manipulate AMR/IAMR bit fields.

Control flow: Early init rejects radix and pre-POWER7, scans CPU nodes for `ibm,processor-storage-keys`, falls back to 32 keys on known bare-metal POWER8/9 cases, clamps to arch-neutral pkey flag capacity, initializes AMR/IAMR/UAMOR defaults, reserves key 1, optionally reserves key 2 for execute-only, reserves key 3 for KUAP/KUEP, and marks unsupported keys reserved. KUAP/KUEP setup programs AMR/IAMR on each CPU and sets MMU feature bits on the boot CPU. User pkey access updates validate UAMOR permission, update current thread AMR/IAMR saved register images, and reject unsupported execute-disable requests.

State and persistence: Global boot-lifetime state includes `num_pkey`, `reserved_allocation_mask`, `initial_allocation_mask`, `default_amr`, `default_iamr`, `default_uamor`, `execute_only_key`, and `pkey_execute_disable_supported`. Per-mm state includes allocation bitmap and execute-only key. Per-thread state lives in AMR/IAMR register values.

Dependencies and integration: Integrates with device tree, CPU feature/PVR detection, firmware LPAR detection, `mprotect`, generic pkeys, VMA flags, PTE pkey bits, and kernel user protection options.

Risks: Radix does not support the same pkey mechanism, so early mode checks are important. UAMOR must prevent userspace from changing reserved keys. Execute-only behavior depends on IAMR support and key availability. Foreign VMA checks intentionally skip current-thread AMR enforcement.

Test signals: Boot with and without pkey device-tree properties, pkey_alloc/free/mprotect tests, execute-only mappings, KUAP/KUEP boot logs and access faults, fork pkey duplication, and ptrace/foreign-mm access behavior.
