# sources/distributed-fs/ceph-client/tools/verification/rv/include/in_kernel.h

Purpose: `in_kernel.h` declares the interface from the top-level `rv` CLI into in-kernel monitor support.

Important APIs: `ikm_list_monitors(char *container)` lists available monitors, optionally scoped to a container; `ikm_run_monitor(char *monitor, int argc, char **argv)` runs a named in-kernel monitor with monitor-specific options.

Control flow and integration: `rv.c` calls these functions for `rv list` and `rv mon`. The implementation in `src/in_kernel.c` maps CLI actions onto tracefs `rv/` files.

State, dependencies, risks, and tests: the header has no state. It depends on callers obeying root and tracefs availability requirements handled elsewhere. Risks are sparse documentation and return-code semantics that require consulting the implementation. Test signals are successful compile/link and `rv list`/`rv mon` reaching in-kernel monitor logic.
