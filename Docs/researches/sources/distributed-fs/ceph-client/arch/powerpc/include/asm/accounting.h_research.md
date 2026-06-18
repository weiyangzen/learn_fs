# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/accounting.h

Purpose: defines the per-CPU accounting data layout used by PowerPC time accounting code.

Important APIs/types/functions: `struct cpu_accounting_data` contains accumulated user, system, guest, hardirq, softirq, stolen, and idle cputime values plus internal timebase snapshots. With `CONFIG_ARCH_HAS_SCALED_CPUTIME`, it also carries scaled user/system fields and SPURR-based snapshots.

Control flow: this header is declarative. Accounting code elsewhere updates the fields on ticks, context transitions, IRQ entry/exit, and virtualization accounting events.

State and persistence: instances of `cpu_accounting_data` persist as CPU-local runtime accounting state. The structure records accumulated time plus start snapshots such as `starttime`, `starttime_user`, and optional `startspurr`.

Dependencies and integration points: integrates with PowerPC scheduler cputime accounting, timebase/SPURR accounting, guest time, stolen time, and IRQ time accounting implementations.

Risks: field order and config-gated fields must match all users. Incorrect snapshot maintenance in implementation code would skew user/system/steal/IRQ time, especially on virtualized systems.

Test signals: build with and without `CONFIG_ARCH_HAS_SCALED_CPUTIME`; validate `/proc/stat`, task cputime, guest/steal accounting, and IRQ time under CPU-bound and interrupt-heavy workloads.
