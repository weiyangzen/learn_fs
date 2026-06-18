## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/KerberosIV/kadm_err.h

Purpose: Newer generated K4 administration error table header using the K5 com_err `struct error_table` model.

Important APIs/types/functions: Includes `<com_err.h>`, defines the `KADM_*` constants from `KADM_RCSID` through newer values such as `KADM_NOT_SERV_PRINC` and `KADM_REALM_TOO_LONG`, sets `ERROR_TABLE_BASE_kadm`, and declares `extern const struct error_table et_kadm_error_table`. On non-Windows it declares `initialize_kadm_error_table`; on Windows initialization is a no-op macro.

Control flow: Error table lookup uses the static `et_kadm_error_table`; non-Windows callers can register it explicitly, while Windows builds rely on static or DLL-provided table availability.

State and persistence: Error table registration is process-global when used. No durable storage.

Dependencies and integration points: Uses `krb5/com_err.h` semantics and is consumed by KerberosIV compatibility/admin code.

Risks: This header differs from `krb4/kadm_err.h` in initialization signature and constant set. Including the wrong one can produce link errors or missing newer error constants.

Test signals: Verify constants and base values; compile with K5 `com_err.h`; assert `error_message(KADM_*)` works when table registration is expected; Windows tests should ensure the no-op initializer is compatible with the DLL.
