# Group Research: group_1372_openbsd_src_sources_os_bsd_openbsd_src_sbin_isakmpd_dpd_c_sources_o_d3e98077ebc4

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/dpd.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/dpd.c

Implements RFC 3706 Dead Peer Detection for isakmpd phase-1 SAs. It advertises DPD with a VENDOR ID payload, detects peer support on inbound vendor payloads, handles R_U_THERE/R_U_THERE_ACK notify messages, and runs timer-driven liveness probes after phase 1 completes.

Key behavior:
- `dpd_add_vendor_payload()` allocates an ISAKMP vendor payload containing the RFC 3706 DPD vendor ID plus version bytes.
- `dpd_check_vendor_payload()` compares incoming vendor payload bodies and sets `EXCHANGE_FLAG_DPD_CAP_PEER` on the current exchange.
- `dpd_start()` enables DPD on an ISAKMP SA only when `General/DPD-check-interval` is positive.
- `dpd_handle_notify()` validates sequence numbers, replies to R_U_THERE, marks ACKs as handled, and resets the DPD timer when peer activity is confirmed.
- `dpd_event()` first checks kernel IPsec SAs for recent `last_used` activity via PF_KEY; only if no child SA traffic was recently observed does it send R_U_THERE.
- `dpd_check_event()` retries up to `DPD_RETRANS_MAX`; on failure it deletes all ready phase-2 SAs matching the phase-1 IDs and then deletes the ISAKMP SA.

Important dependencies:
- SA lifetime and lookup: `sa_find()`, `sa_delete()`, `SA_FLAG_DPD`, `SA_FLAG_READY`.
- Kernel activity: `pf_key_v2_get_kernel_sa()`.
- Timers: `timer_add_event()`, `timer_remove_event()`.
- Messages: `message_send_dpd_notify()`, payload macros from `isakmp_fld.h`.

Notable implementation detail:
- The initial DPD sequence is randomized with the MSB cleared, then incremented.
- Duplicate inbound R_U_THERE packets are tolerated until the duplicate count reaches `DPD_RETRANS_MAX`.
- `dpd_find_sa()` compares `id_i`/`id_r` using the candidate SA’s ID lengths; callers rely on matching phase-2 SAs with ready state.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/dpd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/dpd.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/dpd.h

Public interface for Dead Peer Detection support.

Exports:
- `dpd_add_vendor_payload(struct message *)`
- `dpd_check_vendor_payload(struct message *, struct payload *)`
- `dpd_handle_notify(struct message *, struct payload *)`
- `dpd_start(struct sa *)`

The header forward-declares `message`, `payload`, and `sa`, keeping DPD integration independent of the full message/SA definitions at include sites.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/dpd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/exchange.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/exchange.c

Core exchange manager for isakmpd. It owns exchange allocation, lookup, validation scripts, initiator/responder dispatch, finalization, retransmit bookkeeping, nonce/certificate request helpers, and high-level phase establishment.

Key responsibilities:
- Maintains a global hash table of `struct exchange` entries keyed by cookies and, for phase 2, message ID.
- Defines payload validation scripts for Base, Identity Protection/Main Mode, Authentication Only, Aggressive, Informational, Transaction, and DOI-specific exchange types.
- `exchange_run()` drives the exchange state machine by alternating between outbound generation and inbound validation/DOI handler execution. It advances `step` and `exch_pc`, saves last received/sent messages, registers post-send finalization, and updates crypto IVs after encrypted inbound messages.
- `exchange_establish_p1()` creates initiator phase-1 exchanges from configuration, generates initiator cookies, creates the initial ISAKMP SA, handles `ikecfg` finalization chaining, and starts the state machine.
- `exchange_establish_p2()` creates phase-2 exchanges under an existing ISAKMP SA, copies cookies, creates a random message ID, enables encryption/NAT-T flags, optionally creates child SAs, and starts the state machine.
- `exchange_setup_p1()` and `exchange_setup_p2()` create responder-side exchanges from inbound messages after checking policy, DOI, exchange type, duplicate active exchange state, and cookies.
- `exchange_finalize()` transfers negotiated state into SAs, marks SAs ready, copies IDs and phase-1 keystate/authentication material, handles replaced SAs, runs DOI and caller finalizers, detaches SAs from the exchange, and starts DPD after phase 1 if the peer advertised support.
- `exchange_free()`/`exchange_free_aux()` release messages, nonce/ID buffers, DOI data, keys, certs, KeyNote sessions, cert request lists, hash links, finalizers, and unfinalized SAs.
- Nonce helpers generate and save 8..256 byte nonces.
- Certificate request helpers save inbound CERTREQs, reflect acceptable CERTREQs, obtain certs, add CERT/CERTREQ payloads, and free ACA lists.
- `exchange_establish()` is the top-level config-driven entry point for phase 1 or phase 2, including recursive phase-1 establishment when a phase-2 request lacks an ISAKMP SA.

