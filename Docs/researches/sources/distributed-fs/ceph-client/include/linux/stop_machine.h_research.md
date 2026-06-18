# sources/distributed-fs/ceph-client/include/linux/stop_machine.h

Purpose: declares the kernel stop-machine and per-CPU stopper interfaces used when code must run with selected CPUs monopolized or the whole machine quiesced.

Important APIs and types: `cpu_stop_fn_t` is the non-sleeping callback signature. `struct cpu_stop_work` is either queued stopper work on SMP or a `work_struct` fallback on UP. Public entry points include `stop_one_cpu()`, `stop_two_cpus()`, `stop_one_cpu_nowait()`, `stop_machine()`, `stop_machine_cpuslocked()`, `stop_core_cpuslocked()`, and `stop_machine_from_inactive_cpu()`. SMP-only helpers park/unpark stoppers and print stopper diagnostics.

Control flow: callers submit a callback and argument for execution on target CPUs. SMP builds use preallocated per-CPU stopper resources and, for `stop_machine()`, schedule stopper threads that run with interrupts disabled while other CPUs are prevented from useful progress. UP/non-hotplug fallbacks run the function locally with preemption or interrupts disabled.

State and persistence: no persistent state is owned by the header. Runtime state lives in stopper work queues, CPU hotplug state, and preallocated per-CPU stopper resources.

Dependencies and integration points: integrates with CPU hotplug locking, cpumasks, SMP/preemption control, workqueues for UP fallback, and task diagnostics. It is used by high-risk kernel mutation paths such as CPU hotplug, text patching, and synchronization fallbacks.

Risks and test signals: risks are deadlock or latency spikes from sleeping callbacks, misuse outside `cpus_read_lock()` for the cpuslocked variants, offline CPU targeting, and assumptions that stop-machine calls serialize globally. Test signals include SMP/UP builds, CPU hotplug stress, lockdep with raw spinlocks, latency tracing, and fault injection around offline targets.
