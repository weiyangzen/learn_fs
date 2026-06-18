## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/KerberosIV/krb_err.h

Purpose: Generated Kerberos IV error table for the K5 com_err model.

Important APIs/types/functions: Includes `<com_err.h>`, defines `KRBET_*` constants from `KRBET_KSUCCESS` through reserved slots and named K4 failures, sets `ERROR_TABLE_BASE_krb = 39525376L`, and declares `extern const struct error_table et_krb_error_table`. Non-Windows builds also declare `initialize_krb_error_table`.

Control flow: `KerberosIV/krb.h` maps legacy small K4 error numbers with `KRB_ET(x)`, while com_err users can look up full table codes through `et_krb_error_table`.

State and persistence: Optional table registration mutates process-global com_err state. No durable state.

Dependencies and integration points: Must be paired with K5 `com_err.h` and `KerberosIV/krb.h`. It is not ABI-equivalent to `krb4/krberr.h`.

Risks: Very large generated macro surface increases collision risk. Windows no-op initialization assumes the table is already linked into the library. Using `KRBET_*` full codes where legacy offset codes are expected changes behavior.

Test signals: Verify `KRB_ET` mappings in `KerberosIV/krb.h`, message lookup for representative failures (`KDC`, `GC`, `RD_AP`, ticket-file errors), and compile/link behavior on Windows where initializers are macros.
