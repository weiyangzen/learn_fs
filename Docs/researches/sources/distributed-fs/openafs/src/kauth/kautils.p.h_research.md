# sources/distributed-fs/openafs/src/kauth/kautils.p.h

## Purpose
Defines the public kauth client utility API, service identifiers, protocol labels, authentication macros, and wire-format request/answer structures.

## Important APIs, Types, And Functions
The header declares token acquisition, server connection, authentication, ticket retrieval, password change, string-to-key, password reading, login-name parsing, initialization, cell/realm helpers, byte/time utilities, user-authentication wrappers, debug key cache access, and ticket-file helpers. It defines `Date`, `KA_TIMESTR_LEN`, user-auth flag bits, password-control bits, KA service IDs, builtin principal names, labels such as `gTGS`, `gADM`, `CPWl`, and `gtkt`, and structs for TGT, ticket, change-password, and get-ticket messages.

## Control Flow
There is no implementation flow. The macro wrappers build versioned calls to `ka_UserAuthenticateGeneral`, and the structs define the payloads encrypted and decrypted by client and server code.

## State And Persistence
No state is stored here. The declared APIs manipulate token caches, Ubik connections, passwords, and ticket files elsewhere.

## Dependencies And Integration Points
It includes authentication, Rx/XDR, Ubik, cellconfig, and afsutil headers. It is the central public header for `klog`, `kpasswd`, admin tools, token helpers, and server request code.

## Risks And Test Signals
Risks include ABI drift in wire structures, label or service-ID mismatch with `kaprocs.c` and generated RPC code, macro compatibility, and `Date` remaining 32-bit. Test signals include client/server authentication interoperability, old and new ticket-answer formats, password-change request/answer layout, public library symbol builds, and cross-platform struct packing.
