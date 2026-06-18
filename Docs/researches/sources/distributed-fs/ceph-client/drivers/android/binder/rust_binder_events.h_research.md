# sources/distributed-fs/ceph-client/drivers/android/binder/rust_binder_events.h

Purpose: declares the Rust Binder tracepoint set for ioctl, read/write completion, waiting, transactions, fd transfer, command, and return events.

Important APIs/types/functions: trace events include `binder_ioctl`, `binder_ioctl_done`, `binder_read_done`, `binder_write_done`, `binder_wait_for_work`, `binder_transaction`, `binder_transaction_received`, `binder_transaction_fd_send`, `binder_transaction_fd_recv`, `binder_command`, and `binder_return`. `binder_function_return_class` is reused for function-return-style events, and `DEFINE_RBINDER_FUNCTION_RETURN_EVENT` instantiates named variants.

Control flow: tracepoint fast-assign blocks copy scalar fields into trace entries. `binder_transaction` uses the inline helpers from `rust_binder.h` to read Rust transaction, node, and process fields and records destination pid/thread, reply flag, code, and flags. `binder_command` and `binder_return` format names through the string tables when `_IOC_NR` is in range.

State and persistence: no driver state is stored here; trace events are passive observation hooks. They depend on live Rust Binder object pointers being valid for the duration of trace emission.

Dependencies and integration points: included by `rust_binder_events.c` for tracepoint creation and by trace wrappers in Rust through generated bindings or C trace symbols. The include path is set to `../drivers/android/binder`, matching kernel trace include conventions.

Risks: tracepoint field extraction crosses the Rust/C layout boundary, so stale offsets can corrupt trace data or fault. Tracepoints must avoid expensive or sleeping operations. String table bounds protect formatting, but table alignment with UAPI remains necessary for useful names.

Test signals: enable each tracepoint under ftrace/perf while issuing Binder ioctls, transactions, replies, fd sends/receives, and blocking reads. Verify transaction ids correlate with Rust debug ids and no trace event dereferences null target nodes except the guarded nullable path.
