## sources/distributed-fs/openafs/src/kauth/test/test_badtix.c

Purpose: `test_badtix.c` is a broad KA ticket and old-key regression test. It validates string-to-key vectors, live authentication, service ticket behavior, bad-key rejection, forged/altered ticket handling, auto password-change/old-key rollover, and optional execution under a new PAG.

Important APIs and functions: `print_entry` displays `kaentryinfo`; `TestOldKeys` exercises admin/TGS token validity across password/key changes and auto-CPW timing; `main` initializes error tables, validates `lcstring`/`ucstring` and `strcasecmp`, tests `ka_StringToKey` against hard-coded DES-key vectors, initializes rx/ka/ubik, fetches the `guest` key through loopback `KAM_GetPassword` or falls back to string-to-key, obtains TGS/admin tokens, checks jittered ticket times, tests `KAM_SetPassword` validation, constructs an AuthServer ticket with `tkt_MakeTicket`, damages a ticket byte, and expects rxkad rejection.

Control flow: the program first runs local deterministic conversion tests, then moves into live kaserver integration. `TestOldKeys` creates an alternate `krbtgt` principal, runs a timed vector of password changes, debug calls, token captures, and field updates, then later verifies all saved admin and TGS tokens still work with expected kvno behavior before deleting the alternate user.

State and persistence: mutates the KA database substantially: creates/deletes users, changes service passwords, changes fields/lifetimes, and may exec a supplied script after `setpag`. It also interacts with local token/PAG state and uses loopback kaserver connections.

Dependencies and integration points: requires running authentication and maintenance services, ubik, rxkad, DES, LWP/IOMGR timing, `kauth` RPCs, and configured test principals. It assumes a local host kaserver via explicit server list.

Risks: destructive against test KA state; not safe for production cells. Timing-sensitive old-key tests depend on auto-CPW intervals and sleeps. Hard-coded principal names and passwords require controlled test fixtures. The code uses legacy DES and old C patterns.

Test signals: success prints `All clear!`; intended failures include bad-key rejection and damaged-ticket rejection. The `test_kaserver` script invokes this with a temporary kaserver and a follow-on script to test bad ticket handling.
