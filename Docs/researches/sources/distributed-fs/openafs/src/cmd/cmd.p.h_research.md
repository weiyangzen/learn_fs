# sources/distributed-fs/openafs/src/cmd/cmd.p.h

Purpose: prolog header included into generated `cmd.h` by `compile_et`. It defines the public command parser types, constants, and function prototypes.

Important APIs and types: defines parameter types (`CMD_FLAG`, `CMD_SINGLE`, `CMD_LIST`, `CMD_SINGLE_OR_FLAG`), syntax flags (`CMD_ALIAS`, `CMD_HIDDEN`, `CMD_IMPLICIT`), parameter flags (`CMD_OPTIONAL`, `CMD_EXPANDS`, `CMD_HIDE`, `CMD_NOABBRV`), `CMD_MAXPARMS`, `struct cmd_item`, `struct cmd_parmdesc`, `struct cmd_syndesc`, config binding structures, parser functions, option conversion functions, and raw config accessors.

Control flow and state: no executable logic. The layout of `cmd_syndesc` and `cmd_parmdesc` is a binary/source contract with `cmd.c` and all command-line tools.

Dependencies and integration: generated `cmd.h` appends error-table definitions after this prolog, so consumers get both parser declarations and `CMD_*` error code definitions.

Risks and tests: changing constants or structure layout can break ABI/source compatibility across OpenAFS tools. Coverage comes from all consumers and `src/cmd/test` binaries.
