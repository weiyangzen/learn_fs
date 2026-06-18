# Group Research: group_1367_openbsd_src_sources_os_bsd_openbsd_src_sbin_iked_ca_c_sources_os_bs_9c794a378834

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/openbsd-src` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/ca.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/ca.c

`ca.c` implements the privileged certificate-authority subprocess for `iked`. It owns local CA/certificate stores, private/public key material received from the parent, certificate request/reply handling, AUTH signing requests, raw public-key fallback, and OpenSSL-based certificate validation.

Key paths include `caproc()`/`ca_run()` process startup, `ca_reset()`/`ca_reload()` store creation and reload, `ca_getreq()` certificate selection for outbound CERT payloads, `ca_getcert()` peer CERT validation, and `ca_getauth()` signing of AUTH payloads. The CA process communicates with parent, IKEv2, and control processes through imsg dispatchers.

Certificate handling supports X.509 certificates, bundled certificates with untrusted intermediates, local supplemental certificate chains, raw RSA/ECDSA public keys, CRLs, optional partial-chain validation, and optional OCSP validation. It computes RFC7296 CERTREQ SHA-1 subject-public-key-info digests and matches identities through ASN.1 DN or subjectAltName.

Security-relevant details: private key material lives in the CA process, certificates are validated through `X509_STORE_CTX`, CRL flags are enabled only after CRLs load, raw public-key validation maps peer IDs to files under the public-key directory, and AUTH signing falls back to `IKEV2_AUTH_NONE` on signing failure. Input bundle parsing is strict on type/length boundaries.

Notable coupling: depends heavily on `iked.h`, `ikev2.h`, OpenSSL, `config_getkey()`, `ikev2_msg_authsign()`, OCSP helpers, imsg helpers, and policy/SA identity structures.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/ca.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/chap_ms.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/chap_ms.c

`chap_ms.c` implements MS-CHAP/MS-CHAPv2 and MPPE key derivation helpers used by EAP authentication. It follows RFC2433, RFC2759, and RFC3079, using OpenSSL MD4, MD5, SHA1, and DES APIs.

Core functions generate NT password hashes, challenge hashes, NT responses, authenticator responses, master keys, asymmetric send/receive start keys, 64-byte MSK material, and decrypted RADIUS MPPE keys. Internal DES helpers expand 56-bit key material to DES parity form and encrypt the challenge in three blocks.

The file is protocol glue rather than daemon orchestration. It does not allocate persistent objects, but it relies on exact fixed-size protocol buffers and legacy crypto primitives required by MS-CHAPv2 compatibility.

Security-relevant details: it implements known-weak legacy MS-CHAPv2 primitives but only as required protocol support. Callers must provide correctly sized output buffers; most functions assume fixed protocol sizes rather than doing dynamic bounds checks.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/chap_ms.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/chap_ms.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/chap_ms.h

`chap_ms.h` declares the MS-CHAP/MS-CHAPv2 helper API and protocol sizes. It defines challenge, hash, master-key, MSK key, MSK padding, total MSK, and maximum NT password sizes.

The header exports functions for NT response generation, authenticator response generation, NT password hashing, challenge hashing, asymmetric key derivation, master-key derivation, RADIUS key decoding, and MSK construction.

This file is intentionally narrow: it exposes cryptographic helper routines to EAP/RADIUS code without defining daemon state.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/chap_ms.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/config.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/config.c

`config.c` manages runtime object allocation, teardown, and configuration IPC. It creates and frees IKE SAs, policies, proposals, transforms, flows, Child SAs, users, sockets, PF_KEY state, keys, static daemon settings, OCSP settings, and RADIUS-related configuration.

SA cleanup in `config_free_sa()` is broad: timers, fragments, proposals, Child SAs, interface configuration, flows, RADIUS accounting, address pools, policy refs, retransmit queues, nonces, DH material, crypto state, AUTH/cert/EAP buffers, configuration payloads, tags, RADIUS requests, and counters. Policy cleanup handles refcounted policy removal when SAs still point at a policy.

Configuration data is serialized through imsg. Policies are sent as a policy header plus proposal/transform records; flows are sent separately. Keys are read from `IKED_PRIVKEY`, serialized through CA helper functions, and sent to the CA process as private and public key imsgs.

Reset handling supports policy, SA, user, RADIUS, CA, and all-state resets. Socket/PF_KEY helpers bind privileged resources in the parent and pass file descriptors to the IKEv2 process. RADIUS helpers configure auth/accounting servers, config maps, DAE listeners, and DAE clients.

Security-relevant details: private key imsg data is explicitly zeroed after receipt, RADIUS secrets use variable-length trailing storage, no-action mode prints/parses without installing runtime config, and reset paths carefully close sockets/events and free outstanding RADIUS requests.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/config.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/control.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/control.c

`control.c` implements the Unix-domain control socket process used by `ikectl`-style clients. It creates/listens on the control socket, accepts nonblocking connections, tracks connected clients with per-connection peer IDs, and forwards control imsgs to parent, IKEv2, or CA.

The control process supports notify subscriptions, verbosity changes, reload/reset/couple/decouple/active/passive commands, reset-by-ID, show-SA, show-stats, and show-certstore requests. Replies are routed back by peer ID so command responses reach the requesting client.

It handles file-descriptor pressure by pausing accept on `ENFILE`/`EMFILE` and resuming with a timer. Socket permissions differ for restricted vs nonrestricted sockets. Runtime pledge is limited to stdio, unix, and recvfd.

Important coupling: parent handles reload/reset/mode control, IKEv2 handles SA/stats/reset-ID views, and CA handles certificate-store display. Notify clients receive forwarded imsgs broadcast from control traffic.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/control.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/crypto.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/crypto.c

`crypto.c` wraps OpenSSL primitives behind iked’s negotiated crypto interfaces. It implements PRF/integrity hashes, encryption ciphers, AEAD handling, and AUTH signing/verification for RSA, ECDSA, RFC7427 generic signatures, and shared-key MICs.

`hash_new()` supports HMAC-MD5, HMAC-SHA1, HMAC-SHA2 PRFs, truncated HMAC integrity algorithms, and AEAD integrity marker entries for AES-GCM. `cipher_new()` supports 3DES-CBC, AES-CBC, and AES-GCM variants, including salt+IV nonce construction for AEAD.

The DSA layer handles HMAC authentication, legacy RSA SHA1 signatures, fixed ECDSA SHA2 methods, and RFC7427 signature-scheme OID prefixes. ECDSA signatures are converted between IKEv2 concat `r|s` format and OpenSSL DER `ECDSA_SIG` format.

Security-relevant details: padding is disabled for IKE encryption, GCM tags are managed explicitly, RFC7427 verification selects the digest based on the encoded OID prefix, and RSA-PSS can be forced through the global `force_rsa_pss`. HMAC verify uses direct `memcmp`, so constant-time comparison is not provided here.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/crypto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/crypto_api.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/crypto_api.h

`crypto_api.h` provides a small NaCl-compatible crypto API surface used by the DH/KEM code. It defines integer aliases, random-byte macros backed by `arc4random_buf()`/`arc4random()`, SHA512 hash size, constant-time verify declaration, and SNTRUP761 KEM sizes/functions.

The header is specifically needed for the hybrid SNTRUP761+X25519 group in `dh.c`. It declares public key, secret key, ciphertext, shared-secret sizes and KEM keypair/encapsulation/decapsulation routines.

It is not a general daemon header; it is a compatibility shim for imported/public-domain crypto routines.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/crypto_api.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/crypto_hash.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/crypto_hash.c

`crypto_hash.c` implements the NaCl-compatible `crypto_hash_sha512()` function declared in `crypto_api.h`. It delegates directly to OpenSSL `EVP_Digest()` with `EVP_sha512()`.

The function returns `0` on digest success and `-1` on OpenSSL failure. It is a small compatibility wrapper, not a higher-level iked crypto abstraction.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/crypto_hash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/dh.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/dh.c

`dh.c` implements iked’s Diffie-Hellman/key-exchange group abstraction. It supports MODP groups, ECP groups, Curve25519, and a private-use hybrid SNTRUP761+X25519 group.

The `ike_groups[]` table defines supported IKE DH group IDs, types, bit sizes, MODP primes/generators, ECP OpenSSL NIDs, Curve25519, and SNTRUP761X25519 group 1035. `group_get()` selects function pointers for group-specific init, exchange, and shared-secret creation.

MODP uses OpenSSL DH with fixed RFC prime/generator values. ECP generates an EC key, encodes public exchange as raw `x|y`, validates peer public keys through `EC_KEY_check_key()`, and derives the x-coordinate shared secret per RFC5903. Curve25519 uses `crypto_scalarmult_curve25519()`.

The hybrid KEM path delays setup until exchange creation. Initiators send SNTRUP761 public key plus X25519 public key; responders encapsulate to the KEM public key and send ciphertext plus X25519 public key. Shared output is SHA512 over KEM key material and X25519 shared secret.

Security-relevant details: group teardown zeroes Curve25519 and KEM private storage, EC temporary BIGNUMs and points are cleared, exchange sizes are strictly checked, and MODP/ECP outputs are zero-padded to fixed protocol lengths.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/dh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/dh.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/dh.h

`dh.h` declares the key-exchange abstraction used by iked. It defines group types for MODP, ECP, Curve25519, and SNTRUP761X25519, plus `group_id` metadata and `dh_group` runtime state.

`dh_group` carries backend-specific state pointers and function pointers for init, exchange length, optional secret length, fixed-buffer exchange/shared operations, and ibuf-based exchange/shared operations for variable hybrid KEM exchanges.

The public API includes group initialization/freeing, group lookup by IKE group ID, and creation of exchange/shared-secret buffers. `DH_MAXSZ` documents the 8192-bit maximum classic DH size.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/dh.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/eap.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/eap.c

`eap.c` implements IKEv2 EAP message construction and parsing, with direct support for EAP Identity and EAP-MSCHAPv2 plus pass-through behavior for RADIUS-backed EAP.

Responder-side flows include sending IDr/CERT/AUTH/EAP identity requests, generating MSCHAPv2 challenges, sending success/failure-style EAP messages, and parsing MSCHAPv2 responses into `msg_parent->msg_eap` for parent/RADIUS/user verification.

`eap_parse()` validates EAP header lengths, handles request/response/success/failure codes, extracts identities, logs/parses MSCHAPv2 challenge/response/success/failure payloads, and dispatches to `eap_mschap()` when local MSCHAPv2 handling is needed. Unsupported EAP types are accepted only when policy auth is `EAP_TYPE_RADIUS`.

Security-relevant details: variable strings are parsed through `get_string()`, short protocol messages are rejected, responder-only MSCHAPv2 is enforced, duplicate identity handling avoids replacing an existing SA identity, and challenge values are randomly generated and stored in SA EAP state.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/eap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/eap.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/eap.h

`eap.h` defines EAP protocol structures, EAP code/type constants, MSCHAPv2 constants, packed MSCHAPv2 payload layouts, error codes, and external constmap declarations.

The structures cover generic EAP headers/messages, MSCHAP challenge, peer response, success, and failure payloads. Constants include IANA EAP method values and iked’s internal `EAP_TYPE_RADIUS`.

This header is consumed by `eap.c` and other IKEv2 code that needs to parse or construct EAP payloads inside IKE_AUTH.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/eap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/genmap.sh -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/genmap.sh

`genmap.sh` is a build helper that generates `struct iked_constmap` arrays from header definitions. It takes an input header and token name, derives map names from existing `struct iked_constmap` declarations, then emits C source with license/header includes and generated map entries.

The script uppercases/lowercases the token, scans `#define` lines with comments, and turns constants of the form `${TOKEN}_${MAP}_... /* description */` into `{ value, "name", "description" }` entries.

