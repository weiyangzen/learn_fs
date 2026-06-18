# sources/distributed-fs/ceph-client/tools/verification/rv/src/utils.c

Purpose: `utils.c` implements minimal stderr diagnostics for the `rv` tool.

Important APIs: global `config_debug` gates `debug_msg()`. `err_msg()` and `debug_msg()` format variadic messages into a 1024-byte stack buffer with `vsnprintf()` and write them to stderr.

Control flow and integration: in-kernel monitor support sets `config_debug` when `-v/--verbose` is parsed and calls these helpers for tracefs and parsing diagnostics.

State and dependencies: state is just `config_debug`. Dependencies are stdio/stdarg. Risks include message truncation without indication and no automatic newline insertion; callers must include desired formatting. Test signals are errors visible by default and debug lines visible only with verbose monitor options.
