## sources/distributed-fs/ceph-client/arch/loongarch/kernel/kprobes.c

### Purpose
`kprobes.c` implements the LoongArch architecture backend for kernel probes. It plants LoongArch breakpoint instructions at probed text addresses, prepares either out-of-line single-step slots or simulated execution for instructions that cannot safely run from the slot, and connects breakpoint, single-step, and fault handling into the generic kprobes core.

### Important APIs, Types, And Functions
The file defines per-CPU `current_kprobe` and `kprobe_ctlblk`, exports the architecture hooks `arch_prepare_kprobe`, `arch_arm_kprobe`, `arch_disarm_kprobe`, `arch_remove_kprobe`, `kprobe_breakpoint_handler`, `kprobe_singlestep_handler`, `kprobe_fault_handler`, `arch_populate_kprobe_blacklist`, `arch_init_kprobes`, and `arch_trampoline_kprobe`. It uses LoongArch break encodings `BRK_KPROBE_BP` and `BRK_KPROBE_SSTEPBP`, `union loongarch_instruction`, instruction decoder helpers such as `insns_not_supported`, `insns_need_simulation`, and `arch_simulate_insn`, plus generic kprobe helpers for probe lookup, miss accounting, and handler invocation.

### Control Flow
Probe preparation validates 4-byte alignment, snapshots the original instruction, rejects unsupported opcodes, then either allocates a two-instruction slot containing the original instruction plus a single-step breakpoint or records that the instruction will be simulated. Arming replaces the probed instruction with `KPROBE_BP_INSN` and flushes instruction cache state; disarming restores the saved opcode. On breakpoint, the handler disables preemption, looks up the probe by `csr_era`, runs the pre-handler if present, and either redirects `csr_era` to the out-of-line slot or simulates the instruction and immediately post-processes. The single-step handler recognizes the slot breakpoint, restores the saved interrupt state, invokes post-handler logic, and resets current probe state.

### State, Persistence, And Dependencies
State is strictly runtime and per-CPU: current probe pointer, previous reentered probe state, saved interrupt flags, and probe status. Kprobe text patching persists until the probe is disarmed or removed. The backend depends on LoongArch trap delivery from `traps.c`, instruction-slot allocation from the generic kprobe layer, instruction decode/simulation support, and text-cache coherency helpers. It blacklists `__irqentry_text_start..__irqentry_text_end` so interrupt entry code cannot be probed.

### Integration Points
The trap path dispatches `BRK_KPROBE_BP` and `BRK_KPROBE_SSTEPBP` to this file. Generic kprobes call the architecture prepare/arm/disarm/remove hooks, and debugfs exposes the arch blacklist. The probe path also coexists with kgdb, uprobes, and BUG breakpoints by returning `false` for breakpoints it does not own.

### Risks
Incorrect interrupt masking around single-step can accidentally single-step into interrupt handlers. Reentrant probe handling is delicate: losing previous probe state or preemption state would corrupt nested probe execution. Simulated-instruction support must stay aligned with the LoongArch decoder; unsupported branch, PC-relative, or privileged instructions need rejection or correct simulation. The arming/disarming writes directly to kernel text, so cache flushing and races with removed breakpoints are high-risk.

### Test Signals
High-signal validation includes `CONFIG_KPROBES` selftests on LoongArch, probes on normal instructions and simulated instruction classes, nested probe tests, probe removal while hit, post-handler path redirection, fault-in-single-step recovery, and boot checks that kprobes blacklist entries cover interrupt entry symbols. Runtime failures usually appear as missed probes, stuck preemption, bad `csr_era`, or unexpected breakpoint traps in `do_bp`.
