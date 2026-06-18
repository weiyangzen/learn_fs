## `sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_trampoline.S`

Purpose: low-level trampoline used after Hyper-V root devirtualization. Hyper-V calls this copied low-4G code in 32-bit protected mode; it restores paging and long mode, switches to kernel page tables, and jumps to the C crash entry.

Important APIs and labels: `hv_crash_asm32`, `hv_crash_asm64`, and `hv_crash_asm_end` are consumed by `hv_crash.c`. The `HV_CRASHDATA_OFFS_*` constants define exact offsets into `struct hv_crash_tramp_data` and must match build-time checks in C.

Control flow: 32-bit entry enables PAE, loads temporary CR3, sets EFER.LME, enables paging, loads a temporary GDT, and far-jumps to a 64-bit code selector. The 64-bit entry loads the kernel CR3 and jumps indirectly to the saved C entry address.

State and persistence: no persistent state; it consumes the trampoline data block at the physical address passed in `EDI`. It temporarily changes CR0/CR3/CR4/EFER/GDT/CS during crash recovery.

Dependencies and integration points: `hv_crash.c` copies this code to a DMA32 page and builds the matching data and page tables. Uses x86 processor flag definitions and ENDBR/retpoline annotations.

Risks: no stack is available and compile/link-time addresses are invalid after copying, so only offset-based addressing is safe. Offset drift, instrumentation, stack protector, or profiling would break the path.

Test signals: root crash devirtualization reaches `hv_crash_c_entry()` and kexecs; build validates C/assembly offsets; objtool accepts intentional nonstandard control flow.