Important data flow:
- `exchange->data` is DOI-specific storage allocated from `doi->exchange_size`.
- `exchange->sa_list` temporarily owns negotiated SAs until finalization detaches them.
- `exchange->keystate` moves into `msg->isakmp_sa->keystate` during phase-1 finalization.
- Phase-1 IDs are copied between exchange and ISAKMP SA depending on which side already has them.
- `exchange->finalize` may be a composed chain built by `exchange_add_finalization()`.

Important dependencies:
- `doi_lookup()` and DOI handler callbacks: initiator/responder, scripts, finalization, free hooks.
- Message layer: allocation, replies, payload scanning, send, drop, post-send callbacks.
- SA layer: create, release/free, lookup, replacement marking.
- Config, transport, timers, KeyNote, cert/key handlers, NAT-T/DPD integrations.

Notable details:
- Exchange expiration is controlled by `General/Exchange-max-time`, defaulting to 120 seconds.
- Last messages are retained for duplicate/retransmit handling. Completed exchanges with no `last_sent` can be freed immediately.
- The finalization path starts DPD only after SAs are detached, avoiding a race with exchange cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/exchange.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/exchange.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/exchange.h

Defines `struct exchange`, exchange flags, timeout constant, and the public exchange API.

Core fields:
- Hash/list ownership: `link`, `linked`.
- Naming/policy: `name`, `policy`, `policy_id`.
- Finalization hook and argument.
- Temporary negotiated SAs in `sa_list`.
- Lifetime timer `death`.
- ISAKMP cookies, phase-2 `message_id`, exchange `type`, `phase`, `step`, `initiator`.
- Flags for commit, encryption, NAT-T, DPD, peer type.
- DOI pointer and DOI-specific `data`.
- Script program counter `exch_pc`.
- Retransmit/duplicate state: `last_received`, `last_sent`, `in_transit`.
- Nonces and IDs for initiator/responder.
- Crypto state: transform, key length, keystate.
- Authentication/cert/key material used by policy and kernel export.
- CERTREQ acceptable CA list.

Exports lifecycle, lookup, establishment, nonce/cert helpers, script lookup, setup, run, finalize, and phase-1 cookie upgrade functions.

Notable flags:
- `EXCHANGE_FLAG_ENCRYPT` gates encrypted exchange handling.
- `EXCHANGE_FLAG_NAT_T_*` records NAT traversal negotiation details.
- `EXCHANGE_FLAG_DPD_CAP_PEER` records DPD peer capability.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/exchange.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/field.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/field.c

Runtime helper for generated packet field descriptors. It decodes, logs, reads, and writes fixed-size protocol fields described by `struct field`.

Key functions:
- `field_dump_field()` and `field_dump_payload()` pretty-print decoded fields for debug logs.
- `field_get_num()` reads 1, 2, or 4 byte network-order numeric fields.
- `field_set_num()` writes 1, 2, or 4 byte numeric fields using protocol endian helpers.
- `field_get_raw()` and `field_set_raw()` copy raw fixed-length fields.
- Static debug decoders support raw hex, decimal number, bitmask names, ignored fields, and constants.

