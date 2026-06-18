# sources/distributed-fs/openafs/src/WINNT/tests/torture/include/common.h

Purpose: shared constants, data structures, and command metadata for the Windows torture harness.

Important APIs and types: defines path buffer sizes, file attribute bits, Open/Create option bits, command IDs from `CMD_CLOSE` through `CMD_NONAFS`, `NTSTATUS`, `pstring`, `fstring`, `file_info`, `cmd_struct`, `EXIT_STATUS`, `PARAMETERLIST`, and `FTABLE`. `cmd_names[]` maps command IDs to report names, disable-option names, and underlying API descriptions.

Control flow: no runtime control flow, but command IDs drive dispatch, timing, logging, and statistics aggregation across `nbio.c` and `output.c`.

State and persistence: `cmd_struct` stores count, error count, millisecond remainder, min/max/total seconds, sum of squares, and error time. `FTABLE` persists logical script handle to Win32 `HANDLE` mappings for each thread.

Dependencies and integration: included by `includes.h`, `proto.h`, `nbio.c`, and `output.c`. `CMD_MAX_CMD` must remain synchronized with `cmd_names` and command arrays.

Risks and test signals: `cmd_names` is defined `static` in the header, so every translation unit gets its own copy. Off-by-one errors are possible because loops run `i <= CMD_MAX_CMD` and `cmd_names` has a null sentinel. Statistics output consistency is the main signal.
