## sources/distributed-fs/ceph-client/rust/kernel/seq_file.rs

Purpose: provides a minimal Rust facade over `struct seq_file` for formatted output in procfs/debugfs-style sequential files.

Important APIs/types/functions: `SeqFile` is a transparent wrapper containing `Opaque<bindings::seq_file>` and `NotThreadSafe`. `unsafe from_raw` creates a borrowed wrapper from C. `call_printf` writes `fmt::Arguments` through `seq_printf("%pA")`. The exported `seq_print!` macro mirrors Rust formatting syntax.

Control flow: callers receive a raw seq-file pointer from a C callback, wrap it with `from_raw`, then invoke `seq_print!`, which passes `fmt!` arguments to `call_printf`.

State/persistence: state is the underlying C seq file buffer/cursor managed by the kernel seq-file subsystem. The Rust wrapper owns no buffer.

Dependencies/integration: depends on `bindings::seq_printf`, `fmt`, `CStrExt::as_char_ptr`, `Opaque`, and `NotThreadSafe`. It integrates with kernel virtual file emit paths.

Risks: `from_raw` is unsafe because the caller must guarantee exclusive thread access and valid lifetime. `call_printf` ignores `seq_printf` return behavior; consumers cannot observe truncation/error through this API. The `%pA` format assumes kernel formatting support for Rust `Arguments`.

Test signals: no direct tests. Compile-time macro use and seq-file callback integration tests should verify formatting, truncation behavior, and thread confinement.
