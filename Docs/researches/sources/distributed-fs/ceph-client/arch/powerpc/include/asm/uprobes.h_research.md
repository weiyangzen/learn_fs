<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uprobes.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uprobes.h

Purpose: Defines PowerPC uprobes instruction slots and per-probe arch state.

Important APIs/types/functions: `uprobe_opcode_t`, XOL slot sizes, breakpoint instruction constants, `struct arch_uprobe`, and `struct arch_uprobe_task`. Source-visible declarations include: #define _ASM_UPROBES_H; typedef u32 uprobe_opcode_t;; #define MAX_UINSN_BYTES 8; #define UPROBE_XOL_SLOT_BYTES (MAX_UINSN_BYTES); #define UPROBE_SWBP_INSN BREAKPOINT_INSTRUCTION; #define UPROBE_SWBP_INSN_SIZE 4 /* swbp insn size in bytes */; struct arch_uprobe {; union {.

Control flow: uprobes copies/analyzes the original instruction, plants a breakpoint, and executes an out-of-line slot for probed user instructions. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: per-probe decoded instruction state and per-task saved state persist while probes are armed. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/notifier.h>, #include <asm/probes.h>. Integrated with uprobes, instruction decoder, notifier chain, and breakpoint exception handling.

Risks: instruction length/prefix handling and single-step emulation must be correct or probed tasks misexecute. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 35 lines, 770 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uprobes.h -->