Implementation details:
- `decode_field[]` must match the enum order in `struct field`.
- Constant and mask decoding use `struct constant_map` lookup helpers.
- Unsupported numeric lengths return failure or zero.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/field.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/field.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/field.h

Declares the generated-field descriptor type and accessor API.

`struct field` contains:
- Field name.
- Byte offset.
- Length.
- Type enum: `raw`, `num`, `mask`, `ign`, `cst`.
- Optional constant maps.

This header is used by generated protocol field headers and by code that uses `GET_*`/`SET_*` macros produced by `genfields.sh`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/field.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/genconstants.sh -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/genconstants.sh

Shell/awk generator that converts a `.cst` constants specification into a generated header and C file.

Generated header:
- Include guard based on the basename.
- Includes `constants.h`.
- Emits `extern struct constant_map <prefix>_cst[];`.
- Emits `#define PREFIX_NAME value` for indented constant rows.

Generated C:
- Includes `constants.h` and the generated header.
- Emits `struct constant_map <prefix>_cst[] = { ... }`.
- Adds a `{ 0, 0 }` terminator at `.` section boundaries.
- Stores optional linked-map values from a third field.

It uses `${AWK:-awk}` and an awk `locase()` helper implemented by shelling out to `tr`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/genconstants.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/genfields.sh -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/genfields.sh

Shell/awk generator that converts a `.fld` packet-field specification into generated field headers and C descriptors.

Generated header:
- Include guard and `field.h`.
- Emits `extern struct field <prefix>_fld[]`.
- Emits structure size macros `<PREFIX>_SZ`.
- Emits offset/length macros.
- Emits typed `GET_*` and `SET_*` macros backed by `field_get_num`, `field_set_num`, `field_get_raw`, and `field_set_raw`.
- Emits extern map arrays for fields with constant maps.

Generated C:
- Includes `constants.h`, `field.h`, generated header, `isakmp_num.h`, and `ipsec_num.h`.
- Emits `struct field` arrays with offset, length, field type, and maps.
- Emits constant-map pointer arrays and field-array terminators.

Important detail:
- The generator supports structure inheritance/continuation by initializing a new section’s offset from the size of a previous prefix when a third token is provided.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/genfields.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/hash.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/hash.c

Hash and HMAC abstraction over MD5, SHA1, SHA256, SHA384, and SHA512.

Key pieces:
- Static wrappers adapt OpenBSD hash APIs to common `Init`, `Update`, `Final` signatures using `union ANY_CTX`.
- Static `hashes[]` maps internal enum values to ISAKMP/Oakley IDs, digest sizes, block sizes, shared temporary contexts, and HMAC hooks.
- `hash_get()` returns a pointer to the matching static hash descriptor.
- `hmac_init()` implements RFC-style HMAC key normalization, ipad/opad setup, and initializes inner/outer contexts.
- `hmac_final()` completes inner digest, feeds it into the outer context, and emits the final HMAC.

Notable details:
- Uses static temporary contexts and digest buffer; callers must not assume independent concurrent `struct hash` instances from `hash_get()`.
- HMAC key material is scrubbed with `explicit_bzero()`.
- Long HMAC keys are first hashed into the local key buffer.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/hash.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/hash.h

Declares hash algorithm constants, enum IDs, `struct hash`, HMAC pad constants, and hash lookup/init prototypes.

`struct hash` contains:
- Internal enum and ISAKMP/Oakley ID.
- Digest size and block length.
- Pointers to primary and secondary contexts.
- Shared digest pointer.
- Context size.
- Function pointers for normal hash and HMAC operations.

Supported algorithms:
- MD5, SHA1, SHA2-256, SHA2-384, SHA2-512.

Public API:
- `hash_get(enum hashes)`
- `hmac_init(struct hash *, unsigned char *, unsigned int)`
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/hash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/if.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/if.c

Small network-interface iterator.

`if_map()`:
- Calls `getifaddrs()`.
- Iterates every `struct ifaddrs`.
- Invokes a caller callback with interface name, address pointer, and caller argument.
- Returns `-1` if `getifaddrs()` fails or if any callback returns `-1`; otherwise returns `0`.
- Frees the address list with `freeifaddrs()`.

