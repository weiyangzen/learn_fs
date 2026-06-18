## sources/distributed-fs/ceph-client/rust/kernel/std_vendor.rs

Purpose: vendors and adapts standard Rust `dbg!` behavior for the kernel, printing through `pr_info!` instead of standard error.

Important APIs/types/functions: the exported `dbg!` macro supports no-argument location printing, one expression returning the expression value, and multiple expressions returning a tuple. It uses `file!`, `line!`, `column!`, `stringify!`, and `Debug` formatting.

Control flow: single-expression expansion evaluates via `match` to control temporary lifetimes, logs the source location, expression text, and pretty debug value, then returns the moved value. Multi-expression form recursively calls `dbg!` for each expression.

State/persistence: no state except kernel log output.

Dependencies/integration: depends on `pr_info!` and Rust formatting. It is intended for temporary development diagnostics, not committed production logging.

Risks: it moves non-`Copy` inputs just like standard `dbg!`, can leak sensitive data into kernel logs, and always runs in release builds. Output format is not stable.

Test signals: documentation examples describe expression, no-arg, method-call, recursive, and tuple behavior. Practical validation is macro expansion/compile coverage and controlled log output checks.
