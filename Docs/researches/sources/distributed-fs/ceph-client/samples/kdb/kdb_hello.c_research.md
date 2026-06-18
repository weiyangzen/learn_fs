# sources/distributed-fs/ceph-client/samples/kdb/kdb_hello.c

Purpose: registers a simple dynamic KDB command named `hello`.

Important APIs/functions: `kdbtab_t`, `kdb_register`, `kdb_unregister`, `kdb_printf`, and `KDB_ARGCOUNT`.

Control flow: init registers the command. The command prints `Hello world!` or a provided string, though the argument-count condition appears inconsistent because `argc > 1` rejects the documented optional string. Exit unregisters the command.

State and persistence: KDB command table entry while loaded.

Dependencies and integration: requires KDB debugger support and module loading.

Risks: sample command logic may reject one-argument usage depending on KDB `argc` semantics. KDB is a privileged debugger interface.

Test signals: load module, enter KDB, run `hello` and `hello name`, verify output or argument-count behavior, then unload.
