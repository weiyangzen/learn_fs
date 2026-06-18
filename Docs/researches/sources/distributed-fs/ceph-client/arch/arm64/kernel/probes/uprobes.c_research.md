# sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/uprobes.c

Purpose: this is the ARM64 backend for uprobes. It copies user instructions into XOL slots, validates probed instructions, controls user single-step state, simulates unsupported-XOL instructions, and handles uretprobe return-address hijacking including GCS support.

Important APIs: `arch_uprobe_copy_ixol()` writes and cache-syncs the XOL page. `arch_uprobe_analyze_insn()` rejects AArch32 and unaligned probes, then decodes the instruction and marks simulation. `arch_uprobe_pre_xol()`, `arch_uprobe_post_xol()`, `arch_uprobe_abort_xol()`, and `arch_uprobe_skip_sstep()` manage XOL/simulation execution. `arch_uretprobe_hijack_return_addr()` replaces LR and, when GCS is enabled, updates the user guarded control stack. Breakpoint hooks are `uprobe_brk_handler()` and `uprobe_single_step_handler()`.

Control flow: registration decodes the instruction using the shared decoder. On hit, pre-XOL sets `thread.fault_code` to a sentinel, redirects PC to `utask->xol_vaddr`, and enables single step. Post-XOL asserts the XOL instruction itself did not trap, moves PC to `utask->vaddr + 4`, and disables stepping. Simulated instructions bypass XOL and invoke the selected handler at the current PC. Abort rewinds PC to the probed address.

State and dependencies: uses `current->utask`, `current->thread.fault_code`, user debug single-step controls, cache alias maintenance, highmem local mapping, and GCS helpers. Uretprobes compare LR and GCS top before replacing the return address with the trampoline to avoid creating an impossible GCS return.

Risks: no AArch32 probing is supported. XOL fault detection depends on the sentinel fault code. GCS mismatch causes the return probe to abort by returning `-1` as the original return address. Cache maintenance must run when an XOL slot changes.

Test signals: uprobes and uretprobes selftests on branch simulation, XOL faults, signal aborts, and GCS-enabled return probes. Failures include stuck single-step state, wrong PC after XOL, or SIGSEGV from invalid GCS updates.
