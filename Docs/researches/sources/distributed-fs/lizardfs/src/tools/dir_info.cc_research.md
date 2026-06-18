# sources/distributed-fs/lizardfs/src/tools/dir_info.cc

Purpose: Implements `lizardfs dirinfo`, a directory statistics reporter for LizardFS objects.

Important APIs/types/functions: `dir_info_run`; static usage and per-path query helpers; legacy master request/response packing; number formatting through `print_number`.

Control flow: The command parses human-readable output flags, resolves each target through `open_master_conn`, sends the directory-info request to the master, validates response type/query id/status, and prints counts/sizes for files, directories, chunks, and storage usage.

State and persistence: Read-only. It reflects master metadata and chunk accounting but does not mutate state.

Dependencies and integration: Uses legacy socket/datapack helpers, `tools_common_functions`, and `mfserr`. It fits the same command dispatch path as the other tools.

Risks and test signals: Like other legacy tools, it hand-parses response length and fields, so protocol drift can produce wrong output or rejection. No direct tests in this subset.
