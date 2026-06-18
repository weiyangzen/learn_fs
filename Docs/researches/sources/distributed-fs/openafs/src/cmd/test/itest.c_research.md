# sources/distributed-fs/openafs/src/cmd/test/itest.c

Purpose: interactive command parser test shell. It registers `apple`, `pear`, alias, and `quit`, then reads lines, tokenizes them with `cmd_ParseLine`, dispatches, and frees argument vectors.

Important APIs: exercises `initialize_CMD_error_table`, `cmd_CreateSyntax`, `cmd_AddParm`, `cmd_Seek`, `cmd_CreateAlias`, `cmd_ParseLine`, `cmd_Dispatch`, `cmd_FreeArgv`, and `afs_error_message`.

Control flow and state: loops on `gets(tline)`, prints a prompt, parses into a local `tv` array, dispatches, and reports parse/dispatch errors. `quit` exits the process.

Dependencies and integration: uses com_err to report generated cmd error messages and is built as a cmd test binary.

Risks and tests: uses unsafe `gets`, making it unsuitable for production or fuzzing without replacement. It tests quoted-line tokenization and repeated dispatch cleanup better than the one-shot tests.