No filtering is performed, so callbacks must handle null addresses and unsupported families.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/if.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/if.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/if.h

Declares `if_map(int (*)(char *, struct sockaddr *, void *), void *)`.

The header includes `sys/types.h`, forward-declares `struct ifreq`, and leaves address-family-specific handling to callback users.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/if.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_aggressive.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_aggressive.c

Aggressive Mode phase-1 dispatch tables and step wrappers. It composes shared `ike_phase_1_*` helpers into the three-message aggressive exchange.

Initiator steps:
- Send SA, KE, NONCE, ID.
- Receive selected SA, KE, NONCE, ID, AUTH.
- Enable encryption and send AUTH.

Responder steps:
- Receive SA, ID, KE, NONCE.
- Send selected SA, KE, NONCE, ID, AUTH.
- Receive AUTH and, if peer is NAT-T capable, check NAT-D payloads.

Notable behavior:
- The initiator does not send INITIAL-CONTACT in Aggressive Mode, with comments explaining RFC conflict/interop concerns.
- `responder_send_SA_KE_NONCE_ID_AUTH()` performs post-DH/key-material computation before sending responder ID/AUTH.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_aggressive.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_aggressive.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_aggressive.h

Declares Aggressive Mode initiator and responder function-pointer arrays:
- `ike_aggressive_initiator[]`
- `ike_aggressive_responder[]`

These arrays are consumed through DOI exchange dispatch to run the correct step handler for each exchange step.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_aggressive.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_auth.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_auth.c

IKE phase-1 authentication method implementation for pre-shared keys and RSA signatures.

Main components:
- Static `ike_auth[]` table maps authentication method IDs to SKEYID generation, hash decode, and hash encode functions.
- `ike_auth_get()` returns the method descriptor.
- `ike_auth_get_key()` retrieves PSKs, KeyNote RSA keys, X.509 private keys, dynamic credential keys, or default private keys depending on authentication type and ID.
- `pre_shared_gen_skeyid()` finds the PSK, stores it for policy, and computes SKEYID as PRF(PSK, Ni | Nr).
- `sig_gen_skeyid()` computes signature-mode SKEYID as PRF(Ni | Nr, g^xy).
- `pre_shared_decode_hash()` and `pre_shared_encode_hash()` receive/send HASH payloads.
- `rsa_sig_decode_hash()` locates or validates peer public keys from local cert storage, inbound CERT payloads, optional DNSSEC, or public-key files; decrypts the SIG payload to recover the peer HASH; and stores auth material for policy.
- `rsa_sig_encode_hash()` sends a CERT payload when available, obtains the local private key, computes the IKE auth hash, RSA-private-encrypts it, and adds a SIG payload.
- `ike_auth_hash()` computes HASH_I/HASH_R over DH public values, cookies, SA body, and ID.
- `get_raw_key_from_file()` loads peer RSA public keys from the configured pubkey directory.

Important dependencies:
- PRF/hash layer, exchange nonces/IDs, `ipsec_exch` DH material, cert handlers, KeyNote, X.509, monitor file access, config, and key helpers.

Security-relevant notes:
- Private key file loading checks secrecy for X.509 private keys via `check_file_secrecy_fd()`.
- RSA signing enables blinding before private-key operation.
- For PSK auth, the secret is stored in `exchange->recv_key` for later policy processing.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_auth.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_auth.h

Declares the authentication-method vtable used by phase-1 code.

`struct ike_auth` fields:
- Authentication method ID.
- `gen_skeyid(struct exchange *, size_t *)`.
- `decode_hash(struct message *)`.
- `encode_hash(struct message *)`.

Exports:
- `ike_auth_get(u_int16_t)`

The header forward-declares `struct exchange`; `struct message` is referenced in function pointers and supplied elsewhere by including users.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_auth.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_main_mode.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_main_mode.c

