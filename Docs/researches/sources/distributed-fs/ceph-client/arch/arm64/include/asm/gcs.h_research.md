## sources/distributed-fs/ceph-client/arch/arm64/include/asm/gcs.h

Purpose: declares Guarded Control Stack support for arm64 user shadow stacks.

Important APIs/types/functions: provides `gcsb_dsync`, `gcsstr`, `gcsss1`, `gcsss2`, `PR_SHADOW_STACK_SUPPORTED_STATUS_MASK`, `task_gcs_el0_enabled`, `gcs_set_el0_mode`, `gcs_free`, `gcs_preserve_current_state`, `gcs_alloc_thread_stack`, `gcs_check_locked`, `put_user_gcs`, `push_user_gcs`, `get_user_gcs`, and `pop_user_gcs`, with stubs when disabled.

Control flow: helpers write/read GCS memory with special instructions, validate user access, temporarily enable TTBR0 access, update `GCSPR_EL0`, and enforce locked prctl bits.

State and persistence: per-task `gcs_el0_mode`, lock bits, allocated shadow stacks, and `GCSPR_EL0` persist across user execution.

Dependencies and integration: integrates prctl shadow-stack controls, clone/signal handling, uaccess, sysregs, and exception decoding for GCS faults.

Risks: pointer updates and permission checks protect return-address integrity; mistakes can corrupt shadow stacks or bypass locking. Test signals are GCS selftests, clone/exec/signal tests, fault injection, prctl locking tests, and context-switch preservation.
