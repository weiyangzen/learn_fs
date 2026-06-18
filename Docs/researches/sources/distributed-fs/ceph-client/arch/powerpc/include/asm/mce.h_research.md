# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mce.h

Purpose: defines PowerPC machine-check event taxonomy, event storage structures, queues, notifier APIs, and Book3S 64 real-mode machine-check hooks.

Important APIs/types/functions: enums describe version, severity, disposition, initiator, error type, error class, and subtype families for UE, SLB, ERAT, TLB, user, RA, and link errors. `struct machine_check_event`, `struct mce_error_info`, and `struct mce_info` carry event data and queues. APIs include `save_mce_event`, `get_mce_event`, `release_mce_event`, `machine_check_queue_event`, `machine_check_print_event_info`, `addr_to_pfn`, `mce_common_process_ue`, notifier registration, IRQ work helpers, SLB/ERAT flush, real-mode P7/P8/P9/P10 handlers, and `mce_init`.

Control flow: early machine-check handlers classify an event, save it into per-CPU queues, possibly recover or mark fatal disposition, queue delayed processing, and notify registered consumers. Book3S 64 can run additional IRQ-context handlers and real-mode recovery paths.

State and persistence: `mce_info` holds bounded per-CPU active and delayed event queues. Event structures persist until released or printed/processed. Hardware recovery may mutate SLB/ERAT and machine-check state.

Dependencies and integration points: depends on bitops, pt_regs, notifier blocks, Book3S 64 exception code, RAS/EDAC style consumers, and KVM guest-aware printing.

Risks: queues are bounded by `MAX_MC_EVT`; overflow loses diagnostic data. Event layout and subtype interpretation affect userspace/kernel diagnostics. Real-mode handlers have strict constraints and must avoid unsafe operations.

Test signals: inject machine checks where platform supports it, test recoverable UE processing, SLB/ERAT flush recovery, notifier registration, delayed IRQ work, queue release semantics, and Book3S 64 real-mode handler coverage.
