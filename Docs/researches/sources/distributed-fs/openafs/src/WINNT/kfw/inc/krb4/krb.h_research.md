## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb4/krb.h

Purpose: Main legacy Kerberos IV public header: constants, packet structures, credential/ticket-file types, error-code aliases, byte-swap macros, and K4 function prototypes.

Important APIs/types/functions: Defines principal sizing (`ANAME_SZ`, `REALM_SZ`, `MAX_K_NAME_SZ`), ticket text `KTEXT_ST`, `AUTH_DAT`, `CREDENTIALS`, `MSG_DAT`, ticket-file header access via `tkt_ptr()`, KDC and client error constants, sendauth option bits, and aliases from `krb_*` names to older implementation names. Prototypes include ticket-file functions (`tf_init`, `tf_get_cred`, `tf_save_cred`, `tf_close`), credential acquisition (`krb_get_pw_in_tkt`, `krb_in_tkt`, `krb_get_cred`), request construction (`krb_mk_req`), KDC transport (`send_to_kdc`), realm/host helpers, and lifetime conversion.

Control flow: Applications initialize or locate a ticket store, obtain initial credentials, retrieve service tickets, build AP requests, and validate replies using structures declared here. Ticket file operations use `TKT_FILE`/`TKT_ENV` and mutable process state behind `tkt_ptr()`.

State and persistence: K4 tickets persist in ticket files or Kerberos memory mode (`KM_TKFILE`, `KM_KRBMEM`). Globals include `krb_err_txt`; debug flags and ticket-file state live in the implementation.

Dependencies and integration points: Includes `<conf.h>` and `<des.h>`. Windows builds depend on `BOOL`, `PASCAL`, and `FAR`; OpenAFS token conversion paths rely on `CREDENTIALS`, DES keys, and K4 service-ticket calls.

Risks: Fixed-size buffers and string APIs are truncation-prone. Byte-swap macros mutate arguments and are unsafe for expressions. DES/K4 protocol use is legacy. Prototypes differ under `WINDOWS` versus other builds, so ABI mismatches are easy.

Test signals: Compile Windows and non-Windows declaration paths; exercise ticket-file lifecycle, principal parsing, realm lookup, lifetime conversion, KDC retry handling, and AP request creation with known K4 test vectors.
