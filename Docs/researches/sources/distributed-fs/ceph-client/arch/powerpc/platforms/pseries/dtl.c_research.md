# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/dtl.c

Purpose: Implements pseries Dispatch Trace Log support and stolen-time accounting integration for shared-processor LPARs. It can expose per-CPU DTL buffers through debugfs and scan dispatch entries for virtual CPU accounting.

Important APIs/types/functions: Defines `struct dtl`, optional `struct dtl_ring`, per-CPU `cpu_dtl` and `dtl_rings`, `dtl_event_mask`, `dtl_buf_entries`, `consume_dtle()`, `dtl_start()`, `dtl_stop()`, `dtl_current_index()`, `dtl_enable()`, `dtl_disable()`, debugfs file ops, `dtl_init()`, `scan_dispatch_log()`, `pseries_accumulate_stolen_time()`, and `pseries_calculate_stolen_time()`.

Control flow: Debugfs init creates `/sys/kernel/debug/powerpc/dtl` files for each possible CPU on SPLPAR systems. Opening a CPU file allocates a per-CPU buffer, registers it with the hypervisor or hooks native accounting consumption, and enables event logging. Reads copy whole `struct dtl_entry` records from the ring while handling wrap and overflow. Accounting scans PACA dispatch logs with interrupts disabled and subtracts stolen time from user/system accounting buckets.

State and persistence: Per-CPU state includes buffer pointer, CPU id, buffer entries, last read index, and lock. Native accounting mode adds per-CPU ring state and a global consumer pointer protected by atomic count. LPPACA `dtl_enable_mask`, `dtl_idx`, PACA `dtl_ridx`, and `dtl_curr` are persistent runtime accounting state.

Dependencies and integration points: Depends on SPLPAR firmware feature, LPPACA/PACA layout, `register_dtl()`/`unregister_dtl()`, `dtl_cache` and `dtl_access_lock`, debugfs, virtual CPU accounting, and PowerPC time accounting.

Risks: Only one reader is allowed per CPU, and conflicts with other DTL users must be enforced by `dtl_access_lock`. Ring overflow drops old entries. Barriers are required to publish entries and write indexes in the right order. Accounting must run with interrupts disabled and avoid tracing recursion.

Test signals: Debugfs DTL open/read/close, buffer wrap tests, SPLPAR stolen-time accounting under CPU contention, native and non-native accounting configs, lockdep around `dtl_access_lock`, and overflow behavior are important.

Source read size: 444 lines, 9717 bytes.
