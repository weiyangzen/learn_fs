# sources/distributed-fs/ceph-client/arch/arm/kernel/thumbee.c

Purpose: enables ThumbEE support when the CPU advertises it and preserves the ThumbEE Handler Base Register across thread lifecycle events. Key functions are `teehbr_read`, `teehbr_write`, `thumbee_notifier`, and late init `thumbee_init`.

Control flow: init checks ARMv7+ and CPUID PFR0 ThumbEE bits, sets `HWCAP_THUMBEE`, and registers a thread notifier. On `THREAD_NOTIFY_FLUSH` it clears TEEHBR; on `THREAD_NOTIFY_SWITCH` it saves the outgoing thread's value and restores the incoming thread's `thumbee_state`. State lives in per-thread `thread_info`; the CPU register is transient per context. Dependencies are CP14 register access, `elf_hwcap`, and the ARM thread notifier chain. Risks are unsupported coprocessor access, stale per-thread ThumbEE state, and missing hwcap publication. Test signals include hwcap visibility, context-switch preservation, and no registration on CPUs without ThumbEE.
