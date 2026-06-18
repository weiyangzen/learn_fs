<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/set_memory.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/set_memory.h

Purpose: Declares RISC-V runtime page-permission and direct-map attribute APIs.

Important APIs/types/functions: Includes `set_memory_ro/rw/x/nx/rw_nx()`, `set_kernel_memory()`, direct-map validity helpers, `kernel_page_present()`, `SECTION_ALIGN`, and PE/COFF alignment constants.

Control flow: Enabled MMU builds route permission changes to implementation code; non-MMU builds return success no-ops. `set_kernel_memory()` computes page ranges from start/end pointers.

State and persistence: Persistent effects are PTE permission changes for kernel text/modules/BPF/direct-map pages.

Dependencies and integration points: Used by module loader, alternatives/text patching, strict kernel RWX, hibernation, BPF JIT, and memory hotplug/debug code.

Risks: Incorrect permission transitions expose writable executable memory or make live code/data inaccessible.

Test signals: STRICT_KERNEL_RWX, module load/unload, BPF JIT, ftrace/kprobe patching, hibernation, and debug page-present checks.

Source read size: 63 lines, 2049 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/set_memory.h -->
