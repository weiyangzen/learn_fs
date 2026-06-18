# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/fault.c

Purpose: HFI1 debug fault-injection support for transmit and receive packet paths. It creates a per-device debugfs `fault` directory, allows opcode and direction filtering, tracks injected fault counts, and provides fast-path helpers that decide whether to drop/fault a packet.

Important APIs/functions: `hfi1_fault_init_debugfs()`, `hfi1_fault_exit_debugfs()`, `hfi1_dbg_fault_suppress_err()`, `hfi1_dbg_should_fault_tx()`, and `hfi1_dbg_should_fault_rx()` are the public hooks. Internal helpers include seq-file `fault_stats`, `fault_opcodes_read()`, `fault_opcodes_write()`, and `__hfi1_should_fault()`.

Control flow: initialization allocates `struct fault`, seeds `fault_attr`, default direction `TXRX`, skip counters, booleans, and opcode bitmap, then creates debugfs controls (`enable`, `suppress_err`, `opcode_mode`, `opcodes`, `skip_pkts`, `skip_usec`, `direction`, `fault_stats`). The opcode writer parses comma-separated values/ranges, optional leading `-` removals, and `-1` as clear-all. Runtime checks require fault object, enable flag, matching direction, optional opcode bitmap match, skip time/count expiration, then delegate probability/interval logic to `should_fail()`. Successful injection resets skip state, traces, and increments opcode counters.

State and persistence: per-IB-device `ibd->fault` persists until debugfs exit. State includes Linux `fault_attr`, debugfs dentry, opcode bitmap, enable/suppress/opcode booleans, direction, skip counters, skip deadline in jiffies, and per-opcode RX/TX fault counters.

Dependencies and integration: depends on Linux fault-inject debugfs, bitmap helpers, seq_file, tracepoints, HFI1 packet/QP structures, and debugfs helper macros. Receive code calls `hfi1_dbg_should_fault_rx()` after packet setup; send paths call `hfi1_dbg_should_fault_tx()`.

Risks: debugfs controls intentionally alter packet behavior and should be available only in fault-injection debug builds. `fault_opcodes_read()` writes `data[size - 1] = '\n'` even if no opcodes are set, which can underflow the buffer index; an empty bitmap read should be tested. Opcode parsing returns success length even if parsing stops early, so invalid tail input may be silently ignored. Runtime fields are not explicitly locked, relying on debug/test usage and primitive atomicity.

Test signals: build with and without `CONFIG_FAULT_INJECTION_DEBUG_FS`, debugfs creation/removal, opcode add/remove/range/clear parsing, empty opcode read, direction filtering, skip packet/time behavior, `should_fail()` interval/probability behavior, TX/RX counter increments, and suppress-error behavior in receive error handling.
