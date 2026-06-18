# sources/distributed-fs/ceph-client/tools/perf/util/include/asm/system.h

Purpose: empty compatibility header for code imported into perf tools that includes `asm/system.h`.

Important APIs and types: none.

Control flow: none.

State and persistence: none.

Dependencies and integration: belongs to the local tools include shim layer. It prevents userspace perf builds from depending on removed or kernel-only `asm/system.h` content.

Risks: because it is empty, it is safe only for includes that do not require actual barrier, system, or architecture operations. New code should include the precise userspace or Linux helper header it needs.

Test signals: compile-only. Any real dependency would surface as missing macro/function build errors in consumers.
