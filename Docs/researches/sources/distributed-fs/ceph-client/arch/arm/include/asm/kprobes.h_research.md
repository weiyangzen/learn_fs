# sources/distributed-fs/ceph-client/arch/arm/include/asm/kprobes.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/kprobes.h` declares ARM kprobe instruction
slots, per-probe architecture data, and breakpoint helpers. It is part of the ARM kernel-
architecture compatibility layer imported in the Ceph client source tree, so its direct consumers
are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol
logic.

### Important APIs, Types, And Functions
macros: `_ARM_KPROBES_H`, `__ARCH_WANT_KPROBES_INSN_SLOT`, `MAX_INSN_SIZE`, `flush_insn_slot`,
`kretprobe_blacklist_size`, `arch_specific_insn`, `MAX_OPTIMIZED_LENGTH`, `MAX_OPTINSN_SIZE`,
`RELATIVEJUMP_SIZE`, `MAX_COPIED_INSN`; types: `kprobe`, `prev_kprobe`, `kprobe_ctlblk`,
`arch_optimized_insn`, `kprobe_opcode_t`; functions/prototypes: `arch_remove_kprobe`,
`kprobe_fault_handler`. The file is 78 lines / 2150 bytes, and the exported surface is primarily an
include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
Caller-visible state is represented by `kprobe`, `prev_kprobe`, `kprobe_ctlblk`,
`arch_optimized_insn`, `kprobe_opcode_t`. There is no userspace filesystem persistence in this file;
persistence is either kernel memory, CPU register state, hardware register state, or generated ABI
values. Direct includes are `asm-generic/kprobes.h`, `linux/types.h`, `linux/ptrace.h`,
`linux/notifier.h`, `asm/probes.h`. It integrates with generic Linux ARM architecture code through
include-time contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `kprobes.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
