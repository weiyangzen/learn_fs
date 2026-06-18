## sources/distributed-fs/ceph-client/arch/mips/kernel/vmlinux.lds.S

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/vmlinux.lds.S` is the MIPS kernel linker script. It defines ELF architecture, entry point, program headers, section order, ABI/debug metadata retention, special MIPS sections, relocation table space, appended DTB space, and discarded ABI metadata.

### Important APIs, Types, And Functions
Key linker symbols and sections include `OUTPUT_ARCH(mips)`, `ENTRY(kernel_entry)`, `PHDRS`, `jiffies`, `_text`, `_etext`, `EXCEPTION_TABLE(16)`, `__dbe_table`, `_sdata`, `RO_DATA`, `.data`, `_gp`, `.sdata`, `_edata`, `__init_begin`, `__init_end`, `.mips.machines.init`, `PERCPU_SECTION`, `.rel.dyn`, `.appended_dtb`, `.data.reloc`, `__appended_dtb`, `BSS_SECTION`, `_end`, `.mdebug.*`, debug sections, and `DISCARDS`.

### Control Flow
The script sets the kernel load address, lays out executable text and fixups in the text segment, emits exception tables and data-bus-error tables, places read-only data before writable data, aligns init and BSS sections, reserves optional machine descriptors, optional appended DTB and relocation table areas, emits per-CPU data when SMP is enabled, and discards MIPS ABI metadata not wanted in the final kernel image.

### State, Persistence, And Dependencies
This file determines the persistent kernel image layout and many symbols consumed at runtime. Dependencies include `asm-generic/vmlinux.lds.h`, `asm/asm-offsets.h`, `asm/thread_info.h`, Kconfig options such as `CONFIG_32BIT`, `CONFIG_BOOT_ELF64`, `CONFIG_MAPPED_KERNEL`, `CONFIG_SMP`, `CONFIG_RELOCATABLE`, and appended DTB options.

### Integration Points
Runtime code in `traps.c` consumes `__dbe_table` bounds. Early boot depends on `kernel_entry`, load address, BSS, init section bounds, and appended DTB symbols. Debuggers consume `.mdebug.abi32`, `.mdebug.abi64`, and `.mdebug`. Relocation tooling consumes `.data.reloc`.

### Risks
Section alignment changes can break page tables, per-CPU data, init freeing, or swapper page directory alignment. `_gp` placement affects small-data addressing. Program header changes can break bootloaders. Discarding or retaining ABI sections affects tooling. Appended DTB and relocation reservations must match configured sizes.

### Test Signals
Link 32-bit and 64-bit kernels, boot with and without Octeon PT_NOTE suppression, verify exception table and DBE table symbols, test relocatable kernels, appended DTB kernels, SMP per-CPU layout, BSS alignment, and debugger ABI metadata visibility.
