## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dbell.h

Purpose: provides PowerPC doorbell/message-send constants and helpers for IPIs and message interrupts.

Important APIs/types/functions: defines doorbell message fields, `enum ppc_dbell`, `_ppc_msgsnd()`, `_ppc_msgclr()`, `ppc_msgsync()`, `ppc_msgsnd_sync()`, `ppc_msgsnd()`, `doorbell_global_ipi()`, `doorbell_core_ipi()`, `doorbell_try_core_ipi()`, and `doorbell_exception()`.

Control flow: Book3S builds use feature-fixup assembly to choose `msgsnd` versus `msgsndp` and `msgclr` versus `msgclrp` depending on HV mode. SMP IPI helpers set KVM host IPI state, issue a full sync, and send a tagged doorbell to PIR or thread-in-core target.

State and persistence: no persistent local state. It touches interrupt/message hardware state and KVM host IPI bookkeeping.

Dependencies and integration: depends on SMP topology helpers, opcode macros, feature fixups, and KVM PowerPC hooks. Used by platform IPI code and doorbell exception handling.

Risks and test signals: message type, target tag, and sync ordering are architecture-sensitive. Wrong topology choice can signal the wrong thread. Test signals include SMP IPI stress, KVM host/guest interrupt tests, Book3S HV and non-HV boots, and doorbell-capable BookE/embedded systems.
