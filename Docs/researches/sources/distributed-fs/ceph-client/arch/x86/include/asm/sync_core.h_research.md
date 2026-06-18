<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sync_core.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/sync_core.h

Purpose: defines x86 instruction stream/core synchronization helpers used after text patching, memory permission changes, and control-flow-sensitive updates. Important APIs include `sync_core()`, `iret_to_self()`, `sync_core_before_usermode()`, and flags controlling return-to-user synchronization.

Control flow: callers force a serializing event, often via CPUID or IRET-to-self, so later instruction fetch observes patched code or updated permissions. Return-to-user paths can defer synchronization until safe. State includes CPU pipeline/front-end state and per-thread sync flags.

Dependencies include special instructions, entry/IRET mechanics, thread flags, alternatives/text patching, and speculation/IBT-sensitive code. Risks include executing stale patched instructions, excessive serialization overhead, and unsafe use in noinstr/entry contexts. Test signals include live text patching, ftrace/kprobes/static calls, module alternatives, and SMP patch synchronization tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sync_core.h -->
