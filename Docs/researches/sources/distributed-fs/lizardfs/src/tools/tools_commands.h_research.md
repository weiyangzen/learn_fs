# sources/distributed-fs/lizardfs/src/tools/tools_commands.h

Purpose: Declares command lookup/usage helpers and every tool entry point implemented under `src/tools`.

Important APIs/types/functions: `getCommand`; `printUsage`; `printTools`; `printArgs`; `append_file_run`, `check_file_run`, `dir_info_run`, `file_info_run`, `file_repair_run`, `snapshot_run`, eattr/goal/trashtime/quota/remove command functions.

Control flow: Header only declarations; runtime dispatch is implemented in `tools_commands.cc`.

State and persistence: None.

Dependencies and integration: Includes standard function/map/string/vector-related headers and is included by every command implementation and `main.cc`.

Risks and test signals: Adding a new command requires updating both this header and the registry/usage text. No direct tests in this subset.
