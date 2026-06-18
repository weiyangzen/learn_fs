## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/krb5/krb5.h

Purpose: Main MIT Kerberos 5 public API header vendored for Windows KfW: core scalar types, protocol structures, crypto/checksum APIs, credential-cache/keytab APIs, authentication APIs, configuration helpers, and generated error constants.

Important APIs/types/functions: Defines Kerberos scalar types (`krb5_context`, `krb5_principal`, `krb5_data`, `krb5_keyblock`, `krb5_creds`, tickets, authenticators, KDC requests/replies, auth context, ccache/keytab handles), encryption and checksum constants, protocol flags, preauth/authdata/message type constants, and many APIs. Major groups include crypto (`krb5_c_encrypt`, `krb5_c_decrypt`, random, checksum, string-to-key), credential caches (`krb5_cc_*`), keytabs (`krb5_kt_*`), contexts (`krb5_init_context`, `krb5_free_context`), credential acquisition (`krb5_get_init_creds_password/keytab`, `krb5_get_credentials`), AP/safe/private messages (`krb5_mk_req`, `krb5_rd_req`, `krb5_mk_safe`, `krb5_rd_priv`), principal parsing/copy/free helpers, auth-context setters, password change, realm/profile/config helpers, time helpers, and generated KRB5/KDB/KV5M error tables.

Control flow: A typical caller initializes a `krb5_context`, parses principals, opens or creates a credential cache/keytab, obtains or retrieves credentials, builds or validates protocol messages through auth contexts, and then frees every object through the corresponding `krb5_free_*` or close API. Error messages flow through com_err tables and optional per-context extended error strings.

State and persistence: Contexts own configuration/profile state; credential caches and keytabs can persist tickets/keys on disk or OS cache backends; replay caches and auth contexts hold sequence/time/subkey state; default realms, config files, and ccache names are process or profile mediated.

Dependencies and integration points: Includes Windows/Mac ABI support, com_err tables, profile integration, and optional K4 conversion declarations. GSS/Kerberos extensions include this header, and OpenAFS Windows authentication code depends on its ccache, keytab, enctype, and principal APIs.

Risks: Huge ABI surface with historical `KRB5_CALLCONV_WRONG` exports means calling convention must match binaries. Many returned allocations require exact free functions. Deprecated DES/old crypto APIs coexist with newer APIs. Generated error constants are stable API and should not be renumbered.

Test signals: Compile and link against target KfW DLLs; run context init/free, default realm/profile loading, password/keytab initial creds, ccache store/retrieve/iterate, keytab read/iterate, AP request validation, GSS integration, error-message lookup, and leak checks for all copy/free pairs.
