<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/uring-support.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/uring-support.rs

### Purpose
`uring-support.rs` is a tiny diagnostic binary that exits according to kernel io_uring support. It is useful for scripts and deployment checks.

### Important APIs, Types, And Functions
`Args` is an empty clap parser used for standard help/version output. `main` calls `io_engine::bdev::util::uring::kernel_support`.

### Control Flow
The binary parses arguments, checks kernel support, and exits with code `0` when supported and `1` when not supported by casting `!supported` to `i32`.

### State, Persistence, And Dependencies
There is no state or persistence. Dependencies are clap, version info, and the io-engine uring utility.

### Risks And Test Signals
The behavior is encoded solely in exit status, not stdout. Tests should cover supported and unsupported mocked paths, help/version parsing, and shell-script interpretation of the exit code.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/uring-support.rs -->
