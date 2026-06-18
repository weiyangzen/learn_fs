# Group Research: group_1373_openbsd_src_sources_os_bsd_openbsd_src_sbin_isakmpd_ipsec_c_sources_b41e56ede9ea

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ipsec.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ipsec.c

IPsec DOI implementation for `isakmpd`.

It registers the IPsec DOI dispatch table, defines Quick Mode and New Group Mode payload scripts, validates DOI-specific exchanges/protocols/transforms/attributes, decodes negotiated IKE/IPsec attributes, and routes phase-1/phase-2 exchanges to main mode, aggressive mode, transaction mode, informational mode, and quick mode handlers.

The phase-1 finalizer transfers negotiated hash/PRF/SKEYID material into the ISAKMP SA, installs lifetime timers, and starts NAT-T keepalives. The phase-2 finalizer builds traffic selectors from ID payloads, applies optional config-driven PF tags and interface bindings, installs inbound/outbound SPIs through PF_KEY, groups bundled protocol SPIs, enables flows unless acquire-only/interface/on-demand policy says not to, and marks older ready SAs with the same flow as replaced.

It also owns IPsec selector/ID helpers: parsing configured address/subnet IDs, building ISAKMP ID payloads, cloning and rendering IDs, applying configured `NAT-ID`, deriving transport-mode NAT-T flows from the ISAKMP SA addresses, and computing ESP/AH key material lengths. Informational handling processes DELETE payloads, authenticated INITIAL-CONTACT notifications, HASH payload insertion/finalization, and protected informational pre/post hooks.

Notable constraints: only identity-only situations are accepted; many legacy/optional ID and attribute forms are explicitly unsupported; phase-1 default lifetime is 8 hours; INITIAL-CONTACT is rejected in aggressive mode or when unauthenticated/unprotected; DELETE payloads enforce protocol-specific SPI sizes and payload-length bounds before deletion.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ipsec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ipsec.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ipsec.h

Public IPsec DOI header.

It defines `struct ipsec_exch`, the DOI-specific exchange state containing negotiated hash/auth/group/PRF state, DH values, SKEYID material, phase-2 IDs, keymat length, and ISAKMP configuration attributes. It also defines `struct ipsec_sa` for phase-1 key state plus phase-2 selectors and ports, and `struct ipsec_proto` for encapsulation, authentication, key length/rounds, replay window, and directional key material.

The exported API covers DOI registration, transform/attribute decoding, HASH payload handling, DH generation/saving, configured ID construction/parsing/rendering, key length calculation, initial-contact notification, ID cloning, and SA lookup by destination/SPI/protocol.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ipsec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ipsec_doi.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/ipsec_doi.h

Small IPsec DOI constants header.

It includes generated IPsec field and numeric constant headers, defines the fixed IPsec SPI size as 4 bytes, and defines `IPSEC_SPI_LOW` as the lower bound for valid SPI values.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/ipsec_doi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/isakmp.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/isakmp.h

Core ISAKMP protocol constants and utility macros.

It includes generated ISAKMP field/number definitions, defines default IKE UDP ports 500 and NAT-T 4500, the default transport name, cookie aggregate offsets/lengths, ISAKMP attribute format/type packing helpers, and version-major/minor packing helpers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/isakmp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/isakmp_cfg.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/isakmp_cfg.c

IKE configuration mode transaction implementation.

It defines the transaction exchange payload script and initiator/responder step tables for SET/ACK and REQUEST/REPLY mode. The initiator send path builds configuration attribute payloads from peer-ID-derived config sections, either sending configured address/netmask/DNS/WINS/DHCP/lifetime values or requesting attributes listed in configuration.

Receive paths verify phase-2 HASH payloads when needed, check transaction IDs and message types, decode attributes into the exchange's `ie->attrs` list, mark attribute payloads handled, and log ACK/REPLY/SET semantics. The responder send path chooses the peer identity, encodes requested attributes from local config, emits ACK or REPLY payloads, and finalizes HASH protection for phase-2 transaction exchanges.

