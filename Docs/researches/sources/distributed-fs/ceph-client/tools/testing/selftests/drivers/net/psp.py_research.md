# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/psp.py

Purpose: Tests PSP-capable network drivers over the generic netlink PSP family, covering device enumeration, key rotation, associations, data transfer, MSS adjustment, stale keys, and device removal.

Important APIs/functions: Uses `NetDrvEpEnv`, `PSPFamily`, responder process `psp_responder`, and TCP sockets. Helpers manage the control socket (`_send_with_ack`, `_make_clr_conn`, `_make_psp_conn`), SPI/key exchange, careful nonblocking send, receive-length checks, and PSP device initialization. Test cases are selected by name prefixes `dev_`, `assoc_`, `data_`, and `removal_`.

Control flow: Main deploys and starts the responder on the remote endpoint, opens a control socket, builds per-version/per-IP data tests, and runs all matching cases. Device setup discovers the PSP dev id for the local ifindex and enables supported versions with deferred restoration.

State and persistence: Mutates PSP device enabled-version state, per-socket Rx/Tx associations, key rotation counters, TCP sockets, responder process state, and netdevsim reload state for removal tests. Defers restore PSP enablement and closes sockets.

Dependencies and integration: Requires kernel PSP generic netlink support, responder binary, local/remote endpoint connectivity, and netdevsim for reload/removal-specific tests.

Risks: Many tests depend on precise extack errors and version constants. Bad-key/stale-key tests intentionally create queued unsent data, so timing and socket buffer behavior matter. Responder/control protocol must stay in sync with `psp_responder.c`.

Test signals: PASS includes expected device ids/stats, key rotation counter increments and SPI top-bit changes, valid and invalid association behavior, successful encrypted data delivery, bad/stale data not delivered, MSS reduced by PSP overhead after Tx association, and no crash/leak through device removal.
