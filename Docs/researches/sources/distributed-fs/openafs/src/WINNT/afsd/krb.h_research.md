# sources/distributed-fs/openafs/src/WINNT/afsd/krb.h

Purpose: provides a Kerberos v4 compatibility header excerpted from MIT Kerberos material for OpenAFS Windows code that still references legacy ticket, principal, and protocol constants.

Important APIs/types/functions: defines success/failure constants, Kerberos name component sizes, ticket text size (`MAX_KTXT_LEN`), `struct ktext`/`KTEXT`/`KTEXT_ST`, retry and timeout constants for KDC communication, default ticket lifetime, clock-skew tolerance, and many KDC/library error codes. It includes `krb_prot.h` and declares a legacy `static send_to_kdc(KTEXT pkt, KTEXT rpkt)` prototype without an explicit return type.

Control flow: there is no executable control flow. Including code uses these constants and packet text types when building or parsing legacy Kerberos v4 protocol data.

State/persistence: no runtime state. The constants define fixed wire-buffer sizes and error-code contracts. `struct ktext` contains an `mbz` field intended to remain zero as a guard against runaway strings.

Dependencies/integration: depends on `<hcrypto/des.h>` for DES-era Kerberos support and on `krb_prot.h` for wire message macros and message types. It integrates with older AFS authentication paths that predate Kerberos v5-only APIs.

Risks: Kerberos v4 and DES are obsolete security mechanisms; any live authentication use should be treated as legacy compatibility. Fixed-size principal fields can truncate longer modern names. The K&R-style implicit-int `static send_to_kdc` declaration is incompatible with modern strict C modes and can hide ABI mistakes.

Test signals: compile with modern MSVC/C warning levels, verify no new code depends on v4-only authentication, and regression-test any legacy token path that still maps these error codes.