Attribute encoding supports IPv4/IPv6 address, netmask, subnet, DHCP, DNS, NBNS, address expiry, application version, and supported-attributes shells. Unsupported/private/future attributes are ignored or rejected according to type range, and ACK responses include only attributes marked as used.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/isakmp_cfg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/isakmp_cfg.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/isakmp_cfg.h

Header for ISAKMP configuration mode support.

It defines `struct isakmp_cfg_attr`, a list node holding an attribute type, used/ignored flags, value length, and copied value. It exports the transaction-mode initiator/responder function tables and the transaction exchange validation script.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/isakmp_cfg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/isakmp_doi.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/isakmp_doi.c

Minimal ISAKMP DOI registration and handlers.

This DOI is mostly a compatibility shell around informational exchanges. It registers a DOI with no DOI-specific state sizes, no SPI allocation/deletion hooks, no exchange script, no situation bytes, and IPsec ID decoding for reporting.

Validation is intentionally narrow: DOI data in ID payloads must be zero, key information is accepted without work, situations are empty, and most attribute/protocol/transform/exchange validation paths reject if reached. Initiator support only sends informational messages; responder support handles informational NOTIFY payloads, dispatches DPD notifications, marks other notifications and DELETEs handled, and rejects SA proposals with no-proposal-chosen.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/isakmp_doi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/isakmp_doi.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/isakmp_doi.h

Single-purpose ISAKMP DOI header.

It exposes `isakmp_doi_init()` so initialization code can register the lightweight ISAKMP DOI.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/isakmp_doi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/isakmpd.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/isakmpd.c

Main `isakmpd` daemon entry point.

It parses command-line options for address families, acquire-only mode, config path, debug levels, FIFO/PID/report paths, packet capture, UDP/NAT-T ports, policy ignoring, passive shutdown mode, NAT-T disabling, and verbose logging. Startup sanitizes stdio, initializes logging, opens protocol/service databases, initializes the UI FIFO, daemonizes unless debugging, writes the PID file, starts privilege separation, initializes the unprivileged child, optionally starts IKE pcap logging, and enters the event loop.

The main loop handles SIGHUP reconfiguration, SIGUSR1 state reports, controlled shutdown, transport/UI/application readable fds, pending transport write fds, timer deadlines, message receiving/sending, UI/app handlers, and timer expirations. Shutdown queues DELETE notifications for phase-2 then phase-1 SAs unless disabled and exits only after prioritized send queues drain.

Notable behavior: `-S` disables SA deletion and makes the UI daemon passive; report generation temporarily redirects the current log channel to the report file opened through the monitor; the privileged parent never runs the normal event loop and instead enters `monitor_loop()`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/isakmpd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/key.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/key.c

Key conversion helpers for passphrase and RSA key material.

It frees internal keys by type, serializes passphrases as duplicated strings and RSA keys as DER public/private blobs, renders serialized passphrases as strings and RSA blobs as hex, internalizes serialized data back into passphrase strings or OpenSSL RSA objects, and parses printable RSA hex back into serialized bytes.

Unsupported or unknown key types are logged. DSA constants exist in the header, but this implementation only handles passphrases and RSA.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/key.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/key.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/key.h

Key API header.

It defines key type constants for none, passphrase, RSA, and DSA, public/private key direction constants, and declares helpers for freeing, serializing, printing, parsing printable form, and internalizing key material.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/key.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/libcrypto.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/libcrypto.h

Central OpenSSL include wrapper.

It includes the OpenSSL headers used by this daemon for SSL/BIO/MD5/PEM/RSA/X509/X509 verification APIs, allowing local code to include `libcrypto.h` instead of repeating OpenSSL header sets.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/libcrypto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/log.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/log.c

Logging and IKE packet capture implementation.

It supports stderr/file/syslog logging, per-class debug levels, verbose logging, debug-level reconfiguration from config, temporary debug toggling, fatal logging through `monitor_exit()`, and fixed-size log buffers suitable for out-of-memory paths. File logging includes timestamps, class names, levels, and a `[priv]` suffix when running as root, with fallback to syslog if writing fails.

