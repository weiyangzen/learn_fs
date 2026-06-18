<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/context.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/context.rs

### Purpose
`context.rs` is the shared execution context for `io-engine-client`. It normalizes connection options, constructs the v0 and v1 tonic clients, stores output preferences, and provides common table, verbosity, and byte-unit formatting helpers used by every CLI command module.

### Important APIs, Types, And Functions
The main public surface is `Context::new`, `Context::v1`, `Context::v2`, `Context::units`, `Context::units_with`, `Context::print_list`, and `Context::print_streamed_list`. `OutputFormat` selects human or JSON output, and `Units` selects bytes, binary, or decimal display. The nested private `v1` module aliases all v1 generated service clients and groups them into `v1::Context`.

### Control Flow
`Context::new` accepts a bind string, verbosity flags, units, and output format. It parses the URI, falls back to bracketed IPv6 parsing when plain parsing fails, injects `http` when no scheme is present, adds port `10124` when no port is supplied, and defaults the path to `/`. It then builds a tonic `Endpoint` and eagerly connects v0 Mayastor/Bdev/Json clients plus all v1 clients. Printing helpers build aligned table columns from the first rows and headers; headers prefixed with `>` are right-aligned. `print_streamed_list` buffers the first streamed row to size columns, emits the header when verbose, then drains the channel.

### State, Persistence, And Dependencies
The context owns client handles, verbosity, unit preference, and output mode for a single process invocation. It persists nothing beyond stdout/stderr. Dependencies include `tonic::transport::Endpoint`, generated `io_engine_api` clients, `http::Uri` parts, `byte_unit`, `bytes`, and SNAFU errors. URI normalization is an integration point for both `API_VERSION=v0` and default v1 clients.

### Risks And Test Signals
Every client connection uses `unwrap`, so transport failures panic instead of returning `ContextCreate`. `print_list` asserts non-empty data and matching header length, so callers must guard empty lists. `print_streamed_list` sizes columns from the first row only, so later longer rows can exceed header widths. Useful tests cover bind strings with host-only, IPv6, explicit ports, quiet/verbose formatting, right-aligned numeric columns, byte-unit selection, and connection error behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/context.rs -->
