# sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/smp.c

Purpose: Implements PS3 SMP message passing by mapping PowerPC IPI message classes onto PS3 event receive ports and registering them with generic SMP IPI handling.

Important APIs/types/functions: Defines per-CPU `ps3_ipi_virqs[MSG_COUNT]`, `ps3_smp_message_pass()`, `ps3_smp_probe()`, `ps3_smp_cleanup_cpu()`, `ps3_smp_ops`, and `smp_init_ps3()`.

Control flow: Initialization installs `ps3_smp_ops`. During SMP probe, CPUs 0 and 1 get four event receive ports matching `PPC_MSG_CALL_FUNCTION`, `PPC_MSG_RESCHEDULE`, `PPC_MSG_TICK_BROADCAST`, and `PPC_MSG_NMI_IPI`; successful ports are requested as message IPIs, registered with PS3 IRQ code, and the NMI IPI is registered for debug break. Message sending looks up the target CPU/message virq and calls `ps3_send_event_locally()`. Cleanup destroys each per-CPU event receive port.

State and persistence: Persistent state is the per-CPU virq array. There is no dynamic allocation in this file beyond event ports created by helper APIs. Cleanup resets each virq slot to zero.

Dependencies and integration points: Depends on PS3 event-port helpers, generic PowerPC SMP message numbers, `smp_request_message_ipi()`, PS3 IRQ registration, debug break IPI support, and machine setup calling `smp_init_ps3()`.

Risks: The code assumes exactly two CPUs and fixed message-number ordering, enforced only by `BUILD_BUG_ON()`. Failed event setup leaves some message virqs zero; later sends to those messages may fail in lower layers. Cleanup cannot call `free_irq()` and relies on event-port destruction being sufficient.

Test signals: PS3 SMP boot, reschedule and call-function IPI traffic, tick broadcast, debug/NMI IPI, CPU shutdown/kexec cleanup, and logs for failed event receive port setup are relevant.

Source read size: 120 lines, 2540 bytes.
