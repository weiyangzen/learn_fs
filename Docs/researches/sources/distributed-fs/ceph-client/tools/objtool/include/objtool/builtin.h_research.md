# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/builtin.h

Purpose: shared declaration of objtool command options and top-level command entry points.

Important APIs/types/functions: `struct opts` groups action flags and option flags, including ORC, CFI, IBT, retpoline, rethunk, noinstr, uaccess, disassembly, dry-run, output, stats, trace, verbose, werror, and wide output. Declares global `opts`, `cmd_parse_options()`, `objtool_run()`, `make_backup()`, and `cmd_klp()`.

Control flow: none; consumers branch heavily on the global flags declared here.

State and persistence behavior: `opts` is global mutable process state set by `builtin-check.c` and read by analysis, ELF, disassembly, trace, and architecture code. Some flags cause persistent ELF changes.

Dependencies and integration points: includes `subcmd/parse-options.h` and is included across objtool modules.

Risks: global options make feature interactions implicit. Adding a flag requires updates to parser, validation, and all consumers.

Test signals: CLI option parsing tests should verify each field affects the expected downstream behavior and rejects invalid combinations.
