# sources/distributed-fs/ceph-client/tools/objtool/builtin-klp.c

Purpose: small subcommand dispatcher for objtool livepatch (`klp`) operations.

Important APIs/types/functions: `struct subcmd`, `subcmds[]` mapping `diff` to `cmd_klp_diff` and `post-link` to `cmd_klp_post_link`, `cmd_klp_usage()`, and `cmd_klp()`.

Control flow: strips the `klp` word from argv, requires a subcommand, scans the static table for a name match, and dispatches to the matched function. Unknown or missing subcommands print usage and exit.

State and persistence behavior: this file itself has no persistent state. The dispatched KLP commands may create or mutate ELF artifacts elsewhere.

Dependencies and integration points: includes parse-options, objtool core, and `objtool/klp.h`; integrated by the top-level objtool command dispatcher.

Risks: usage exits the process, so embedding would need care. Adding new KLP operations requires table updates and matching command implementation.

Test signals: invoking `objtool klp`, `objtool klp diff`, `objtool klp post-link`, and an unknown subcommand should exercise dispatch and usage behavior.
