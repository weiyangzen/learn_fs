# sources/distributed-fs/ceph-client/tools/verification/rv/include/utils.h

Purpose: `utils.h` declares shared diagnostic helpers for the `rv` tool.

Important APIs: `debug_msg()` prints only when `config_debug` is set; `err_msg()` always prints to stderr. `MAX_PATH` provides a local path buffer bound. `config_debug` is a global flag implemented in `src/utils.c`.

Control flow and integration: in-kernel monitor code uses these helpers for tracefs/read/write diagnostics, and CLI option parsing toggles `config_debug` on verbose mode.

State, dependencies, risks, and tests: state is a single global debug flag. Risks are fixed 1024-byte message/path buffers in callers and no syslog integration. Test signals are verbose messages appearing with `rv mon ... -v` and errors going to stderr.
