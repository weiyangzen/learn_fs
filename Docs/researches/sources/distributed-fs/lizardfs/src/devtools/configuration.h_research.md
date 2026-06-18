# sources/distributed-fs/lizardfs/src/devtools/configuration.h

Purpose: small environment-variable configuration helper for devtool instrumentation.

Important APIs/functions: protected static `getIntWithUnitOr`, `getIntOr`, `parseIntWithUnit`, `parseInt`, and `getOptionValue`; private `doGetIntFromOption` centralizes parse-and-exit behavior.

Control flow: callers ask for an option with a default; if absent, default is returned. Integer parsing uses string streams; unit parsing accepts B/K/M/G/T suffixes as powers of 1024. Parse failures print a diagnostic to stderr and terminate with `exit(1)`.

State and persistence: stateless; reads process environment.

Dependencies and integration: used by `request_log.h` through `RequestLogConfiguration`; includes signal/stdlib/iostream/string utilities.

Risks: `parseIntWithUnit` reads `text[text.size() - 1]`, so empty strings passed directly would be invalid; public wrappers avoid empty env values by returning defaults. Multiplication may overflow `long` for large values. Exiting inside a helper is abrupt for library use.

Test signals: no direct tests in this subset.
