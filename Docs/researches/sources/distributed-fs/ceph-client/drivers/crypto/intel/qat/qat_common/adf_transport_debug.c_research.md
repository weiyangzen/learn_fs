# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_transport_debug.c

## Purpose
`adf_transport_debug.c` provides debugfs inspection for QAT ETR banks and rings. It exposes per-ring configuration and raw ring data dumps plus per-bank head/tail/empty summaries.

## Important APIs, Types, And Functions
The exported internal debugfs hooks are `adf_ring_debugfs_add()`, `adf_ring_debugfs_rm()`, `adf_bank_debugfs_add()`, and `adf_bank_debugfs_rm()`. Seq-file operations are implemented by `adf_ring_start/next/show/stop()` and `adf_bank_start/next/show/stop()`. The ring debug entry stores the human-readable ring name and debugfs dentry in `struct adf_etr_ring_debug_entry`.

## Control Flow
Bank debugfs creation makes `transport/bank_%02d/config`. Ring debugfs creation adds `ring_%02d` under the bank directory and records the configured ring name. Reading a ring file locks `ring_read_lock`, emits a header with ring name, bank/ring number, CSR head/tail, empty status, ring and message sizes, then hex-dumps each message slot. Reading a bank config locks `bank_read_lock`, emits a bank header, skips unreserved rings, and reports head/tail/empty state for active rings.

## State And Persistence Behavior
Debug state is runtime-only. Each active ring owns an allocated debug entry; each bank stores debugfs dentries. The seq readers inspect live coherent DMA ring memory and live CSRs, so output changes as hardware and callbacks advance rings.

## Dependencies And Integration Points
The file depends on debugfs, seq_file, transport internals, CSR operations, and transport conversion macros. It is called only from transport bank/ring create and cleanup paths, and becomes a diagnostic integration point for QAT services using ETR rings.

## Risks
Ring dumping exposes raw firmware messages to privileged debugfs readers; this may include addresses or request metadata. The global read mutexes serialize reads but do not freeze hardware updates, so dumps can be a live snapshot rather than a coherent transaction. `adf_bank_show()` casts `loff_t *pos` to `int *`, which is fragile across type sizes and can misreport on unusual architectures.

## Test Signals
With `CONFIG_DEBUG_FS`, probe should create transport bank directories and ring files. Reading ring files should show correct head/tail progression and no crashes under concurrent traffic. Removal should clean dentries without leaks or use-after-free warnings.
