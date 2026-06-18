<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_io.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_io.rs

Purpose: implements the fast-path nexus I/O submission and completion logic. It translates a parent SPDK bdev I/O into one child read or fan-out write-like operations, handles retries and resubmission, faults failed children, logs writes for partial rebuild, and completes the parent I/O.

Important APIs/types/functions: `NioCtx`, `NexusBio`, `NexusBio::new`, `submit_request`, `child_completion`, `complete`, `readv`, `do_readv`, `submit_all`, `submit_write`, `submit_unmap`, `submit_write_zeroes`, `submit_reset`, `submit_flush`, `resubmit`, `fail`, `fail_nvme_status`, `completion_error`, `fault_device`, `log_io`, and fault-injection helpers under feature flags.

Control flow: `submit_request` freezes the I/O if the channel is frozen, otherwise dispatches by `IoType`. Reads select one reader and retry other readers if submission fails. Writes, unmaps, write-zeroes, resets, and flushes submit to every writer and log write-like ranges to active I/O logs. Each child completion updates `in_flight`, success/failure counters, and on last completion either completes success, resubmits when some children succeeded, or fails the parent if all failed.

State and persistence: per-I/O state lives in SPDK driver context `NioCtx` and is sized by the nexus module. Nexus-wide `last_error` records the final child error when all children fail and affects parent failure status. No disk persistence occurs, but completion errors can schedule child retirement, which later updates persistent nexus info. Effective offsets add the nexus data partition offset before child submission.

Dependencies/integration: uses `NexusChannel` for reader/writer/log selection, block-device handle APIs, SPDK NVMe completion status helpers, Mayastor `IoCompletionStatus`, `IoStatus`, `CoreError`, `NvmeStatus`, `LvolFailure`, and optional `fault-injection`/`nexus-io-tracing` features.

Risks: submission errors fault devices broadly, with TODOs noting ENOMEM and ENXIO should be distinguished. Parent I/O resubmission after partial child failure can repeat writes on children that already succeeded, so child idempotence and upper-layer semantics matter. Reservation conflict triggers self-shutdown rather than child retire. Invalid opcode is ignored for retire. Frozen I/O stores cloned `NexusBio` until resume/abort.

Test signals: read selection and retry exhaustion, write fan-out partial submission failure, all-completion success/fail/resubmit paths, ENOSPC mapping to capacity exceeded, reservation conflict self-shutdown, invalid opcode no-retire behavior, write logging when I/O log exists, frozen submission and abort, data partition offset correctness, and fault-injection submission/completion paths.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/nexus/nexus_io.rs -->
