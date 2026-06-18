<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/uprobes.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/uprobes.c

## Purpose
Implements SPARC architecture support for Linux uprobes, including breakpoint address selection, out-of-line instruction copying, single-step preparation and completion, trap notification handling, and uretprobe return-address hijacking.

## Important APIs, Types, And Functions
Important entry points include `uprobe_get_swbp_addr`, `arch_uprobe_copy_ixol`, `arch_uprobe_analyze_insn`, `arch_uprobe_skip_sstep`, `arch_uprobe_pre_xol`, `arch_uprobe_post_xol`, `uprobe_trap`, `arch_uprobe_exception_notify`, `arch_uprobe_abort_xol`, `arch_uprobe_xol_was_trapped`, and `arch_uretprobe_hijack_return_addr`. Helpers include `copy_to_page`, `relbranch_fixup`, and `retpc_fixup`.

## Control Flow
Probe setup copies the original instruction into the XOL slot and appends the single-step trap, clearing branch annul bits when necessary. Pre-XOL saves TPC/TNPC and redirects execution to the XOL slot. Post-XOL reconstructs the real next PC for relative branches and fixes return-PC writes for `call` and `jmpl`. Trap `0x173` triggers breakpoint notification, trap `0x174` triggers single-step notification, and only user-mode traps are accepted.

## State And Persistence
Per-task uprobe state stores saved PCs and XOL addresses. The XOL page is modified with the copied instruction and step trap. `pt_regs` TPC/TNPC and return-register slots are updated during pre/post handling.

## Dependencies And Integration Points
Connected to `ttable_64.S` uprobe trap vectors, Linux generic uprobe core, die notifier chain, highmem page mapping, cache-flush expectations for executable copied instructions, and SPARC register-window handling via `flushw_all` for hard `jmpl` cases.

## Risks And Edge Cases
Branch annul handling is essential so the single-step trap is reached. `retpc_fixup` must write either `%o7`/integer registers or stack-resident locals with correct 32/64-bit stack layout. Kernel-mode probes are rejected because uprobe breakpoints should never exist in kernel code.

## Test Signals
Signals include uprobes on NOP, call, branch, and jmpl instructions; uretprobe return hijacking; 32-bit and 64-bit user stack layouts; breakpoint and single-step die notifications; and aborted XOL execution resetting the instruction pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/uprobes.c -->
