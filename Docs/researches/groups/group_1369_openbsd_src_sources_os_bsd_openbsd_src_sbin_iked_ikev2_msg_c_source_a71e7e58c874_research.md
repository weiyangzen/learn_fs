# Group Research: group_1369_openbsd_src_sources_os_bsd_openbsd_src_sbin_iked_ikev2_msg_c_source_a71e7e58c874

Scope checked against `Docs/research_subset_a.md`: all requested files are under `sources/os/bsd/openbsd-src`, which is included in subset A. All seven listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/ikev2_msg.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/ikev2_msg.c

Read completely: 1370 lines.

Implements iked's IKE datagram message lifecycle: UDP/NAT-T receive, IKEv1 rejection logging, outbound message construction and send, encrypted payload encryption/decryption, integrity tags, IKE_AUTH signed/MACed data generation, authentication verification/signing, encrypted fragmentation, response/request retransmit queues, and timers.

Core receive/send flow:
- `ikev2_msg_cb()` receives from a bound iked socket with `recvfromto()`, preserves local/peer addresses, strips the 4-byte NAT-T non-ESP marker when receiving on the NAT-T port, copies the datagram into an `ibuf`, initializes proposal/certreq queues, dispatches IKEv1 to `ikev1_recv()` and IKEv2 to `ikev2_recv()`, then cleans the message.
- `ikev2_msg_init()` prepares an `iked_message` with peer/local addresses, response flag, static max-size `ibuf`, `msg_parent` set to itself, and proposal queue initialization.
- `ikev2_msg_send()` logs the exchange, optionally prepends the NAT-T marker, sends with `sendtofrom()`, updates send statistics, handles `EADDRNOTAVAIL` by moving the SA toward closing, and stores a retransmittable copy in either `sa_responses` or `sa_requests`.

Encryption, integrity, and fragmentation:
- `ikev2_msg_encrypt_prepare()` computes final IKE/SK/SKF payload lengths before encryption so headers included in authentication are correct.
- `ikev2_msg_encrypt()` pads plaintext, selects initiator/responder encryption key, initializes the cipher, prepends IV, supplies AAD for AEAD ciphers, appends ciphertext, and reserves tag space.
- `ikev2_msg_integr()` fills the HMAC/tag field; non-AEAD hashes the message excluding the tag, while AEAD obtains the tag from the cipher.
- `ikev2_msg_decrypt()` verifies HMAC for non-AEAD, configures AEAD tag/AAD when needed, decrypts, validates block alignment, and strips padding.
- `ikev2_msg_send_encrypt()` builds a normal SK message; `ikev2_send_encrypted_fragments()` splits plaintext into independently encrypted/authenticated SKF fragments under IPv4/IPv6 size limits.

Authentication and retransmit:
- `ikev2_msg_auth()` constructs AUTH input from the initial exchange message, opposite nonce, and PRF over the local ID buffer.
- `ikev2_msg_authverify()` verifies peer AUTH with PSK-derived material or certificate key material and updates SA auth state.
- `ikev2_msg_authsign()` signs/MACs local AUTH data and stores it in `sa_localauth`.
- Retransmit helpers group messages by msgid/exchange, cache request/response fragments, resend responses on duplicate requests, and retry requests with exponential backoff until the SA is freed.

Risks and notes:
- Cleanup ownership depends on `msg_parent`; top-level and decrypted child messages free different fields.
- Fragment retransmission only responds to peer retransmission of fragment number one.
- A retransmit send failure sets an SA reason and frees the SA.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/ikev2_msg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/ikev2_pld.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/ikev2_pld.c

Read completely: 2213 lines.

Implements IKEv2 payload parsing and validation for iked. It walks payload chains, bounds-checks every generic/substructure header before copying, recursively parses encrypted SK/SKF payloads, reassembles encrypted fragments, and records peer-provided state into the parent `iked_message`.

