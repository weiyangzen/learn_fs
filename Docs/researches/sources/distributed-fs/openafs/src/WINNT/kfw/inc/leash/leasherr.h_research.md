## sources/distributed-fs/openafs/src/WINNT/kfw/inc/leash/leasherr.h

Purpose: Generated error table for Leash, the Windows Kerberos credential UI/helper layer.

Important APIs/types/functions: Defines `LSH_*` errors covering singleton enforcement, invalid principal/instance/realm, EOF, expiry, bad characters, Winsock/time-server/socket/connect failures, time receive/set failures, and `LSH_ALREADY_SETTIME`. Declares `initialize_lsh_error_table(struct et_list **)`, sets `ERROR_TABLE_BASE_lsh`, and compatibility macros `init_lsh_err_tbl()` and `lsh_err_base`.

Control flow: Leash code initializes the table and reports these codes through com_err-style lookup.

State and persistence: Error-table initialization mutates process-global `_et_list`. No durable state.

Dependencies and integration points: Depends on old com_err `struct et_list` and is used by Leash UI/API calls in `leashwin.h`.

Risks: No include guard and reliance on `_et_list` can collide with other old generated tables. The declarations match older com_err, not the newer K5 `struct error_table` model.

Test signals: Compile with the intended com_err header, initialize the table, look up representative Leash errors, and verify values remain stable for external callers.
