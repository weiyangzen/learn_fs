# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/switch.c

Purpose: host-side SPU context save/restore engine. It follows the SPE Book IV sequence to quiesce hardware, save privileged/problem state, load SPU-side helper programs, transfer local-store/LSCSA data, restore state, and initialize new CSAs.

Important APIs: exported `spu_save`, `spu_restore`, `spu_init_csa`, and `spu_fini_csa`. Major internal phases are `quiece_spu`, `save_csa`, `save_lscsa`, `harvest`, `restore_lscsa`, `restore_csa`, and `__do_spu_save`/`__do_spu_restore`. Many static helpers map one documented save/restore step to MMIO operations.

Control flow: save disables interrupts, blocks context-switch-sensitive handlers, suspends/purges MFC queues, saves run-control/status/channel/mailbox/query state, configures kernel SLBs for helper code and LSCSA, DMAs save code into local store, waits for tag completion and SPU stop completion, and validates `SPU_SAVE_COMPLETE`. Restore first harvests/reset hardware, configures LSCSA/status/decrementer/mailboxes, DMAs restore code, waits for `SPU_RESTORE_COMPLETE`, restores queues/channels/registers/status/routing, and reenables interrupt masks.

State and dependencies: includes generated `spu_save_dump.h` and `spu_restore_dump.h`, manipulates `struct spu_state`, SPU MMIO, SLBs, interrupts, and `spu->flags`. It also initializes default CSA register values and allocates LSCSA via `lscsa_alloc.c`. Risks are high: busy waits, panic on failed save/restore, incomplete TODO steps for user/other-SPU access, exact hardware sequencing, and isolate exit handling. Test signals include stress preemption, fault during switch, isolate state, mailbox/MFC queue preservation, register/local-store round trips, and lockdep/IRQ assertions.
