# sources/distributed-fs/openafs/src/vol/daemon_com_inline.h

Purpose: tiny diagnostic helper header for the generic SYNC protocol. It converts generic SYNC response codes into stable string names for logs and debug tools.

Important APIs/types/functions: `SYNC_res2string(afs_int32 response)` is a `static_inline` switch that recognizes `SYNC_OK`, `SYNC_DENIED`, `SYNC_COM_ERROR`, `SYNC_BAD_COMMAND`, and `SYNC_FAILED`. The private `SYNC_ENUMCASE` macro keeps case labels and returned strings synchronized, then is undefined at the end of the file.

Control flow: runtime behavior is only a switch lookup. Unknown or protocol-specific response values fall through to `"**UNKNOWN**"`.

State and persistence: no mutable state and no persistence. The returned strings are string literals.

Dependencies: includes `daemon_com.h` and relies on the repository's `static_inline` definition from platform headers included before this header in normal OpenAFS builds.

Integration points: used by `fssync-server.c` for verbose response logging and by `fssync-debug.c` for command-line output. It intentionally covers only generic SYNC response codes, while protocol-specific command/reason stringification lives in `fssync_inline.h`.

Risks: new generic response codes added to `daemon_com.h` need a matching case here or debug output degrades to unknown. The function returns `char *` rather than `const char *`, so callers could technically attempt to mutate literals.

Test signals: compile inclusion with `daemon_com.h`, one assertion for every known response code, and an unknown-value assertion returning `"**UNKNOWN**"`.
