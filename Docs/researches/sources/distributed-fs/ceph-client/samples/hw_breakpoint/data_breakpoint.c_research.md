# sources/distributed-fs/ceph-client/samples/hw_breakpoint/data_breakpoint.c

Purpose: kernel module that installs a write hardware breakpoint on a named kernel symbol, defaulting to `jiffies`.

Important APIs/functions: `module_param_string(ksym, ...)`, `__symbol_get`, `__symbol_put`, `hw_breakpoint_init`, `register_wide_hw_breakpoint`, `unregister_wide_hw_breakpoint`, and `sample_hbp_handler`.

Control flow: init resolves the symbol address, initializes a `perf_event_attr` for 4-byte write watchpoint, registers per-CPU breakpoints, and logs installation. Handler prints that the symbol changed and dumps stack. Exit unregisters and releases the symbol.

State and persistence: global per-CPU `perf_event` pointer and held symbol reference while loaded.

Dependencies and integration: perf hardware breakpoints, kallsyms/exported symbol resolution, architecture breakpoint support.

Risks: default `jiffies` changes frequently and can produce heavy stack dumps. Breakpoint length is fixed at four bytes and may not match all symbol types. `__symbol_get` only works for exported symbols.

Test signals: load with a low-frequency writable exported symbol, write or wait for changes, inspect handler stack dumps, and unload.
