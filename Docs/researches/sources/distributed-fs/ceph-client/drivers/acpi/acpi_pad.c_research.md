# sources/distributed-fs/ceph-client/drivers/acpi/acpi_pad.c

## Purpose
`acpi_pad.c` implements the ACPI Processor Aggregator driver for `ACPI000C`. It responds to firmware requests to idle a number of CPUs by creating high-priority kernel threads that enter deep MWAIT states and rotates those threads across CPUs.

## Important APIs, Types, And Functions
Important state includes `power_saving_mwait_eax`, TSC instability flags, `cpu_weight`, `tsk_in_cpu`, `pad_busy_cpus_bits`, `idle_pct`, `round_robin_time`, `ps_tsks`, and `ps_tsk_num`. Main functions are `power_saving_mwait_init()`, `round_robin_cpu()`, `power_saving_thread()`, `create_power_saving_task()`, `destroy_power_saving_task()`, `set_power_saving_task_num()`, sysfs `idlecpus`, `idlepct`, and `rrtime` handlers, `acpi_pad_pur()`, `acpi_pad_handle_notify()`, `acpi_pad_notify()`, `acpi_pad_probe()`, `acpi_pad_remove()`, `acpi_pad_init()`, and `acpi_pad_exit()`.

## Control Flow
Init skips Xen Dom0, determines the deepest usable MWAIT hint, and registers the platform driver. Probe installs an ACPI notify handler. On notify `0x80`, the driver evaluates `_PUR`; if firmware returns a CPU count, it creates or stops power-saving threads to match, then reports status and current idle count via `_OST` and emits a netlink event. Each power-saving thread is RT-priority, periodically chooses a CPU avoiding sibling contention where possible, enters low-power MWAIT with interrupts disabled and tick broadcast coordination, sleeps enough to respect `idle_pct`, and exits its CPU assignment on stop. Sysfs can also set requested idle CPU count, idle percentage, and rotation time.

## State And Persistence
All state is runtime kernel state. Sysfs attributes reflect and mutate global driver settings. Created kthreads persist until firmware/sysfs requests fewer idle CPUs, device removal, or module exit.

## Dependencies And Integration Points
It depends on ACPI platform devices and notifications, `_PUR`/`_OST`, CPU masks and hotplug read locking, scheduler RT policy, MWAIT CPUID and idle helpers, tick broadcast, perf low-power callbacks, TSC stability handling, and Xen detection.

## Risks
This driver deliberately consumes CPU time to force package power savings; incorrect settings can impact latency and throughput. MWAIT support and TSC behavior vary by CPU vendor. The global arrays are sized by `NR_CPUS`, and hotplug/online CPU changes must remain coordinated through CPU locks. `round_robin_cpu()` leaves `preferred_cpu` uninitialized in theory if the loop never runs, though the code checks for empty masks before the loop.

## Test Signals
Tests should cover unsupported MWAIT, Xen Dom0 skip, `_PUR` success/failure, `_OST` status, sysfs bounds for `idlepct` and `rrtime`, CPU hotplug during active threads, thread creation failure, and module removal stopping all threads.