Top-level parser:
- `ikev2_pld_parse()` logs the IKE header, verifies `ike_length`, advances past the header, and calls `ikev2_pld_payloads()`.
- `ikev2_validate_pld()` checks generic payload header size and declared payload length.
- `ikev2_pld_payloads()` dispatches SA, KE, ID, CERT, CERTREQ, AUTH, NONCE, NOTIFY, DELETE, TS, SK, SKF, CP, and EAP payloads, sends informational errors for bad peer messages, and enforces encrypted payloads as terminal.

Major payload handling:
- SA/proposal parsing validates proposal lengths, optional SPI sizes, creates peer proposals, parses transforms/attributes, and drops invalid peer proposals when transform selection is unsupported.
- KE, ID, CERT, CERTREQ, AUTH, and NONCE handlers reject malformed/duplicate critical fields and save peer data to the parent message only when `ikev2_msg_frompeer()` is true.
- Notify handling updates NAT detection, auth failure, invalid KE, rekey, IPCOMP, MOBIKE, COOKIE/COOKIE2, fragmentation, transport mode, UPDATE_SA_ADDRESSES, and signature-hash flags, with encryption checks for sensitive notifications.
- DELETE parsing stores delete SPI metadata and validates SPI count/size.
- Traffic selector parsing validates IPv4/IPv6 address ranges and rejects trailing bytes.
- CP parsing stores one IPv4/IPv6 address or DNS value from peer configuration payloads.
- EAP parsing validates EAP length, calls `eap_parse()`, rejects duplicate EAP payloads, and stores the raw EAP message.

Encrypted payloads and fragments:
- `ikev2_pld_ef()` validates SKF fragment counters, caps total fragments, decrypts each fragment, rejects duplicate or inconsistent fragment sets, and triggers reassembly when complete.
- `ikev2_frags_reassemble()` concatenates plaintext fragments, flushes original request retransmits on response reassembly, recursively parses the reassembled plaintext, and frees fragment state.
- `ikev2_pld_e()` decrypts SK payloads and recursively parses decrypted payloads; it rejects receiving SK while SKF fragments are queued.
- `ikev2_pld_parse_quick()` is a lightweight parser used to extract SKF fragment number for retransmit response logic without requiring `msg_sa`.

Risks and notes:
- Most state mutation is guarded by `ikev2_msg_frompeer()`.
- Optional malformed notifications are often ignored, while structural payload errors fail the parse.
- Reassembly uses `fatalx()` if a supposedly complete fragment array has a missing slot.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/ikev2_pld.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/imsg_util.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/imsg_util.c

Read completely: 122 lines.

Provides small internal convenience wrappers around OpenBSD's `imsg`/`ibuf` API for iked message buffers.

Functions:
- `ibuf_new()` creates a dynamic `ibuf` capped at `IKED_MSGBUF_MAX`, optionally zero-filling or copying caller data.
- `ibuf_static()` opens a fixed-size `IKED_MSGBUF_MAX` buffer.
- `ibuf_length()` safely returns `0` for `NULL` or `ibuf_size()` otherwise.
- `ibuf_getdata()` extracts a requested-length sub-buffer and returns an owned copy.
- `ibuf_dup()` duplicates an existing buffer.
- `ibuf_random()` reserves and fills a buffer with `arc4random_buf()`.
- `ibuf_setsize()` truncates/sets `wpos` if the requested length is within allocation.

Risks and notes:
- `ibuf_setsize()` directly updates `buf->wpos`, so callers must pass a valid mutable `ibuf`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/imsg_util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/log.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/log.c

Read completely: 218 lines.

Implements iked's small logging facade over stderr/syslog, with debug/verbose controls and fatal helpers.

Core behavior:
- `log_init()` sets debug/verbose mode, initializes the process name, opens syslog when not debugging, and calls `tzset()`.
- `vlog()` preserves `errno`, writes newline-terminated messages to stderr in debug mode, or sends them to syslog otherwise.
- `log_warn()` appends saved `errno` text to messages and has fallback behavior if formatting allocation fails.
- `log_warnx()`, `log_info()`, and `log_debug()` emit fixed-priority messages; debug logs require `verbose > 1`.
- `fatal()` and `fatalx()` log critical messages through `vfatalc()` and exit.