Main Mode phase-1 dispatch tables and small step wrappers. It maps the six-message Identity Protection exchange onto shared phase-1 helpers.

Initiator sequence:
- Send SA.
- Receive SA.
- Send KE/NONCE.
- Receive KE/NONCE.
- Enable encryption, send ID/AUTH, then send INITIAL-CONTACT.
- Receive ID/AUTH.

Responder sequence:
- Receive SA.
- Send SA.
- Receive KE/NONCE.
- Send KE/NONCE and register post-send DH/key-material computation.
- Receive ID/AUTH.
- Enable encryption, send ID/AUTH, then send INITIAL-CONTACT.

Notable detail:
- `responder_send_KE_NONCE()` uses the initiator nonce length for responder nonce size and computes DH/key material in a post-send callback to overlap computation with network round trip.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_main_mode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_main_mode.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_main_mode.h

Declares Main Mode initiator and responder function-pointer arrays:
- `ike_main_mode_initiator[]`
- `ike_main_mode_responder[]`

These are the per-step handlers used by DOI exchange dispatch for Identity Protection/Main Mode phase 1.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_main_mode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_phase_1.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_phase_1.c

Shared phase-1 IKE helper implementation used by Main Mode and Aggressive Mode.

Major functions:
- `ike_phase_1_initiator_send_SA()` builds the initiator SA payload from configured transforms, stores transform offers on the exchange SA, saves the SA body for HASH computation, and advertises OpenBSD, NAT-T, and DPD vendor IDs.
- `ike_phase_1_initiator_recv_SA()` validates that the responder selected exactly one SA/proposal/transform, negotiates it against offers, decodes the transform, and selects the DH group.
- `ike_phase_1_responder_recv_SA()` validates initiator proposals, negotiates an acceptable transform, decodes attributes, checks mandatory crypto/hash/auth/group state, and stores the initiator SA body.
- `ike_phase_1_responder_send_SA()` emits the selected SA and vendor payloads.
- `ike_phase_1_send_KE_NONCE()` emits DH public value, nonce, pending CERTREQ/CERT payloads, and NAT-D payloads when needed.
- `ike_phase_1_recv_KE_NONCE()` saves peer DH public value, nonce, CERTREQs, and Main Mode NAT-D checks.
- `ike_phase_1_post_exchange_KE_NONCE()` computes DH shared secret, SKEYID, SKEYID_d/a/e, derives/extends encryption key material, initializes crypto state, handles weak DES key retry, and initializes IV from hash(g_xi | g_xr).
- `ike_phase_1_send_ID()` builds the local phase-1 ID from configured ID sections or transport source address.
- `ike_phase_1_recv_ID()` validates optional configured `Remote-ID`, stores peer ID, and marks the payload.
- `ike_phase_1_send_AUTH()` delegates HASH/SIG creation to the selected auth method.
- `ike_phase_1_recv_AUTH()` delegates HASH/SIG decoding, recomputes expected HASH_I/HASH_R, compares it, and marks the message authenticated.
- `ike_phase_1_validate_prop()` and `attribute_unacceptable()` validate peer transform attributes against configured policy, including lifetimes, algorithms, group, PRF, key length, field size, and group order.

Important dependencies:
- Attribute encoding/decoding, config lists, DH groups, crypto transforms, PRF/hash/auth modules, `ipsec_exch` DOI data, NAT-T, DPD, vendor payloads, message and SA layers.

Notable behavior:
- Aggressive Mode requires consistent group descriptions across all offered transforms.
- Nonce size defaults to 16 for initiator send, while responders mirror the initiator nonce length.
- Mandatory phase-1 attributes are enforced on responder receive: crypto transform, hash, auth method, and DH group.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_phase_1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_phase_1.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_phase_1.h

Declares shared phase-1 helper functions for SA negotiation, KE/NONCE exchange, post-DH key derivation, ID handling, and authentication.

The header is consumed by Main Mode and Aggressive Mode implementations to compose their mode-specific step arrays.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_phase_1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_quick_mode.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_quick_mode.c

Implements IKE Quick Mode phase-2 negotiation for IPsec SAs.

