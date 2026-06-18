# sources/distributed-fs/ceph-client/arch/x86/include/asm/page_64_types.h

Purpose: defines x86-64 page-size-adjacent layout constants: thread, IRQ, and exception stack sizes; IST indexes; page-offset base addresses for 4-level and 5-level paging; kernel image virtual base and size; address mask shifts; and user-space task/stack limits.

Important APIs, types, and functions: key macros are `THREAD_SIZE_ORDER`, `THREAD_SIZE`, `EXCEPTION_STACK_ORDER`, `EXCEPTION_STKSZ`, `IRQ_STACK_ORDER`, `IRQ_STACK_SIZE`, `IST_INDEX_*`, `__PAGE_OFFSET_BASE_L5`, `__PAGE_OFFSET_BASE_L4`, `__PAGE_OFFSET`, `__START_KERNEL_map`, `__PHYSICAL_MASK_SHIFT`, `__VIRTUAL_MASK_SHIFT`, `TASK_SIZE_MAX`, `DEFAULT_MAP_WINDOW`, `IA32_PAGE_OFFSET`, `TASK_SIZE_LOW`, `TASK_SIZE`, `TASK_SIZE_OF()`, `STACK_TOP*`, and `KERNEL_IMAGE_SIZE`.

Control flow: there is no runtime control flow except macro expansion. `KASAN_STACK_ORDER`, `RANDOMIZE_BASE`, `pgtable_l5_enabled()`, `TIF_ADDR32`, and process personality control the concrete values selected by users.

State and persistence: the header itself has no state. It reads `page_offset_base` through `__PAGE_OFFSET` and tests thread flags when task-size macros are used.

Dependencies and integration points: included by `page_64.h` and `page_types.h`, and indirectly by paging, entry, signal, stack, KASLR, module-layout, and compat mmap code. IST indexes must match the TSS hardware exception stack layout.

Risks: address constants must stay synchronized with `Documentation/arch/x86/x86_64/mm.rst`, PTI LDT remap space, Xen hypervisor slots, module/fixmap placement, and KASLR constraints. Stack-size changes affect interrupt/exception overflow margins and kernel memory footprint.

Test signals: boot tests with KASAN on/off, KASLR on/off, LA57 on/off, compat 32-bit tasks, and PTI; verify stack overflow tests, IST exception delivery for DF/NMI/DB/MCE/VC, module range placement, and user mappings just below task-size boundaries.
