<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/errtrans.pm -->
# sources/distributed-fs/openafs/src/tests/OpenAFS/errtrans.pm

## Purpose
Translates between symbolic AFS/com_err/POSIX/Rx/volume error names, numeric error codes, and human-readable strings for the AFStools test environment.

## Important APIs, Types, And Functions
Exports `errcode` and `errstr`. Private helpers `_tbl_to_num`, `_num_to_tbl`, `_load_system_errors`, and `_load_error_table` implement com_err package encoding, reverse decoding, POSIX `errno.h` scanning, and `.et` table parsing. Tables `%Vol_Codes`, `%Vol_Desc`, `%Rx_Codes`, and `%Rx_Desc` cover special OpenAFS values.

## Control Flow
`errcode($pkg,$code)` encodes a com_err table/code directly. `errcode($name)` lazily loads system errors, checks volume/Rx/system maps, tries `POSIX::constant`, and then loads every error table in `$err_table_dir`. `errstr` handles Rx first, optional volume errors, plain system errors, and then com_err table lookups.

## State And Persistence
State is in-memory caches: `%Codes`, `%Desc`, `%Have_Table`, and `%did_include`. Persistent input is `/usr/include` headers and `$err_table_dir` table files.

## Dependencies And Integration Points
Depends on `OpenAFS::config`, `OpenAFS::util`, `Symbol`, and `POSIX`. The module supports wrapper error checking and test diagnostics where OpenAFS tools return numeric com_err/Rx values.

## Risks And Test Signals
The `.et` parser is permissive but simplistic and can silently return on malformed files. Recursive include scanning of `/usr/include` may be platform-sensitive. Test signals include translating known POSIX names, Rx constants, volume constants, table-defined symbols, and unknown values returning `-999` or `Unknown code`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/errtrans.pm -->
