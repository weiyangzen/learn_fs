# sources/distributed-fs/ceph-client/arch/arm64/mm/fault.c

Purpose: implements ARM64 memory abort handling, page fault resolution, kernel fault reporting, MTE tag fault handling, GCS access checks, pkey/POE reporting, external abort notification, and MTE-aware page allocation/tag clearing.

Important APIs/types/functions: `fault_info`, ESR decode helpers, `show_pte`, `__ptep_set_access_flags_anysz`, permission/spurious/pKVM checks, `__do_kernel_fault`, `set_thread_esr`, `do_page_fault`, `do_translation_fault`, `do_alignment_fault`, `do_sea`, `do_tag_check_fault`, `do_mem_abort`, `do_sp_pc_abort`, `vma_alloc_zeroed_movable_folio`, and `tag_clear_highpages`.

Control flow: `do_mem_abort` indexes `fault_info` by FSC and calls the handler. Translation/access/permission faults enter `do_page_fault`, which rejects no-context faults, derives `vm_flags` and `FAULT_FLAG_*` from ESR, detects illegal kernel user-memory access outside uaccess routines, handles pKVM stage-2 aborts, tries the RCU VMA fault path, falls back to mmap lock, calls `handle_mm_fault`, and converts errors into SIGSEGV/SIGBUS/OOM/MCE signals. Kernel faults attempt exception-table fixup, spurious translation fault detection with AT/PAR, MTE tag recovery, EFI fixup, and finally die with decoded ESR and page table dump.

State and persistence: updates current thread fault address/code, page table access flags, TLB state, MTE tag checking mode on recovery, task signals, folio allocation flags, and page MTE-tagged state. No disk persistence.

Dependencies/integration: core MM fault handling, KASAN/KFENCE, kprobes, perf page-fault events, pkeys/POE, GCS, pKVM, EFI runtime fixups, APEI SEA, MTE, hugetlb, TLB flush helpers, and signal delivery.

Risks: ESR interpretation drives signal codes and kernel oops classification. Permission checks must distinguish PAN/user-memory misuse from normal user faults. RCU VMA fast path must unwind locks correctly on retry/completion. MTE tag recovery disables checking locally and relies on lazy handling elsewhere. pKVM stage-2 abort recovery and spurious fault detection are security-sensitive.

Test signals: user read/write/exec faults, COW and retry paths, OOM/hwpoison/SIGBUS cases, kernel uaccess fixups, illegal kernel user access, PAN translation faults, pkey faults, GCS invalid access, MTE sync tag faults, SEA/APEI, pKVM protected-memory aborts, and access-flag atomic updates on different page sizes.
