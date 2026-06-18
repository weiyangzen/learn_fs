# sources/distributed-fs/ceph-client/arch/x86/boot/startup/gdt_idt.c

Purpose: loads early GDT and IDT state for 64-bit startup before the normal kernel IDT is available.

Important APIs and state: defines page-aligned `bringup_idt_table`, `startup_64_load_idt(void *vc_handler)`, and `startup_64_setup_gdt_idt()`.

Control flow: `startup_64_setup_gdt_idt()` obtains a RIP-relative pointer to `gdt_page`, loads the GDT, reloads data segments, selects `vc_no_ghcb` as a #VC handler when AMD memory encryption is enabled, and calls `startup_64_load_idt()`. The IDT loader optionally initializes a #VC descriptor in the bringup table and loads it.

Dependencies and integration: called from `head_64.S` during boot CPU and secondary CPU bringup. Depends on descriptor helpers, RIP-relative access, and SEV early VC handler.

Risks and test signals: using runtime `idt_table` too early would run instrumented code or require unavailable CPU state, so this local table is essential. Test normal, SEV-ES/SNP, and secondary CPU startup paths with early #VC delivery.
