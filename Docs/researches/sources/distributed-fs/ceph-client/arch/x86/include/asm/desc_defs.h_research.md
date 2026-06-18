
# sources/distributed-fs/ceph-client/arch/x86/include/asm/desc_defs.h

Purpose: x86 segment, system, and interrupt descriptor bit layouts shared by C and assembly.

Important APIs and control flow: defines low-level descriptor flags, high-level data/code/TSS constants, `struct desc_struct`, `GDT_ENTRY_INIT`, gate type enums, `struct ldttss_desc`, `struct idt_bits`, `struct idt_data`, `struct gate_struct`, `struct desc_ptr`, and access-right bit masks. `gate_offset()` and `gate_segment()` decode gate fields outside setup builds.

State, dependencies, and risks: no runtime state; structures are ABI contracts for CPU descriptor tables and assembly offsets. Dependencies include x86 hardware descriptor formats and `CONFIG_X86_64`. Risks include packed bitfield layout assumptions, incorrect high/low offset handling, and changing values consumed by assembly or hardware. Test signals are boot descriptor setup, IDT/GDT inspection, modify_ldt, and compile-time layout checks.
