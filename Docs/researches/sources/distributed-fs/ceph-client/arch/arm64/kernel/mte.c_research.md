# sources/distributed-fs/ceph-client/arch/arm64/kernel/mte.c

Purpose: Implements arm64 Memory Tagging Extension support for page tag initialization, kernel/user tag checking modes, thread switching, prctl controls, ptrace tag access, suspend/resume, and sysfs CPU preferences.

Important APIs and state: per-CPU `mte_tcf_preferred` controls preferred user tag check mode. `mte_async_or_asymm_mode` is a static key for KASAN HW tags. Entry points include `mte_sync_tags()`, `memcmp_pages()`, kernel enable helpers, `mte_check_tfsr_el1()`, `mte_thread_init_user()`, `mte_thread_switch()`, `mte_cpu_setup()`, suspend hooks, `set_mte_ctrl()`, `get_mte_ctrl()`, `mte_ptrace_copy_tags()`, and `mte_probe_user_range()`.

Control flow: page mapping calls clear tags once and mark pages/hugetlb folios tagged before publishing PTEs. Thread switch resolves requested TCF modes against per-CPU preference, updates `SCTLR_EL1` user fields and `GCR_EL1`, clears TCO state, and reports pending async faults when needed. `set_mte_ctrl()` converts prctl bits into thread state and updates current CPU immediately. Ptrace tag access validates ptrace permission, walks remote pages, requires `VM_MTE`, and copies tag granules to or from user iovecs.

Dependencies and integration: integrates with page table mapping, KASAN HW tags, scheduler context switch, prctl ABI, ptrace ABI, hugetlb, swap/KSM comparison, CPU sysfs devices, and suspend resume.

Risks and test signals: risks include publishing PTEs before tags are visible, merging tagged pages in KSM, async fault loss, wrong per-CPU preferred mode, ptrace permission bugs, tag copy partial-progress handling, and suspend losing MAIR/GCR/RGSR state. Test with MTE selftests, KASAN HW tags sync/async/asymm/store-only, ptrace tag copy, hugetlb MTE, KSM, CPU hotplug/suspend, and sysfs preference changes.
