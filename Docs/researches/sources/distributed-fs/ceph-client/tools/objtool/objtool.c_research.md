# sources/distributed-fs/ceph-client/tools/objtool/objtool.c

Purpose: Provides objtool top-level object state and command dispatch shared by check, ORC, livepatch, and architecture hooks.

Important APIs/types/functions: `objtool_pv_add`, `main`, `objtool_file`.

Control flow: `objtool_open_read()` opens one mutable ELF and initializes analysis lists/hash tables; `main()` initializes signal/subcmd/pager support, dispatches `objtool klp`, or runs the normal builtin path.

State and persistence behavior: Process-global `debug`, `indent`, and static `objtool_file file` hold transient run state; output persistence is delegated to ELF writers.

Dependencies and integration points: Uses libsubcmd, builtin option state, ELF helpers, Linux list/hash utilities, and signal handling.

Risks: The static single-file object prevents multi-file processing in one process; paravirt tracking is gated by `opts.noinstr` and assumes pv state allocation elsewhere.

Test signals: CLI dispatch for normal and `klp` subcommands, repeated open rejection, paravirt add edge cases, and top-level directory discovery from installed binary layout.

Source coverage: researched from the complete local file (126 lines, 2487 bytes).
