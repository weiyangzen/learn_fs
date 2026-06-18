# sources/distributed-fs/ceph-client/drivers/cpuidle/coupled.c

Purpose: provides the generic coordination engine for coupled CPU idle states, where multiple CPUs must enter a shared low-power state together because of cluster, cache, interrupt-controller, or hardware sequencing constraints.

Important APIs and functions: exported/visible helpers include `cpuidle_coupled_parallel_barrier()`, `cpuidle_state_is_coupled()`, `cpuidle_coupled_state_verify()`, `cpuidle_enter_state_coupled()`, `cpuidle_coupled_register_device()`, and `cpuidle_coupled_unregister_device()`. Internal helpers maintain combined waiting/ready counts, requested state per CPU, poke IPIs through per-CPU `call_single_data_t`, and hotplug prevent/allow transitions.

Control flow and state: each `struct cpuidle_coupled` tracks the coupled CPU mask, requested state array, atomic combined ready/waiting counts, abort barrier, online count, refcount, and prevent flag. Entry has a waiting phase where CPUs use the safe state until all are waiting, a ready phase where all CPUs commit to enter, a pending-poke abort check to avoid lost interrupts, then a simultaneous call into the deepest mutually requested state. CPU hotplug callbacks prevent coupled entry while online masks change and update `online_count`.

Dependencies and integration points: depends on `cpuidle_device.coupled_cpus`, `safe_state_index`, `CPUIDLE_FLAG_COUPLED`, CPU hotplug states, SMP call-function machinery, cpuidle core locks/devices, and platform drivers that provide synchronized low-level idle entry.

Risks and test signals: risks include delicate atomic bit packing, potential refcount bug in unregister where `kfree()` occurs when refcount remains nonzero, global poke masks shared across coupled sets, busy spinning while interrupts are disabled, and strong assumptions about platform enter functions returning with IRQs disabled or safe to reenable. Test signals include coupled state verification rejecting bad safe state, all CPUs entering target state together, poke masks clearing without deadlock, hotplug blocking coupled entry, and no lost wakeups under interrupt storms.
