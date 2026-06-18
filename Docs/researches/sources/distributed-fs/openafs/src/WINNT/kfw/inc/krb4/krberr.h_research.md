## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/krberr.h

Purpose: Generated Kerberos IV error-table registration shim for the older K4 com_err mechanism.

Important APIs/types/functions: Declares `initialize_krb_error_func(err_func func, HANDLE *)` on Windows or `initialize_krb_error_func(err_func func, struct et_list **)` elsewhere. Defines `ERROR_TABLE_BASE_krb = 39525376L`, `init_krb_err_func(erf)`, `krb_err_base`, and external `_et_list`.

Control flow: K4 code registers an `err_func` that translates offsets into text, then com_err lookup uses the registered table/list state.

State and persistence: Mutates process-global error table list state. No persistent storage.

Dependencies and integration points: Requires `err_func` from `krb4/com_err.h` and Windows `HANDLE` when compiled for Windows. Used with `krb_err_txt` and K4 error reporting.

Risks: No include guard and a generic `_et_list` declaration can collide with other generated K4 error tables. It registers a function rather than a static `struct error_table`, unlike newer K5 headers.

Test signals: Verify `init_krb_err_func` installs the expected translator, that `ERROR_TABLE_BASE_krb` aligns with K4 error offsets, and that multiple generated tables can coexist in target link mode.
