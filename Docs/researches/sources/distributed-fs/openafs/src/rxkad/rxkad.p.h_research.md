# sources/distributed-fs/openafs/src/rxkad/rxkad.p.h

Purpose: Main rxkad public-private protocol header for ticket sizes, principal structures, security levels, ticket type numbers, and stats indexing macros.

Important APIs/types: Defines `MAXKTCTICKETLIFETIME`, ticket length bounds, principal name bounds, clock skew, `ktc_encryptionKey`, `ktc_principal`, `rxkad_type`, `rxkad_level`, `rxkad_clear`, `rxkad_auth`, `rxkad_crypt`, ticket type values for Kerberos v5 and v5 encrypted-part-only tickets, and `rxkad_get_key_enctype_func`.

Control flow and state: No runtime flow. Constants drive validation in ticket decode, security negotiation in client/server challenge processing, packet security header sizes, and stats index mapping.

Dependencies and integration: Includes `<rx/rxkad_prototypes.h>` after defining core types. This header is the canonical include behind installed `rx/rxkad.h` style users.

Risks: Size constants are wire and ABI limits. `MAXKTCTICKETLEN` is large enough for v5 tickets, so all stack buffers using it are security-relevant. Stats macros sanitize invalid type/level inputs to index 0, which avoids bounds errors but can hide bad callers.

Test signals: Stress command parsing exercises level names and ticket creation; v4/v5 ticket routines enforce the bounds defined here.
