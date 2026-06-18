# sources/control-plane/mayastor/io-engine/src/logger.rs

## Purpose
This module configures io-engine logging and tracing. It bridges SPDK logs into Rust logging, provides default/compact/JSON formatters, supports optional hostname and eventing output, and exposes CLI-friendly span event options.

## Important APIs, types, and functions
`log_impl` is the C ABI callback used for SPDK logs; it maps `spdk_log_level` to `log::Level`, checks SPDK print level, converts C strings, and emits a Rust `log::Record` with target `mayastor::spdk`. `LogFormat` stores formatter options: ANSI, `LogStyle`, date, and hostname. `FromStr` parses comma-separated options such as `compact`, `json`, `color`, `nodate`, and `host`.

`FormatLevel`, `CustomContext`, `Location`, and `LogHostname` implement display helpers. `StringVisitor` extracts tracing event fields for JSON mode. `FmtSpan` maps CLI enum values to tracing subscriber span lifecycle flags. `init_ex` installs `LogTracer`, builds the tracing formatter layer, applies a rust-log filter, optionally adds an event publisher layer for `EVENTING_TARGET`, and installs the global subscriber. `init` is the default simple initializer.

## Control flow
Runtime setup flows through `init_ex`: initialize log-to-tracing bridge, create format/event layer filtered away from eventing target, build target/env filter, optionally initialize event publishing via `EventHandle::init_ext`, combine layers on `Registry`, and set the global default subscriber. Formatting branches per event into default, compact, or JSON style. SPDK logs enter through `log_impl`, then re-enter the same global logging pipeline.

## State and persistence behavior
The global tracing subscriber and `LogTracer` are process-global one-time state. `HOSTNAME_PREFIX` caches hostname in `OnceCell`. Logging does not persist directly except through configured stdout/stderr and event-publisher sinks.

## Dependencies and integration points
Dependencies include `tracing`, `tracing_subscriber`, `tracing_log`, `tracing_filter`, `ansi_term`, `chrono`, `event_publisher`, `once_cell`, `nix`, and SPDK log FFI. It integrates with CLI logging configuration, SPDK log callback registration, and control-plane event emission.

## Risks and test signals
`set_global_default` and `LogTracer::init` panic on repeated initialization, so tests or embedding processes must initialize once. `log_impl` dereferences raw C strings and unwraps file conversion. JSON style collapses recorded fields into a single `message` field and may not preserve structured tracing fields. Eventing filter correctness matters to avoid recursive event logs. Useful tests cover `LogFormat::from_str`, formatting modes, hostname toggling, and repeated-init behavior; this file has no local tests visible.
