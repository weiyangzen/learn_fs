# sources/distributed-fs/ceph-client/tools/counter/counter_watch_events.c

Purpose: Flexible test utility for configuring one or more Counter API watches from command-line suboptions and reading matching event records.

Important APIs, types, and functions: Name arrays map event/component/scope enum values to strings. `print_watch()` dumps configured watches. `print_usage()` documents CLI. `counter_watch_subopts[]` maps `getsubopt()` tokens to enum-like indices. `main()` does a first option pass to count watches and parse common options, a second pass to fill `struct counter_watch` entries, then opens `/dev/counterN`, adds watches, enables events, and reads events.

Control flow: If no `-w` is provided, uses `simple_watch`. Otherwise allocates one watch per `-w`, parses comma-separated scope/component/event/channel/id/parent tokens, optionally prints debug, opens the target device, adds all watches, enables events, reads until `--loop` count or forever, prints timestamp/value/event/channel, and reports per-event status errors.

State and persistence: Configures watches and event enablement on a device fd. Allocates dynamic watch array when needed.

Dependencies and integration points: Depends on Counter UAPI and `/dev/counterN`. Integrates with kernel counter drivers for exercising event coverage.

Risks: `errno` is not reset before `strtoul()`/`strtol()` conversions, so prior errno can cause false failures. Name arrays are indexed by kernel enum values and need updates if UAPI changes. Unknown suboption error prints `value`, which may be null for flag-style unknown tokens.

Test signals: Parse all suboptions, invalid numeric values, no-watch default, multiple watches, finite loop count, debug output, unsupported watches, and short read behavior.
