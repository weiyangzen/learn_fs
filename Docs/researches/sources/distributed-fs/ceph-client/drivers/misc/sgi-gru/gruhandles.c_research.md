# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/gruhandles.c

Purpose: implements privileged GRU MCS handle operations for context configuration, TLB invalidation, and TLB fault-handle dropins/restarts.

Important APIs and functions: exported-to-subsystem functions include `cch_allocate()`, `cch_start()`, `cch_interrupt()`, `cch_deallocate()`, `cch_interrupt_sync()`, `tgh_invalidate()`, `tfh_write_only()`, `tfh_write_restart()`, `tfh_user_polling_mode()`, and `tfh_exception()`. Internal helpers are `start_instruction()`, `wait_instruction_complete()`, `report_instruction_timeout()`, and `update_mcs_stats()`.

Control flow: each operation fills opcode-specific fields, calls `start_instruction()` to set command/status bits after a write barrier and cache flush, then either waits for handle status to leave ACTIVE or returns after issuing async restart-like commands. CCH allocate/deallocate call `sync_core()` to stop speculation into mapped/unmapped GSEG regions. Timeouts after roughly 10 seconds call `panic()` because hardware is considered malfunctioning.

State and persistence: updates hardware MCS handle cachelines and optional `mcs_op_statistics[]`. No file persistence.

Dependencies and integration points: depends on `gruhandles.h`, `grutables.h`, `gru_flush_cache()`, x86 TSC frequency, and consumers in GRU context load/unload, fault handling, and TLB purge code.

Risks and test signals: timeout panic is intentionally severe. Correct memory barriers/cache flushing are essential. Tests should exercise each handle opcode on emulator/hardware, exception status returns, stats accounting with `OPT_STATS`, CCH speculation barriers, and malformed/stuck handle timeout behavior in controlled environments.
