# sources/distributed-fs/ceph-client/kernel/trace/preemptirq_delay_test.c

## Purpose
`preemptirq_delay_test.c` is a small kernel module used to create controlled preemption-disabled and IRQ-disabled latency windows. It is intended to exercise latency tracers by generating deterministic sections where either local interrupts or preemption are disabled for a configurable number of microseconds.

## Important APIs, types, and functions
The user-facing controls are module parameters: `delay`, `test_mode`, `burst_size`, and `cpu_affinity`. The important routines are `busy_wait()`, `irqoff_test()`, `preemptoff_test()`, `execute_preemptirqtest()`, the ten generated `preemptirqtest_N()` wrappers, `preemptirq_delay_run()`, `preemptirq_run_test()`, and the sysfs `trigger_store()` handler.

## Control flow
Module initialization runs one test immediately, then creates `/sys/kernel/preemptirq_delay_test/trigger`. A write to `trigger` launches a kthread named after the selected mode. The thread optionally pins itself to `cpu_affinity`, runs up to `burst_size` of the generated wrapper functions, completes `done`, then sleeps until `kthread_stop()` is issued by the caller. `test_mode=irq` wraps the busy wait in `local_irq_save()/local_irq_restore()`, `preempt` wraps it in `preempt_disable()/preempt_enable()`, and `alternate` alternates by wrapper index.

## State and persistence
All state is transient module state. Parameters are read-only module parameters after load, `done` synchronizes the launching thread with the worker, and the sysfs kobject persists until module exit. No trace data is stored here; the latency tracers under test observe the generated delays.

## Dependencies and integration points
It integrates with kthreads, completions, cpumasks, sysfs kobjects, trace clock timing, local IRQ control, and preemption control. The ten unique wrappers deliberately create distinct call sites so stack traces from latency tracers are not all identical.

## Risks and test signals
Risks include intentionally stalling a CPU with IRQs or preemption disabled, invalid CPU affinity causing a logged `set_cpus_allowed_ptr()` failure, `test_mode` strings outside the accepted set producing no delay, and large `delay`/`burst_size` values causing disruptive latency. Test signals are tracer reports matching the configured delay, distinct stack traces for each burst wrapper, correct sysfs retrigger behavior, and affinity causing events to appear on the selected CPU.