Dispatch:
- Initiator steps: send HASH/SA/NONCE, receive HASH/SA/NONCE, send final HASH.
- Responder steps: receive HASH/SA/NONCE, send HASH/SA/NONCE, receive final HASH.

Major behavior:
- `check_policy()` integrates KeyNote policy checks for negotiated phase-2 SAs and IDs. It builds principals from PSKs, KeyNote certs, or X.509/RSA certs and queries policy with true/false return values. If policy is disabled or ignored, it allows the negotiation.
- `initiator_send_HASH_SA_NONCE()` builds SA proposals from configured suites/protocols/transforms, allocates incoming SPIs through the DOI, stores local offer state in `proto`/`proto_attr`, handles NAT-T encapsulation mapping for ESP, sends nonce, optional PFS KE, optional client IDs, and fills HASH(1).
- `initiator_recv_HASH_SA_NONCE()` verifies HASH(2), authenticates the message, parses/synthesizes client IDs, records chosen transforms, prunes unchosen offers, enforces policy, saves responder nonce, and handles optional PFS KE.
- `initiator_send_HASH()` emits HASH(3), registers optional PFS shared-secret generation and Quick Mode post-processing.
- `responder_recv_HASH_SA_NONCE()` verifies HASH(1), authenticates the message, parses/synthesizes IDs, negotiates an acceptable SA under policy, validates AH/auth and PFS group consistency, saves nonce/KE, and assigns a passive connection name by IDs.
- `responder_send_HASH_SA_NONCE()` emits HASH(2), selected SA payloads, nonce, optional PFS KE, mirrored client IDs, and registers optional PFS shared-secret generation.
- `responder_recv_HASH()` verifies HASH(3), authenticates the message, and runs `post_quick_mode()`.
- `post_quick_mode()` derives inbound and outbound KEYMAT for each non-IPComp negotiated protocol using SKEYID_d, optional PFS g^xy, protocol ID, SPI, and both nonces; then logs Quick Mode completion.
- `gen_g_xy()` computes optional PFS DH shared secret after KE exchange.

Important dependencies:
- ISAKMP SA phase-1 key material from `msg->isakmp_sa->data`.
- PRF/hash layer, DOI SPI/proto hooks, message SA negotiation, IPsec transform decoding, connection lookup, policy/KeyNote, cert/key helpers.
- Transport endpoints for implicit Quick Mode IDs when IDci/IDcr are omitted.

Notable constraints:
- Current initiator receive path says multiple SA payloads in Quick Mode are unsupported.
- Client ID support is limited to IPv4/IPv6 address/subnet and FQDN in NAT-T transport-mode cases.
- PFS group descriptions must be consistent across accepted SAs.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_quick_mode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_quick_mode.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_quick_mode.h

Declares Quick Mode initiator and responder function-pointer arrays:
- `ike_quick_mode_initiator[]`
- `ike_quick_mode_responder[]`

These arrays provide the three-step phase-2 handler sequence used by the DOI dispatch layer.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ike_quick_mode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/init.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/init.c

Static initialization and reinitialization ordering for isakmpd subsystems.

`init()` order:
- Application, DOI, exchange, DH group, IPsec, ISAKMP DOI.
- Timer.
- Config and connection, which depend on timer.
- Logging reinit after config.
- Policy after config.
- Cert/CRL after config and policy.
- SA, transport, virtual, UDP, NAT-T, UDP encapsulation, vendor registry.

`reinit()`:
- Logs daemon reinitialization.
- Reloads config, logging, policy, certs, CRLs, connections.
- Reinitializes transports to rescan interfaces.
- Reinitializes SAs.
- Comments note unresolved questions about pending exchange timers and stale last messages after SIGHUP/UI reinit.

This file is the dependency-order anchor for daemon startup rather than a generic module registry.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/init.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/init.h

Declares daemon lifecycle entry points:
- `init(void)`
- `reinit(void)`

Used by the main daemon/control path to perform initial subsystem setup and config-driven reinitialization.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/init.h -->