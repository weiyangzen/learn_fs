## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/KerberosIV/krb.h

Purpose: Kerberos V distribution's Kerberos IV compatibility API, exposing K4 structures and functions while integrating with K5 profile, com_err, and context types.

Important APIs/types/functions: Defines K4 principal/ticket sizing, `KTEXT_ST`, `AUTH_DAT`, `CREDENTIALS`, `MSG_DAT`, K4 error constants mapped through `KRBET_*`, sendauth options, profile section names for v4 realms, `key_proc_type`, `decrypt_tkt_type`, and globals such as `krb_ignore_ip_address`, `krb_debug`, and `krb5__krb4_context`. Prototypes cover ticket management (`dest_tkt`, `tkt_string`, `tf_*`), KDC/realm lookup, initial credential acquisition with password/preauth/creds, AP request/response generation and reading, service-key access, K5 conversion helpers, password change, profile access, default user, and Windows notification/time helpers.

Control flow: K4 compatibility callers acquire or locate ticket files, fetch TGTs/service tickets, build AP requests, validate server replies, and optionally bridge to K5 keyblocks/context. Realm and string-to-key behavior can be driven by K5 profile sections.

State and persistence: Ticket files persist through `TKT_FILE` or caller-set ticket strings; profile-backed realm settings are read through `profile.h`; globals hold debug, address-ignore, and K4-over-K5 context state.

Dependencies and integration points: Includes `<kerberosIV/des.h>`, `<kerberosIV/krb_err.h>`, and `<profile.h>`, with Windows additions from `<time.h>` and `win-mac.h` transitively. OpenAFS uses these declarations when KfW-backed Kerberos IV/AFS token compatibility is needed.

Risks: K4 and DES are legacy. This header intentionally exposes many private functions except on some Mac builds. ABI varies by `_WIN32`, Mac packing, and `KRB_PRIVATE`. Mixing it with older `krb4/krb.h` can cause conflicting prototypes and error-code semantics.

Test signals: Compile K4 compatibility users against this exact header; test profile-driven realm lookup, ticket-file set/get, KDC retry failures, AP request validation, K5 key conversion, password-change path, and Windows notification/time helpers.
