# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/xive-internal.h

## Purpose
`xive-internal.h` is the private contract between the generic XIVE core and its native/sPAPR backends. It defines per-CPU XIVE state, backend operation callbacks, disabled IRQ sentinels, queue constants, and shared initialization/debug helpers.

## Important APIs, Types, And Functions
`XIVE_BAD_IRQ` marks disabled interrupts and `XIVE_MAX_IRQ` bounds valid logical interrupt values. `struct xive_cpu` stores optional IPI hardware state, chip id, up to eight queues, pending-priority bits, and cached CPPR. `struct xive_ops` defines backend hooks for IRQ data population, IRQ configuration/query, queue setup/cleanup, CPU lifecycle, node matching, shutdown, pending update, source sync, ESB access, IPI allocation/free, and debugfs support. Declared helpers are `xive_core_init`, `xive_queue_page_alloc`, `xive_core_debug_init`, and `xive_alloc_order`.

## Control Flow
The header itself has no runtime control flow, but it shapes the sequence used by both backends: discover hardware, provide a populated `xive_ops`, call `xive_core_init`, allocate per-CPU queues through `setup_queue`, acknowledge pending work through `update_pending`, and let common IRQ paths call backend configuration callbacks.

## State And Persistence
It defines in-memory runtime state only. `xive_cpu.queue` entries carry queue page and accounting fields declared in public XIVE headers, while `pending_prio` and `cppr` mirror current CPU interrupt flow state. `xive_cmdline_disabled` and `xive_has_save_restore` are shared global capability/configuration flags.

## Dependencies And Integration Points
The definitions depend on `struct xive_irq_data`, `struct xive_q`, `struct device_node`, `struct seq_file`, and debugfs dentry types from surrounding kernel headers. It is included by `common.c`, `native.c`, and `spapr.c`, and backs external users through exported globals declared here.

## Risks
`struct xive_ops` is a strict backend ABI inside the kernel; common code assumes required callbacks are present for the selected backend. `XIVE_MAX_QUEUES` and priority bit handling are coupled to a `u8 pending_prio`, so adding more priorities requires wider state. Misusing `XIVE_BAD_IRQ` as a real IRQ would corrupt disabled-source handling.

## Test Signals
Compile coverage across native and pseries XIVE configurations validates this header. Runtime signals are successful backend initialization, queue allocation at the selected priority, debugfs creation, IPI setup under `CONFIG_SMP`, and KVM save/restore capability exposure.
