# sources/distributed-fs/ceph-client/net/sctp/endpointola.c

Purpose: implements the SCTP endpoint abstraction for a socket. Endpoints own bind addresses, association lists, input queue handling before association lookup, AUTH defaults, cookie keys, buffer policies, and matching/peeled-off checks.

Important APIs/types/functions: `gen_cookie_auth_key()` prepares a random HMAC-SHA256 cookie key and wipes raw bytes. `sctp_endpoint_init()` configures endpoint policy, AUTH, inqueue, bind address, association list, socket callbacks, buffer policies, cookie key, null shared key, feature flags, and socket/net references. `sctp_endpoint_new/free/hold/put/destroy/destroy_rcu()` manage lifetime, unhashing, auth/bind/inqueue cleanup, port release, RCU final free, and object counters. `sctp_endpoint_add_asoc()` links associations and listener backlog. `sctp_endpoint_is_match()`, `sctp_endpoint_lookup_assoc()`, and `sctp_endpoint_is_peeled_off()` provide lookup helpers. `sctp_endpoint_bh_rcv()` drains endpoint input and dispatches chunks to the state machine.

Control flow: creation initializes auth if enabled, creates a null key, sets SCTP socket callbacks and write queue flag, generates cookie auth material, and holds the socket. Incoming chunks without known association are processed by endpoint bottom-half work. The worker handles first AUTH+COOKIE-ECHO specially, retries association lookup after cookie processing may create one, enforces AUTH-required chunk placement, updates stats and transport timestamps, and calls `sctp_do_sm()`. Free marks dead, closes socket state, unhashes, and drops the reference; final cleanup waits for refs/RCU.

State and persistence: volatile endpoint refcount/dead flag, inqueue, bind address list, association list, socket/net refs, cookie auth key, auth parameter/key lists, buffer policies, and SCTP feature flags. Cookie key material is explicitly zeroed on destruction.

Dependencies/integration: SCTP socket callbacks, endpoint hash, bind address management, AUTH, inqueue scheduling, state machine, association and transport lookup, global association checks for peeloff, port binding, net namespace defaults, and IPv6/device matching.

Risks: refcount/RCU correctness is critical during endpoint destruction and lookup. AUTH-before-COOKIE-ECHO clone/skip ordering affects authenticated setup. Association lookup returns under the established RCU contract; callers must not outlive it incorrectly. Peeled-off detection assumes socket lock stability. Socket callback replacement must remain compatible with SCTP semantics.

Test signals: create/free with auth on/off, ADDIP auth chunk additions, cookie key zeroing instrumentation, namespace/device/port/address endpoint match, association add/backlog accounting, endpoint inqueue COOKIE-ECHO creation path, AUTH-required discard, peeled-off detection, free with queued chunks, and port release on final destroy.
