# sources/distributed-fs/ceph-client/arch/x86/kernel/machine_kexec_32.c

Purpose: Handles the 32-bit x86 machine transition for kexec and kexec-jump. It prepares minimal executable control code and page tables, then disables unsafe CPU state and jumps into the relocation routine.

Important APIs/types/functions: defines `machine_kexec_prepare()`, `machine_kexec_cleanup()`, and `machine_kexec()`. Helpers include `load_segments()`, `machine_kexec_alloc_page_tables()`, `machine_kexec_free_page_tables()`, `machine_kexec_page_table_set_one()`, and `machine_kexec_prepare_page_tables()`.

Control flow: prepare marks the control page executable, allocates a PGD plus PTEs and optional PAE PMDs, and maps the control page both at its virtual address and physical identity. Cleanup restores NX and frees page tables. Execution optionally saves processor state for kexec jump, disables ftrace, interrupts, and hardware breakpoints, may reset IOAPIC to boot IRQ mode, copies relocation code to the control page, fills `page_list` with physical control page, virtual control page, PGD, and optional swap page, reloads kernel segments, invalidates IDT/GDT, and calls the relocation code with image head, page list, entry point, PAE flag, and preserve-context flag.

State and persistence: staged page-table pointers live in `image->arch`. Control page permissions are changed for the lifetime of the image. During execution the old kernel is past the point of no return unless preserve-context jump returns.

Dependencies and integration points: depends on generic kexec image layout, x86 page table allocation, relocation assembly symbols, ftrace state save/restore, IOAPIC legacy mode, segment/GDT/IDT management, hardware breakpoint disable, and suspend processor-state helpers.

Risks: `machine_kexec()` must not allocate or fail. Page tables must map the control code exactly as relocation expects. Invalidating GDT/IDT means no normal exception handling is available after that point. Preserve-context paths must restore processor state and ftrace on return.

Test signals: 32-bit kexec tests should cover default kexec, crash/preserve-context where configured, PAE and non-PAE page tables, IOAPIC reset behavior, control page permissions before and after cleanup, and ftrace/hardware-breakpoint state restoration on kexec-jump return.
