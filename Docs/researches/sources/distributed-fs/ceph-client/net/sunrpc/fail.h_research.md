# sources/distributed-fs/ceph-client/net/sunrpc/fail.h

Purpose: declares the optional SUNRPC fault-injection control structure shared by debugfs setup and runtime fault sites. It is compiled when kernel fault injection support is enabled.

Important APIs/types/functions: `struct fail_sunrpc_attr` contains a generic `struct fault_attr` plus booleans `ignore_client_disconnect`, `ignore_server_disconnect`, and `ignore_cache_wait`. The global `fail_sunrpc` is declared for consumers and defined/exported in `debugfs.c` under the appropriate config.

Control flow: runtime code includes this header and, when `CONFIG_FAULT_INJECTION` or related SUNRPC failure config is enabled, checks the booleans or `should_fail(&fail_sunrpc.attr, ...)` to alter behavior. Debugfs creates files that mutate these fields.

State and persistence behavior: state is in-memory global fault-injection configuration exposed through debugfs. It is reset on module/kernel lifetime and not persisted.

Dependencies/integration points: depends on `<linux/fault-inject.h>`. It is consumed by cache deferral fault paths and SUNRPC transport/server disconnect fault paths, and configured through `debugfs.c`.

Risks: the header only declares `fail_sunrpc` when fault injection is enabled; consumers must use matching `IS_ENABLED` guards. Fault settings can mask disconnects or force cache wait behavior, so tests must clean up debugfs settings after use.

Test signals: build with fault injection enabled and disabled to catch guard mismatches. Runtime tests should toggle each debugfs boolean and verify affected SUNRPC paths change behavior only under configured fault conditions.
