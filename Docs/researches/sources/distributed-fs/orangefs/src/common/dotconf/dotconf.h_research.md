# sources/distributed-fs/orangefs/src/common/dotconf/dotconf.h

Purpose: Public interface and data model for the OrangeFS-bundled dot.conf parser.

Important APIs/types: Defines parser limits, option type constants, runtime flags, error codes, logging levels, callback typedefs, and macros for option-table termination and callback declarations. `configfile_t` describes parser state and registered options. `configoption_t` describes one option name, type, callback, auxiliary info, context mask, and default value. `command_t` carries parsed command name, option descriptor, typed data, arg list/count, error bit, and context pointers.

Control flow contract: Applications create a parser with `PINT_dotconf_create()`, optionally register callbacks/options, run `PINT_dotconf_command_loop()` or `_until_error()`, and call `PINT_dotconf_cleanup()`. Callback return strings become parser errors.

State/persistence: The header exposes many `configfile_t` fields as read-only by convention, not type-enforced. Parsed arguments in `command_t` are transient and freed after callback invocation.

Dependencies/integration: C/C++ compatible with `extern "C"`. Includes `stdio.h` for `FILE *` and optionally syslog constants. Integrated into OrangeFS config consumers through `PINT_`-prefixed parser APIs.

Risks: Struct internals are public, so consumers can accidentally depend on layout. Parser limits are compile-time constants. `FUNC_ERRORHANDLER` macro uses `long dc_errno` while typedef uses `unsigned long`, a small signature inconsistency.

Test signals: Compile C and C++ consumers, validate option-table termination macros, and test every option type against callback-visible `command_t` fields.
