## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/kadm_err.h

Purpose: Generated Kerberos administration error table header for the older K4 com_err ABI.

Important APIs/types/functions: Defines `KADM_*` numeric constants from `KADM_RCSID` through `KADM_PW_MISMATCH`, with `ERROR_TABLE_BASE_kadm = -1783126272L`. Declares `initialize_kadm_error_table(HANDLE *)` on Windows or `initialize_kadm_error_table(struct et_list **)` elsewhere. Compatibility macros map `init_kadm_err_tbl()` and `kadm_err_base`.

Control flow: Callers initialize the table into `_et_list`, then pass returned error codes to `com_err`/`error_message`.

State and persistence: Error table registration mutates the process-global `_et_list`. No durable persistence.

Dependencies and integration points: Depends on the K4 com_err error-list model and Windows `HANDLE` when `WINDOWS` is defined. It is consumed by admin-client code and any K4/Kadmin compatibility path that reports password or database errors.

Risks: The header is generated but lacks include guards. It declares a global `_et_list`, so combining multiple generated K4 error headers can create ownership and linkage confusion. The Windows signature differs from newer MIT com_err headers.

Test signals: Compile together with `krb4/com_err.h`; verify one-time table initialization and message lookup for representative admin failures; assert constants remain stable for binary compatibility.
