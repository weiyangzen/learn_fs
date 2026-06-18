
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/optprobes.c

Purpose: PowerPC optimized kprobe backend that replaces an armed breakpoint with a direct branch to a generated detour buffer when the probed instruction can be safely emulated and the branch ranges permit it.

Important APIs/types/functions: `alloc_optinsn_page`; `free_optinsn_page`; `can_optimize`; `optimized_callback`; `arch_prepare_optimized_kprobe`; `arch_optimize_kprobes`; `arch_unoptimize_kprobe`; `arch_unoptimize_kprobes`; `arch_remove_optimized_kprobe`; `arch_within_optimized_kprobe`; patch helpers for immediate loads; assembly template labels from `optprobes_head.S`.

Control flow: only one static optinsn page is exposed. Optimization rejects non-kernel addresses, module addresses, conditional branches, and instructions that `analyse_instr` cannot predict/emulate with dummy regs; the rethook trampoline is a special accepted case. Preparation allocates a detour slot, checks branch reach from probe to detour and detour back to post-emulation NIP, copies the assembly template, patches in the `optimized_kprobe` pointer, branches to `optimized_callback` and `emulate_step`, patches the original instruction immediate, and installs a return branch. Optimization later backs up the original instruction and patches the probed address to branch to the detour.

State and persistence: static `insn_page_in_use`; per-optimized-probe detour slot and copied instruction bytes; live kernel text patched from breakpoint to branch and back. No durable storage.

Dependencies and integration: integrates generic optimized kprobes, PowerPC text patching/cache flushing, `analyse_instr`, `emulate_step`, kallsyms lookup for internal helper addresses, and the fixed near-text `optinsn_slot`.

Risks: branch reach is limited to 32 MiB; module probes are not optimized; conditional branch NIP cannot be predicted; only one page of detour slots is available; disabled probes under delayed unoptimization must be ignored by callback; generated immediate-load instruction counts differ PPC32/PPC64.

Test signals: optimize probes on simple emulatable kernel instructions, reject module and conditional branch probes, fill/free optinsn slots, enable/disable delayed unoptimization, and verify post-probe NIP and pre-handler callbacks.
