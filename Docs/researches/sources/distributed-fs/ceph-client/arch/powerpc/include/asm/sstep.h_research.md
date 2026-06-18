<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/sstep.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/sstep.h

Purpose: Declares PowerPC instruction single-step analysis and emulation metadata.

Important APIs/types/functions: instruction-type enum, flag bits, `struct instruction_op`, register-name helpers, `analyse_instr()`, `emulate_step()`, and related emulate helpers. Source-visible declarations include: struct pt_regs;; #define IS_MTMSRD(instr) ((ppc_inst_val(instr) & 0xfc0007be) == 0x7c000124); #define IS_RFID(instr) ((ppc_inst_val(instr) & 0xfc0007be) == 0x4c000024); enum instruction_type {; #define INSTR_TYPE_MASK 0x1f; #define OP_IS_LOAD(type) ((LOAD <= (type) && (type) <= LOAD_VSX) || (type) == LARX); #define OP_IS_STORE(type) ((STORE <= (type) && (type) <= STORE_VSX) || (type) == STCX); #define OP_IS_LOAD_STORE(type) (LOAD <= (type) && (type) <= STCX).

Control flow: debug/kprobe/single-step code decodes one instruction, classifies memory/control effects, and emulates or advances registers. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: transient operation descriptions and pt_regs mutations are caller-owned. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/inst.h>. Integrated with kprobes, uprobes, xmon, ptrace single-step, and `lib/sstep.c` tests.

Risks: decoder coverage is large and ABI-sensitive; wrong classification can corrupt registers or skip faults. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 176 lines, 4713 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/sstep.h -->
