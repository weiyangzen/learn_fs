# sources/distributed-fs/ceph-client/tools/lib/subcmd/help.h

Purpose: Defines command-name storage structures and help/listing API declarations for libsubcmd.

Important APIs/types/functions: `struct cmdnames` contains allocation/count plus an array of flexible-array `struct cmdname` entries. `mput_char()` prints repeated characters. Declares command-list lifecycle, sorting, filtering, membership, loading, and listing functions.

Control flow: Header declarations support callers creating zero-initialized `cmdnames`, populating via `load_command_list()` or `add_cmdname()`, sorting/filtering, printing, and cleaning.

State and persistence: Structures store heap pointers managed by `help.c`; no persistence.

Dependencies/integration: Includes `sys/types.h` and `stdio.h`, and is installed as a libsubcmd public header.

Risks: Callers must initialize `struct cmdnames` to zero and later call `clean_cmdnames()`. `mput_char()` is inline and writes directly to stdout.

Test signals: Compile API usage with static initializers and dynamic lists; verify ABI expectations for flexible array allocation.