Risks and notes:
- Logging paths intentionally restore `errno`.
- `log_procname` is global and expected to be initialized before fatal messages.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/ocsp.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/ocsp.c

Read completely: 621 lines.

Implements asynchronous OCSP certificate validation across iked's privilege-separated processes. The parent resolves/connects to the OCSP responder and passes a socket fd to the cert process; the cert side builds and sends OCSP requests with OpenSSL, verifies responses, and reports valid/invalid results to IKEv2.

Key flow:
- `ocsp_connect()` receives SA header and optional URL, falls back to `env->sc_ocsp_url`, parses the URL, rejects OCSP over SSL, opens a nonblocking IPv4 TCP socket, resolves the host, and starts or completes connect.
- `ocsp_connect_cb()` handles connect timeout/completion via `SO_ERROR`.
- `ocsp_connect_finish()` sends `IMSG_OCSP_FD` to `PROC_CERT`, including the path and fd on success.
- `ocsp_validate_cert()` decodes the DER certificate, builds `OCSP_REQUEST` and cert ID state, queues the request, includes optional AIA OCSP URL, and asks the parent for a connected fd.
- `ocsp_receive_fd()` matches the returned SA header to a pending request, binds the fd to an OpenSSL BIO, creates an `OCSP_REQ_CTX`, and registers nonblocking send/read callbacks.
- `ocsp_callback()` drives `OCSP_sendreq_nbio()` and rearms read/write events as OpenSSL requires.
- `ocsp_parse_response()` checks response status, loads responder certs, verifies nonce when present, verifies the basic response, checks certificate status and optional validity windows, and treats only GOOD status as valid.
- `ocsp_validate_finish()` sends `IMSG_CERTVALID` or `IMSG_CERTINVALID` to `PROC_IKEV2` and frees state.

Risks and notes:
- Parent-side connection selects only IPv4 results.
- OCSP over SSL is explicitly unsupported.
- Missing nonce is logged but not fatal; nonce verification errors are fatal.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/ocsp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/parse.y -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/parse.y

Read completely: 3391 lines.

Defines the yacc grammar, lexer, macro/include handling, address/transform parsing, policy/user/RADIUS construction, and helper routines for iked configuration files. It parses `ikev2` rules and selected global settings while skipping IKEv1/manual-keying/ipsec.conf legacy rules.

Major areas:
- Static defaults define IKE/ESP transform sets, transform name maps, auth methods, SA protocols, configuration payload names, parser globals, and parser-local address/filter/mode structures.
- Grammar accepts includes, `set` statements, local `user` entries, `ikev2` policies, RADIUS settings, macro assignments, and ignored legacy rules.
- `ikev2rule` gathers name, flags, SA protocol, AF, IP protocols, rdomain, flow hosts, peers, IKE/child transforms, IDs, lifetimes, auth, CP options, interface, and filters, then calls `create_ike()`.
- Transform grammar supports auth/encryption/PRF/group/ESN lists, separating IKE and child SA encryption maps.
- Auth grammar supports default signature-any, inline/file PSK, EAP RADIUS/MSCHAPv2, and explicit RSA/ECDSA/RFC7427/signature methods.
- RADIUS grammar configures auth/accounting servers, retry/failover counts, config-attribute mapping, DAE listener, and DAE clients, zeroing secrets after use.

Lexer and file handling:
- `yylex()` skips whitespace/comments, expands `$macro` values, parses quoted strings, strict numbers, keywords, and bare strings.
- `pushfile()`/`popfile()` implement include stacks and secrecy checks.
- `check_file_secrecy()` requires safe ownership and permissions for config/secret files.
- `parse_config()` resets parser defaults, runs `yyparse()`, transfers parsed global settings into `env`, frees macros/interface cache, and returns failure on parse errors.

