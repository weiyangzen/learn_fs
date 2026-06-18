# sources/distributed-fs/ceph-client/arch/riscv/kernel/cpu-hotplug.c

Purpose: Supplies RISC-V CPU hotplug callbacks for bringing harts down and parking them safely.

Important APIs/types/functions: Implements `arch_cpu_idle_dead()`, `__cpu_disable()`, `cpu_die()`, and related stop/park paths using SBI HSM or platform CPU operations.

Control flow: CPU-down preparation disables interrupts, marks the CPU offline, migrates per-CPU work through generic hotplug, and asks firmware or spinwait code to stop the hart. The dying CPU enters an idle-dead path and does not return unless a platform cannot truly power it off.

State and persistence: Updates CPU online/offline masks and relies on per-hart firmware state. No persistent storage beyond kernel CPU state.

Dependencies and integration points: Depends on generic CPU hotplug, RISC-V SMP, `cpu_ops`, SBI HSM when available, IRQ state, and scheduler CPU teardown.

Risks and test signals: Hotplug races can leave interrupts targeted at offline CPUs or park a CPU with stale stack/task pointers. Test repeated online/offline cycles, CPU0 restrictions, SBI and spinwait boot modes, lockdep, and interrupt affinity after hotplug.
