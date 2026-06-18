## sources/distributed-fs/openafs/src/kauth/test/test_getticket.c

Purpose: despite its filename, this source identifies itself as `test_rxkad_free` and focuses on ticket lifetime/error behavior for AFS service ticket acquisition. It mutates KA entry flags, expirations, and lifetimes, authenticates through user-level APIs, and verifies resulting AFS token lifetimes and expected failure codes.

Important APIs and functions: `Crash` restores the original AFS token before exiting; `PrintRxkadStats` reports rxkad object/connection counters; `SetFields` wraps `KAM_SetFields` for flags, expiration, and lifetime changes; `CheckLife` compares token end times either exactly or through Kerberos v4 lifetime quantization; `GetTokenLife` calls `ka_UserAuthenticateLife` and validates the installed AFS token; `Main` obtains an admin token and ubik maintenance connection, applies a series of field changes, and tests success/failure outcomes.

Control flow: after parsing admin credentials/cell/server options, it saves the current AFS token, obtains a maintenance token, normalizes flags/lifetimes/expirations for `afs`, `krbtgt`, and the test user, and checks default/user/server/TGS lifetime limiting. It then restores the original token before negative tests for expired users, expired `afs`, `KAFNOSEAL`, `KAFNOTGS`, and old TGS reuse. With `-patient`, it waits about five minutes to test aging of an old TGS ticket.

State and persistence: mutates KA database entries for service and user principals and local token cache state. It tries to restore saved tokens and fields, but failures can leave altered test state.

Dependencies and integration points: requires a live KA maintenance service, cache-manager token store, ubik, rxkad stats, command parser, and admin credentials.

Risks: unsafe outside a controlled test cell because it changes flags and expirations on service principals such as `afs` and `krbtgt`. The source has minor defects such as `fprintf("Can't get admin token\n")` without a stream in one branch. Timing and Kerberos lifetime rounding make assertions sensitive to wall-clock behavior.

Test signals: prints expected lifetime checks and `All Okay` on success. It is buildable through the makefile as `test_getticket`, but not in default `all`.