Helpers and policy construction:
- Address helpers parse interfaces, numeric IPs, DNS, `any`, `dynamic`, CIDR masks, interface groups, and source NAT wrappers.
- Key helpers parse PSK hex strings and key files up to `KEYSIZE_LIMIT`.
- Transform helpers expose key/nonce lengths and copy explicit or default transforms into policy proposals.
- `create_ike()` validates peers, address families, active-mode requirements, interfaces, IDs, transform combinations, IKE/child proposal construction, flow expansion, CP config copying, cert request type, and emits policy/flow config.
- `create_flow()`, `expand_flows()`, and `expand_keyword()` create concrete outbound flow records from wildcard/dynamic endpoints.
- `create_user()` validates and sends local EAP user credentials, then zeroes temporary state.
- `iaw_free()` releases address wrapper lists.

Risks and notes:
- `parse_xf()` uses prefix matching, so transform table ordering matters for ambiguous prefixes.
- DNS may expand to multiple address wrappers; IPv6 DNS plus netmask is rejected.
- Link-local IPv6 interface addresses are skipped due to missing scope support.
- Some malformed system states call `err()`/`fatalx()` rather than returning parse errors.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/parse.y -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/pfkey.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/iked/pfkey.c

Read completely: 2124 lines.

Implements iked's PF_KEY v2 integration with the OpenBSD kernel IPsec stack. It maps IKEv2 algorithms/protocols to SADB constants, installs/deletes flows and SAs, obtains SPIs, groups bundled SAs, queries last-use/stat counters, handles decoupled operation, registers for kernel acquires/expires, and processes asynchronous PF_KEY messages.

Core behavior:
- `pfkey_couple()` toggles kernel coupling for all known SAs and flows, installing on recouple and deleting on decouple.
- `pfkey_flow()` builds `SADB_X_ADDFLOW`/`SADB_X_DELFLOW` messages with flow addresses, masks, protocol, direction, optional tunnel endpoints, identities, pre-NAT handling, and rdomain extension.
- `pfkey_sa()` builds SADB ADD/UPDATE/DELETE messages with SA metadata, addresses, keys, lifetimes, UDP encapsulation, tags, tap, sec(4) interface routing, ESN/tunnel flags, identities, and rdomain data.
- `pfkey_sa_lookup()` sends `SADB_GET` and optionally extracts last-use or counter extensions.
- `pfkey_sa_getspi()` obtains a kernel SPI via `SADB_GETSPI`.
- `pfkey_sagroup()` groups bundled SAs, including IPCOMP+ESP rdomain handling.
- `pfkey_sa_add()` handles ADD/UPDATE choice, timeout recovery by existence probe, local recoupling `ESRCH` retry as ADD, optional grouping, and loaded-state updates.
- `pfkey_sa_delete()` preserves counters before deletion and accumulates them into the parent IKE SA.
- `pfkey_write()` writes one PF_KEY request, temporarily disables the persistent event, waits for a reply, and re-enables the event.
- `pfkey_reply()` polls with timeout, validates PF_KEY version, reads full messages, returns the matching pid/seq reply, postpones async kernel messages, and treats `EEXIST` as non-fatal for no-data operations.
- `pfkey_init()` opens event handling, flushes SADB state, and registers ESP/AH acquires.
- `pfkey_process()` handles `SADB_ACQUIRE` by asking the kernel for policy details and calling `ikev2_child_sa_acquire()`, and handles `SADB_EXPIRE` by rekeying on soft expiry or dropping on hard expiry.

Risks and notes:
- The code assumes one outstanding PF_KEY request via global `sadb_msg_seq`.
- PF_KEY timeout returns retry-style `-2`; SA ADD has recovery logic for replies lost after kernel success.
- `IOV_CNT` must cover every optional extension combination.
- Unsupported identities are silently omitted from PF_KEY messages.
- Acquire destination-mask parsing appears to update `flow_src` net flags while processing destination masks.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/iked/pfkey.c -->