It is simple shell/sed/grep generation logic and assumes comments/defines follow the expected formatting. It does not participate at runtime.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/genmap.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/iked.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/iked.c

`iked.c` is the daemon entry point and parent-process coordinator. It parses command-line options, initializes global daemon state, starts privsep children, configures logging/signals, loads configuration, passes privileged resources to children, and handles reload/shutdown.

The privsep layout contains CA, control, and IKEv2 children. Startup parses config, opens PF_KEY and UDP sockets, reads/sends key material to CA, resets CA state, compiles policies in IKEv2, configures static daemon settings, coupling, OCSP, RADIUS, and finally active/passive mode.

The parent process handles SIGHUP reloads, SIGTERM/SIGINT shutdown, child death, and control-plane messages. Reload either resets/reloads policies/RADIUS/CA and reparses config, or forwards targeted reset modes to IKEv2 and CA. Parent dispatch also handles OCSP socket connection and virtual route/address/DNS requests from IKEv2.

Security-relevant details: root is required unless no-action mode is selected, pledge is applied after privileged setup, process titles/instances are controlled through privsep options, and shutdown kills children before cleaning virtual routes and freeing parent state.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/iked.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/iked.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/iked.h

`iked.h` is the central shared header for daemon structures, constants, macros, and cross-module prototypes. It defines common IKE headers, imsg/event wrappers, control socket state, runtime SA/policy/flow/Child SA/user/RADIUS structures, crypto wrapper state, EAP state, message parse state, privsep process state, daemon global state, and function declarations for most iked modules.

Core runtime models are defined here: `iked_policy` for configured connection policy, `iked_sa` for live IKE SA state, `iked_childsa` for kernel IPsec SA state, `iked_flow` for traffic selectors/flows, `iked_message` for parsed inbound/outbound message state, and `iked` for daemon-global process state.

The header also defines request/state flag bits, timer constants, retransmit limits, fragmentation limits, MOBIKE flags, NAT-T mode, static daemon configuration, stats counters, and RB/TAILQ/SIMPLEQ container types. Many modules depend on these shared layouts, making this a high-coupling ABI within the daemon.

Security-relevant surfaces exposed here include certificate/auth buffers, derived key buffers, EAP/MSCHAP state, RADIUS secrets/requests, PF_KEY and socket descriptors, privsep process IDs, imsg size-check macros, and global mutable daemon settings.

Because this header declares most module interfaces, changes here have broad blast radius across CA, config, control, crypto, DH, EAP, IKEv2, PF_KEY, policy, RADIUS, timer, proc, util, OCSP, parser, and print code.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/iked.h -->