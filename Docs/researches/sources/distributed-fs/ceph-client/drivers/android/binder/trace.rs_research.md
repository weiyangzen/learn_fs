# sources/distributed-fs/ceph-client/drivers/android/binder/trace.rs

## Purpose
`trace.rs` is the Rust Binder tracepoint wrapper layer. It declares Rust-callable bindings for Binder tracepoints and exposes small safe wrapper functions that convert Rust Binder state and `Result` values into the C tracepoint ABI.

## Important APIs, Types, And Functions
The `declare_trace!` block declares tracepoints for ioctl entry/exit, read/write completion, wait-for-work decisions, transaction send/receive, fd send/receive, commands, and returns. `raw_transaction` casts a Rust `Transaction` reference to the generated `rust_binder_transaction` handle described by `TRANSACTION_LAYOUT` in `transaction.rs`. `to_errno` converts `kernel::error::Result` into integer errno. Public crate wrappers include `trace_ioctl`, `trace_ioctl_done`, `trace_read_done`, `trace_write_done`, `trace_wait_for_work`, `trace_transaction`, `trace_transaction_received`, `trace_transaction_fd_send`, `trace_transaction_fd_recv`, `trace_command`, and `trace_return`.

## Control Flow
Callers invoke wrappers at event sites in Binder ioctl, thread, and transaction code. The wrappers do no filtering or buffering; they immediately call the underlying tracepoint in an `unsafe` block. Transaction trace wrappers optionally pass a target task pointer or null and rely on the event consumer to decode fields through the transaction layout exported from Rust.

## State And Persistence
The file owns no persistent state. It observes transaction objects only for the duration of a tracepoint call and writes event records into the kernel tracing infrastructure when enabled. Errnos are computed per call and not retained.

## Dependencies
It depends on `kernel::tracepoint::declare_trace`, kernel C FFI types, `task_struct`, `Task`, and the generated `rust_binder_transaction` layout. Correctness depends on `transaction.rs` exporting offsets that match what C tracepoint code expects.

## Integration Points
The wrappers are used by Rust Binder thread and transaction code. They integrate with the C trace definitions in `binder_trace.h` and with ftrace/perf tooling that consumes Binder trace events. Transaction tracing is ABI-sensitive because it crosses Rust/C object-layout boundaries.

## Risks
The main risk is layout drift: if `TRANSACTION_LAYOUT` and the tracepoint-side interpretation disagree, tracing can read wrong fields or unsafe addresses. Pointer casts are intentionally narrow but still rely on the transaction object being alive for the tracepoint call. Missing trace wrappers for newer C events would leave observability gaps, while tracepoint ABI mismatches can break builds.

## Test Signals
Build with Rust Binder tracing enabled, run Binder transaction traffic while enabling `binder:*` ftrace events, verify ioctl/read/write errno values, check transaction IDs/codes/flags against debugfs or Binder logs, and validate fd send/receive trace offsets during fd transfer tests.
