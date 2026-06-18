<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/main.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/main.rs

### Purpose
`main.rs` is the top-level binary entrypoint for `io-engine-client`. It selects the v0 or v1 command tree, initializes logging, defines shared gRPC client aliases, and centralizes user-facing error reporting.

### Important APIs, Types, And Functions
The file defines `MayaClient`, `BdevClient`, and `JsonClient` aliases over tonic `Channel`, the shared `ClientError` enum, and the crate-local `Result<T>`. `ClientError` covers gRPC statuses, context construction failures, and CLI-level missing-value validation.

### Control Flow
The Tokio main runtime uses two worker threads. It reads `API_VERSION`: `v0` dispatches to `v0::main_`, `v1` and unset both dispatch to `v1::main_`, and any other value panics. If the selected command tree returns an error, the binary prints the display error, prints a SNAFU backtrace when available, and exits with status 1.

### State, Persistence, And Dependencies
The binary is stateless aside from environment variables and process exit status. It depends on generated v0 clients, `tonic`, `snafu`, `env_logger`, Tokio, and the sibling `context`, `v0`, and `v1` modules. It integrates with every subcommand through the shared `ClientError` and `Result` type.

### Risks And Test Signals
Invalid `API_VERSION` is a panic rather than a formatted CLI error. The default API version is v1, which matters for scripts written before v1 became default. Tests should assert default/v0/v1 dispatch, non-zero exit on subcommand error, backtrace printing when enabled, and compatibility of `ClientError` display strings used by operators and automation.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/main.rs -->