The packet capture path writes loopback-style pcap files through monitor-opened files, appending to existing safe regular files or creating restricted new ones. It synthesizes IPv4/IPv6 + UDP headers around ISAKMP payloads, clears the ISAKMP encryption flag in the captured copy for analysis visibility, adds the NAT-T non-ESP marker for port 4500 traffic, computes IP/UDP checksums, and flushes each record.

Notable constraints: capture size is limited by `SNAPLEN`; capture file access goes through the privilege-separation monitor; existing capture files must be regular and not group/world accessible.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/log.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/log.h

Logging API and log-class definitions.

It defines fixed log message size, log classes, class labels, always-logged pseudo-classes, `LOG_DBG` convenience macros, the default pcap path, and declarations for debug logging, packet capture control, current log redirection, normal/error/fatal/verbose logging, initialization, and reconfiguration.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/log.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/message.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/message.c

Generic ISAKMP message engine.

It allocates, references, queues, frees, parses, validates, encrypts, decrypts, sends, receives, duplicates-checks, and indexes ISAKMP messages. Incoming messages are checked for header length/version/exchange/flags/message-ID validity, associated with existing or new exchanges/SAs, optionally decrypted with DOI-provided IV state, packet-logged, payload-sorted, generically validated, authenticated when HASH validation succeeds, and dispatched to exchange logic.

Payload parsing enforces generic header bounds, reserved fields, minimum sizes, next-payload validity, accepted payload sets, and nested SA/proposal/transform containment. Validation covers SA DOI/situation parsing, proposal/transform monotonic ordering, transform IDs and attributes, ID/key/nonce/cert/cert-req/vendor/NAT-D/NAT-OA/notify/delete/hash payloads, authenticated DELETE requirements, DOI/protocol checks, SPI size and length checks, and peer-address checks for DELETE authorization.

Outgoing support builds headers, appends payloads while maintaining next-payload links and payload indexes, constructs SA/proposal/transform payloads from selected protocols and DOI SPI allocation, coalesces and pads payloads before encryption, updates IVs, queues messages on normal or prioritized transport queues, sends informational NOTIFY/DELETE/DPD exchanges, and runs post-send hooks.

SA negotiation walks transform payloads bottom-up to select the first compatible protection suite, backtracking when a full-suite validator rejects a partially compatible choice. Duplicate handling retransmits the previous final response when appropriate and clears old retransmit state once the peer progresses.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/message.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/message.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/message.h

Public message-layer header.

It defines payload index nodes, payload handled marker `PL_MARK`, post-send hook nodes, `struct message`, and message flags for last message, encrypted state, send-queue membership, prioritized sending, authentication, NAT-T reception, and no-retransmit behavior.

It declares message construction, reply allocation, payload insertion, SA payload construction, receive/send/drop/delete/notification/info handling, raw dump, SA negotiation, message copy, post-send hook registration/execution, header setup, retransmit send callback, and first-payload lookup.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/message.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/monitor.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/monitor.c

Privilege-separation monitor implementation.

`monitor_init()` creates a socketpair, forks, chroots and drops the child to `_isakmpd`, and leaves the parent as a privileged broker. The unprivileged side requests privileged operations by writing command codes and arguments over the socket, sometimes passing or receiving file descriptors.

Brokered operations include opening PF_KEY sockets, opening/statting/fopening approved files, setting selected socket options, binding sockets to allowed ports, and enumerating readable regular/symlink files in approved directories. The privileged side validates file paths against `/var/run/` or read-only `ISAKMPD_ROOT`, validates socket option levels/names, and restricts binds to AF_INET/AF_INET6 with matching lengths and either port 500 or non-privileged ports.

The monitor also owns child signal forwarding, shutdown cleanup of FIFO/PID files, reliable must-read/must-write helpers based on atomicio-style loops, and fd-passing integration through `mm_send_fd()`/`mm_receive_fd()`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/monitor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/monitor.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/monitor.h

Privilege-separation monitor API header.

It defines the unprivileged user `_isakmpd`, default ISAKMP privileged port 500, monitor request opcodes, and declarations for monitor initialization/loop/exit, fd passing, monitored file operations, socket option and bind brokers, directory read requests, init completion signaling, and PF_KEY socket opening.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/monitor.h -->