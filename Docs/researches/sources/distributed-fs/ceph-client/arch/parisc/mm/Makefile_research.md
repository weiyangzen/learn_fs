# sources/distributed-fs/ceph-client/arch/parisc/mm/Makefile

Purpose: declares the PA-RISC architecture memory-management objects built into the kernel.

Important build rules: `obj-y := init.o fault.o ioremap.o fixmap.o` always builds core initialization, page fault handling, I/O remapping, and fixmap support. `obj-$(CONFIG_HUGETLB_PAGE) += hugetlbpage.o` conditionally includes huge TLB support.

Control flow: build-system only. Kbuild expands `obj-y` and config-dependent object lists when building `arch/parisc/mm/`.

State and persistence: no runtime state. Its persistent effect is the kernel link composition for PA-RISC MM code.

Dependencies and integration: selected from the parent architecture Makefile. The included objects provide symbols consumed by trap handling, generic MM, TLB flush code, ioremap callers, fixmap users, and hugetlb core.

Risks: omitting an always-needed object would create link failures or missing runtime handlers. Accidentally making `hugetlbpage.o` unconditional could pull hugepage code into unsupported configs; making core files conditional could break boot.

Test signals: build PA-RISC defconfigs with and without `CONFIG_HUGETLB_PAGE`, verify symbols such as `do_page_fault`, `paging_init`, `ioremap_prot`, and `set_fixmap` resolve, and run sparse or allmodconfig-style coverage for conditional hugepage paths.
