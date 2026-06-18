## sources/distributed-fs/openafs/src/WINNT/kfw/inc/leash/leashwin.h

Purpose: Public Windows Leash API for Kerberos login/password dialogs, ticket operations, ticket status display, and user-default configuration.

Important APIs/types/functions: Includes `<krb.h>`, defines dialog type constants, `LSH_DLGINFO`, versioned `LSH_DLGINFO_EX`, optional wide-character `NETID_DLGINFO`, `TICKETINFO`, ticket state constants, and function prototypes for kinit/change-password dialogs, password check/change, `Leash_kinit*`, `Leash_klist`, `Leash_kdestroy`, error retrieval, renew/import, help-file access, default reset, and many registry-backed default getters/setters/resets for lifetime, renewability, forwardable, addresses, proxiable, public IP, KRB4 use, option hiding, lock file locations, uppercase realm, MSLSA import, and preserving settings.

Control flow: UI callers populate dialog info structs, invoke modal Leash dialogs or direct kinit/change-password functions, list/destroy/renew/import tickets, and adjust defaults through registry-oriented setters.

State and persistence: Ticket operations mutate Kerberos credential caches. Default setters alter current-user registry configuration. Dialog structs carry both input and output fields with explicit size-version macros for ABI negotiation.

Dependencies and integration points: Depends on Windows types, K4/Kerberos declarations from `<krb.h>`, NetIDMgr-compatible wide structs when not building NetIDMgr, and Leash DLL exports.

Risks: Struct versioning is size-based and sensitive to packing/pointer width. ANSI `LPSTR` fields coexist with fixed internal buffers. Registry mutations and ticket destruction are user-visible. K4 include path choice affects `MAX_K_NAME_SZ`.

Test signals: Dialog ABI tests for V1/V2/V3 sizes, kinit/change-password success and cancellation, klist states for no/expired/good tickets, registry default round trips, help file set/get, and 32/64-bit struct layout checks.
