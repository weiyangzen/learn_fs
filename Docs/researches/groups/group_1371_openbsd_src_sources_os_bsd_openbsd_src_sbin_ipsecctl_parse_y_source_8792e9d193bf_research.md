# Group Research: group_1371_openbsd_src_sources_os_bsd_openbsd_src_sbin_ipsecctl_parse_y_source_8792e9d193bf

Scope verified against `Docs/research_subset_a.md`: `sources/os/bsd/openbsd-src` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ipsecctl/parse.y -->
# File Research: sources/os/bsd/openbsd-src/sbin/ipsecctl/parse.y

This is the yacc grammar, lexer, and rule-construction core for `ipsecctl` configuration parsing.

Key responsibilities:
- Parses `ipsec.conf`-style statements for IKE rules, flow rules, static SAs, TCP MD5 SAs, includes, and macro assignments.
- Defines supported authentication, encryption, compression, and DH group transforms via `authxfs`, `encxfs`, `compxfs`, and `groupxfs`.
- Converts parsed syntax into `struct ipsec_rule` instances and appends expanded rules through `ipsecctl_add_rule`.
- Handles include stacks, macro expansion, lexical scanning, quoted strings, comments, numbers, and keyword lookup.
- Enforces config file secrecy for the top-level file and key files.
- Resolves host specifications from numeric IPv4/IPv6, DNS, interface names, interface groups, and `any`.
- Expands `any` into IPv4 and IPv6 wildcard networks.
- Validates address-family combinations, transform/key compatibility, SPI ranges, port/protocol constraints, NAT syntax, and static-key restrictions.
- Builds reverse flow and reverse SA rules for bidirectional declarations.
- Supports SA bundles by creating `RULE_BUNDLE` entries connecting sequential destination/SPI pairs.
- Supports `ike interface secN ...` rules by marking IKE rules with `IPSEC_RULE_F_IFACE` and storing the interface unit.

Important functions and data:
- `parse_rules()` initializes parsing, pushes the top file, invokes `yyparse`, and frees macros.
- `yylex()`, `lgetc()`, `lungetc()`, and `findeol()` implement the scanner and pushback handling.
- `pushfile()`/`popfile()` manage nested include files.
- `symset()`, `symget()`, and `cmdline_symset()` implement macros.
- `host()`, `host_v4()`, `host_v6()`, `host_dns()`, `host_if()`, `ifa_lookup()`, and `ifa_grouplookup()` resolve rule endpoints.
- `parsekey()` and `parsekeyfile()` parse hex key material.
- `create_sa()`, `create_flow()`, `create_ike()`, `reverse_sa()`, `reverse_rule()`, and `create_sabundle()` construct in-memory rules.
- `expand_rule()` performs host-list cross-product expansion and inserts concrete rules.
- `validate_sa()` applies protocol-specific transform/key rules.

Notable behavior:
- ESP defaults to AES encryption and HMAC-SHA2-256 authentication when omitted where appropriate.
- AH defaults to HMAC-SHA2-256 authentication.
- IPCOMP defaults to deflate compression.
- Static keys reject transforms marked as `nostatic`, including AEAD/CTR-style entries that require non-static handling.
- AEAD transforms reject explicit separate authentication.
- Port-specific flows require TCP or UDP protocol.
- Flow types default to `require` for AH/ESP and `use` for IPIP/IPCOMP.
- The parser accepts macros with `$name` substitution and warns about unused macros at high verbosity.
- Key file length is capped by `KEYSIZE_LIMIT`.

Dependencies:
- Consumes structures and constants from `ipsecctl.h`.
- Feeds parsed rules into the broader `ipsecctl` rule queues.
- Uses OpenBSD networking APIs such as `getifaddrs`, interface group ioctls, `getaddrinfo`, and `inet_net_pton`.

Research notes:
- This file is the semantic bridge between user configuration and the PF_KEY emission layer.
- It combines parsing, validation, expansion, and memory ownership logic in one large module, so changes to config syntax often have direct rule-generation consequences.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ipsecctl/parse.y -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ipsecctl/pfkdump.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/ipsecctl/pfkdump.c

This file decodes and prints PF_KEY SADB messages for `ipsecctl`.

Key responsibilities:
- Maps PF_KEY message, extension, SA, algorithm, state, identity, flow, and flag numeric IDs to human-readable names.
- Prints SADB extensions in verbose monitor/dump output.
- Reconstructs `struct ipsec_rule` views from SADB SA messages for normal `ipsecctl` rule-style output.
- Supports monitor output for live PF_KEY messages.
- Prints raw PF_KEY byte dumps when requested.

Important functions and data:
- `ext_types`, `msg_types`, `sa_types`, `auth_types`, `enc_types`, `comp_types`, `flag_types`, `identity_types`, `flow_types`, and `states` are local lookup tables.
- `setup_extensions()` walks a PF_KEY message and indexes extensions by extension type.
- `pfkey_print_sa()` converts SADB SA messages back into `struct ipsec_rule` and calls `ipsecctl_print_rule`.
- `pfkey_monitor_sa()` prints message header and each extension.
- `pfkey_print_raw()` prints raw bytes.
- `pfkey_get_spi()` extracts the SPI from an indexed SA extension.
- `print_sa()`, `print_addr()`, `print_key()`, `print_life()`, `print_flow()`, `print_counter()`, and related helpers format individual extension types.
- `parse_addr()`, `parse_key()`, and `parse_satype()` adapt SADB extensions into `ipsecctl` structures.

Notable behavior:
- Authentication and encryption algorithm variants are inferred from PF_KEY algorithm IDs and key lengths.
- Key material is hidden unless `IPSECCTL_OPT_SHOWKEY` is set; key extensions are nulled before rule printing when hidden.
- `print_key()` zeroes key bytes after printing them.
- Bundle output is reconstructed when `SADB_X_EXT_SA2`, `SADB_X_EXT_DST2`, and `SADB_X_EXT_SATYPE2` are present.
- Verbose output prints all known extensions after the reconstructed rule.

Dependencies:
- Uses `ipsecctl.h` structures and transform arrays declared elsewhere.
- Uses `pfkey.h` for public PF_KEY dump/monitor prototypes.
- Consumes OpenBSD PF_KEY V2 and IPsec extension definitions from system headers.

Research notes:
- This module is read-only/diagnostic relative to the kernel, but it must mirror encoding decisions in `pfkey.c` and transform tables in `parse.y`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ipsecctl/pfkdump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ipsecctl/pfkey.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/ipsecctl/pfkey.c

This file emits, receives, monitors, and partially parses PF_KEY V2 messages for `ipsecctl`.

Key responsibilities:
- Opens a raw `PF_KEY` socket.
- Builds PF_KEY messages for flow add/delete, SA add/delete, SA bundle grouping, flush, and promiscuous monitoring.
- Converts `struct ipsec_rule` objects into kernel SADB operations.
- Reads PF_KEY replies and propagates kernel errors.
- Parses SADB flow messages back into partial `struct ipsec_rule` objects.
- Implements live PF_KEY monitor mode.

Important functions:
- `pfkey_init()` opens the global PF_KEY socket.
- `pfkey_ipsec_establish()` dispatches `RULE_FLOW`, `RULE_SA`, and `RULE_BUNDLE` operations to the correct PF_KEY builder.
- `pfkey_flow()` constructs `SADB_X_ADDFLOW`/`SADB_X_DELFLOW` messages with flow type, protocol, src/dst flows, masks, optional local/peer addresses, and optional identities.
- `pfkey_sa()` constructs `SADB_ADD`/`SADB_DELETE` messages with SA, src/dst addresses, optional UDP encapsulation, and optional key extensions.
- `pfkey_sabundle()` constructs `SADB_X_GRPSPIS` messages for bundle relationships.
- `pfkey_reply()` reads a complete reply based on the message header length.
- `pfkey_parse()` parses selected SADB flow extensions into `struct ipsec_rule`.
- `pfkey_ipsec_flush()` sends `SADB_FLUSH`.
- `pfkey_monitor()` enables PF_KEY promiscuous mode and loops on `poll`.
- `pfkey_promisc()` enables promiscuous PF_KEY delivery.

Notable behavior:
- Message lengths are expressed in `PFKEYV2_CHUNK` units and extension payloads are rounded up to 8-byte alignment.
- IPv4 and IPv6 source/destination addresses and masks are encoded into `sockaddr_storage`.
- Port-specific masks use `0xffff` when source or destination ports are set.
- Flow identities are encoded as `SADB_EXT_IDENTITY_SRC` and `SADB_EXT_IDENTITY_DST`.
- Static SA algorithm mapping mirrors transform IDs from `parse.y`.
- UDP encapsulation sets `SADB_X_SAFLAGS_UDPENCAP` and adds `SADB_X_EXT_UDPENCAP`.
- `pfkey_reply()` treats `EEXIST` as non-fatal for no-data callers.
- Monitor mode pledges to `stdio` after setup.

Dependencies:
- Uses `ipsecctl.h` rule structures.
- Uses `pfkey.h` declarations.
- Requires OpenBSD PF_KEY V2, IPsec, `writev`, `poll`, and socket APIs.

Research notes:
- This is the kernel interface layer for `ipsecctl`.
- `pfkey_flow()` and `pfkey_sa()` are sensitive to structure sizes, alignment, and OpenBSD-specific SADB extension semantics.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ipsecctl/pfkey.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ipsecctl/pfkey.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/ipsecctl/pfkey.h

This header declares the public PF_KEY interface used by `ipsecctl`.

Key contents:
- Defines `PFKEYV2_CHUNK` as `sizeof(u_int64_t)`, the unit used for SADB message and extension lengths.
- Declares parsing, printing, monitoring, socket initialization, flush, rule establishment, raw dump, and SPI extraction functions.

Declared functions:
- `pfkey_parse`
- `pfkey_print_sa`
- `pfkey_monitor_sa`
- `pfkey_print_raw`
- `pfkey_ipsec_establish`
- `pfkey_ipsec_flush`
- `pfkey_init`
- `pfkey_monitor`
- `pfkey_get_spi`

Dependencies:
- Assumes `struct sadb_msg` and `struct ipsec_rule` are visible to includers.

Research notes:
- This is a small boundary header between PF_KEY implementation/dump code and the rest of `ipsecctl`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/ipsecctl/pfkey.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/Makefile

This is the OpenBSD build file for the `isakmpd` daemon.

Key responsibilities:
- Defines `PROG=isakmpd`.
- Lists core source files for ISAKMP/IKE, IPsec DOI, PF_KEY, policy, monitor, NAT traversal, transport, crypto, UI, and utility support.
- Adds `.PATH` for OpenBSD-specific system-dependent sources.
- Defines generated constant/field headers and sources.
- Invokes `genconstants.sh` and `genfields.sh` to generate `exchange_num`, `ipsec_num`, `isakmp_num`, `ipsec_fld`, and `isakmp_fld` artifacts.
- Installs manual pages `isakmpd.8`, `isakmpd.conf.5`, and `isakmpd.policy.5`.
- Sets warning flags and include paths.
- Links against KeyNote, crypto, math, and optional LWRES DNSSEC library.
- Includes commented options for debugging and DNSSEC support.
- Ensures generated files are built first with `BUILDFIRST`.

Dependencies:
- OpenBSD `bsd.prog.mk`.
- Local generator scripts and `.cst`/`.fld` metadata files.
- Libraries: `libkeynote`, `libcrypto`, `libm`, and optionally `liblwres`.

Research notes:
- `dnssec.c` is present in the tree but not included by default unless DNSSEC support is enabled.
- The build relies on generated protocol constants and field accessor code.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/app.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/app.c

This file is the application-interface wrapper for `isakmpd`.

Key responsibilities:
- Opens the daemon’s PF_KEY application channel unless disabled.
- Dispatches application events to the PF_KEY v2 handler.

Important symbols:
- `int app_socket`: global application socket descriptor.
- `int app_none`: disables application setup when nonzero.
- `app_init()`: opens the monitored PF_KEY v2 connection via `monitor_pf_key_v2_open`.
- `app_handler()`: calls `pf_key_v2_handler(app_socket)`.

Dependencies:
- `monitor.h` for monitored PF_KEY socket opening.
- `pf_key_v2.h` for PF_KEY application handling.
- `log.h` for fatal logging.

Research notes:
- The file intentionally acts as a thin wrapper around one system-dependent application backend.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/app.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/app.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/app.h

This header declares the `isakmpd` application wrapper API.

Key contents:
- Include guard `_APP_H_`.
- Extern declarations for `app_socket` and `app_none`.
- Function prototypes for `app_init()` and `app_handler()`.

Research notes:
- This header exposes only the small application-channel lifecycle used by the daemon event loop.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/app.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/attribute.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/attribute.c

This file implements ISAKMP attribute encoding and iteration helpers.

Key responsibilities:
- Encodes basic attributes where the value is carried directly in the length/value field.
- Encodes variable-length attributes with explicit data bytes.
- Iterates over a buffer of ISAKMP attributes and invokes a callback per attribute.
- Looks up named configuration constants and writes them as attributes.

Important functions:
- `attribute_set_basic()`: writes an attribute with the ISAKMP basic format bit set.
- `attribute_set_var()`: writes a variable-length attribute and copies payload bytes.
- `attribute_map()`: safely walks an attribute area, handling basic and variable formats.
- `attribute_set_constant()`: reads a config tag, maps its string to a constant value, and emits a basic attribute.

Dependencies:
- Generated ISAKMP field access macros from `isakmp.h`.
- Config lookup via `conf_get_str`.
- Constant mapping via `constant_value`.
- Logging for missing config values.

Research notes:
- `attribute_map()` performs bounds checks before invoking callbacks, making it central to safe transform/proposal parsing.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/attribute.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/attribute.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/attribute.h

This header declares ISAKMP attribute helper functions.

Key contents:
- Forward declaration of `struct constant_map`.
- Prototypes for:
  - `attribute_map`
  - `attribute_set_basic`
  - `attribute_set_constant`
  - `attribute_set_var`

Research notes:
- This is a compact shared interface for modules that encode or validate ISAKMP transform attributes.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/attribute.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/cert.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/cert.c

This file provides certificate handler dispatch for `isakmpd`.

Key responsibilities:
- Registers built-in certificate handlers for X.509 signatures and KeyNote.
- Initializes certificate and CRL subsystems.
- Looks up handlers by ISAKMP certificate encoding ID.
- Decodes certificate request acceptable-authority payloads.
- Frees arrays of certificate subject buffers.

Important data and functions:
- `cert_handler[]`: table of X.509 and KeyNote handler vtables.
- `cert_init()`: runs available `cert_init` callbacks.
- `crl_init()`: runs available `crl_init` callbacks.
- `cert_get()`: finds a handler by encoding ID.
- `certreq_decode()`: validates handler availability, decodes authority data, preserves raw CA bytes, and returns `struct certreq_aca`.
- `cert_free_subjects()`: frees subject ID/length arrays.

Dependencies:
- X.509 support via `x509.h`.
- KeyNote certificate support via `policy.h`.
- ISAKMP certificate encoding constants from `isakmp_num.h`.

Research notes:
- The handler table abstracts certificate storage, validation, serialization, printable conversion, and key extraction across certificate formats.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/cert.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/cert.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/cert.h

This header defines the certificate handler abstraction for `isakmpd`.

Key contents:
- `struct cert_handler`: a vtable for certificate operations including init, CRL init, parse, validate, insert, free, certificate-request handling, obtain, key extraction, subject extraction, duplication, serialization, printable conversion, and CA counting.
- `struct certreq_aca`: stores decoded acceptable certificate authority data, raw CA bytes, handler pointer, and list linkage.
- Prototypes for certificate request decoding, subject freeing, handler lookup, certificate initialization, and CRL initialization.

Dependencies:
- Uses `TAILQ_ENTRY` from `<sys/queue.h>`.

Research notes:
- This header is a core extension point for supported certificate encodings in IKE authentication.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/cert.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/conf.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/conf.c

This file implements the `isakmpd` configuration database, parser, transactions, defaults, and reporting.

Key responsibilities:
- Parses INI-like configuration files with `[section]` headers and `tag=value` assignments.
- Stores configuration bindings in a 256-bucket hash table keyed by section.
- Supports transactional changes with queued set/remove/remove-section operations.
- Loads and applies a large matrix of default phase 1 and phase 2 configuration sections.
- Provides typed accessors for strings, numbers, socket addresses, numeric ranges, comma-separated lists, and section tag lists.
- Handles SIGHUP-style reinitialization by replacing current configuration.
- Dumps non-default running configuration for reports.

Important structures:
- `struct conf_binding`: committed config entry with section, tag, value, and default flag.
- `struct conf_trans`: queued transaction operation.
- `struct conf_list` and `struct conf_list_node`: list return types declared in `conf.h`.

Important functions:
- `conf_init()` initializes hash buckets and the transaction queue, then calls `conf_reinit`.
- `conf_reinit()` opens the config through monitor helpers, checks secrecy, reads it, parses it, loads defaults, and commits.
- `conf_parse()` and `conf_parse_line()` implement file parsing.
- `conf_load_defaults()` creates default general, X.509, KeyNote, lifetime, phase 1, main-mode transform, and quick-mode suite sections.
- `conf_load_defaults_mm()` and `conf_load_defaults_qm()` generate individual main-mode and quick-mode defaults.
- `conf_get_str()`, `conf_get_num()`, `conf_get_address()`, `conf_match_num()`, `conf_get_list()`, and `conf_get_tag_list()` are accessors.
- `conf_begin()`, `conf_set()`, `conf_remove()`, `conf_remove_section()`, and `conf_end()` implement transactions.
- `conf_report()` emits non-default configuration entries.

Notable behavior:
- Duplicate tags are ignored unless override is requested.
- Defaults are marked with `is_default` so reports can omit them.
- Config file absence is tolerated; defaults are still loaded.
- Default generation covers many combinations of encryption, hash, authentication method, DH group, protocol, tunnel/transport mode, and PFS.
- AH defaults reject encryption; ESP defaults reject missing encryption; GCM/GMAC reject separate authentication in quick-mode default generation.
- Escaped newlines are folded into spaces during parse.

Dependencies:
- Uses monitor file-open and secrecy-check helpers.
- Uses `text2sockaddr` from utility code for address parsing.
- Uses `log` for diagnostics.
- Depends on constants from `conf.h`.

Research notes:
- This is the central configuration service for many `isakmpd` modules.
- The default matrix is extensive and provides implicit named sections even when the config file is small or absent.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/conf.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/conf.h

This header defines configuration defaults and the public configuration API.

Key contents:
- Root paths and default config/policy/certificate/keynote directories under `/etc/isakmpd/`.
- Default lifetime tags and values for main mode and quick mode.
- Default key length ranges for Blowfish and AES.
- General defaults such as retransmits, exchange max time, KeyNote usage, policy file, and Delete-SAs behavior.
- Default phase 1 configuration section and transform name.
- `struct conf_list_node` and `struct conf_list` for comma-separated config lists.
- Extern `conf_path`.
- Prototypes for transaction, accessor, initialization, reload, remove, set, free-list, match, and report functions.

Research notes:
- The header exposes the default configuration contract consumed by most daemon subsystems.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/conf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/connection.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/connection.c

This file manages configured active and passive IPsec/IKE connections.

Key responsibilities:
- Initializes active connections from the `Phase 2` `Connections` list.
- Records passive connections from active connections not marked `active-only` and from `Passive-Connections`.
- Schedules recurring checks for required active connections.
- Matches incoming passive exchanges by local/remote ISAKMP IDs.
- Tears down and rebuilds connection state during reinitialization.
- Reports active and passive connection state.

Important structures:
- `struct connection`: active connection name and timer event.
- `struct connection_passive`: passive connection name plus encoded local/remote IDs and lengths.
- Global TAILQs `connections` and `connections_passive`.

Important functions:
- `connection_init()`: populates active and passive connection lists from config.
- `connection_setup()`: adds an active connection and schedules an immediate checker event.
- `connection_checker()`: reschedules itself and calls `pf_key_v2_connection_check`.
- `connection_record_passive()`: builds and stores local/remote IDs for passive matching.
- `connection_passive_lookup_by_ids()`: finds passive config by comparing peer IDs, including a local-ID-only road-warrior fallback.
- `connection_teardown()` and `connection_passive_teardown()` remove entries.
- `connection_reinit()` clears and rebuilds connection lists.
- `connection_report()` logs current connection state.

Dependencies:
- Config service from `conf.h`.
- IPsec DOI ID construction via `ipsec_build_id`.
- PF_KEY v2 checking via `pf_key_v2_connection_check`.
- Timer and UI state.
- DOI lookup for report-time ID decoding.

Research notes:
- This module ties persistent configuration to daemon liveness behavior: active connections are periodically rechecked, while passive connections are used to select config for inbound exchanges.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/connection.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/connection.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/connection.h

This header declares the connection management API.

Key contents:
- Prototypes for:
  - `connection_exist`
  - `connection_init`
  - `connection_passive_lookup_by_ids`
  - `connection_reinit`
  - `connection_report`
  - `connection_setup`
  - `connection_record_passive`
  - `connection_teardown`

Research notes:
- This API exposes active/passive connection lifecycle and lookup to the daemon and exchange handling code.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/connection.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/constants.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/constants.c

This file implements helpers for mapping protocol/config constants between names and numeric values.

Key responsibilities:
- Look up numeric values by case-insensitive string name.
- Look up names by numeric value.
- Look up a linked map by numeric value.
- Produce fallback printable names for unknown values.
- Search multiple maps for a name.

Important functions:
- `constant_value()`
- `constant_lookup()`
- `constant_link_lookup()`
- `constant_name()`
- `constant_name_maps()`

Notable behavior:
- Unknown names map to `0`.
- Unknown values are formatted into static buffers as `<Unknown N>`.
- `constant_name()` and `constant_name_maps()` use static storage, so callers must treat returned unknown strings as transient.

Dependencies:
- `struct constant_map` from `constants.h`.

Research notes:
- This utility underpins config and protocol debugging where generated constant maps are used.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/constants.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/constants.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/constants.h

This header defines the generic constant-map structure and lookup API.

Key contents:
- `struct constant_map` with `value`, `name`, and optional linked map pointer.
- Prototypes for:
  - `constant_link_lookup`
  - `constant_lookup`
  - `constant_name`
  - `constant_name_maps`
  - `constant_value`

Research notes:
- Generated protocol constant tables can share this common lookup format.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/constants.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/cookie.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/cookie.c

This file generates ISAKMP anti-clogging cookies.

Key responsibilities:
- Computes a cookie using SHA1 over transport endpoint addresses, optional initiator cookie data, and fresh random secret bytes.

Important function:
- `cookie_gen(struct transport *t, struct exchange *exchange, u_int8_t *buf, size_t len)`

Notable behavior:
- Uses destination and source socket addresses from the transport vtable.
- For responder-side exchanges, includes the initiator cookie from the exchange header.
- Mixes in `COOKIE_SECRET_SIZE` bytes from `arc4random_buf`.
- Copies the requested number of digest bytes to the caller buffer.

Dependencies:
- Hash framework via `hash_get(HASH_SHA1)`.
- Transport endpoint accessors.
- Exchange cookie fields.

Research notes:
- The cookie is stateless from the peer perspective but includes endpoint and exchange data to resist request flooding.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/cookie.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/cookie.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/cookie.h

This header declares the cookie generation interface.

Key contents:
- Forward declarations for `struct exchange` and `struct transport`.
- Prototype for `cookie_gen`.

Research notes:
- The header keeps cookie generation independent from full transport/exchange definitions.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/cookie.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/crypto.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/crypto.c

This file implements block cipher transform handling for IKE encryption.

Key responsibilities:
- Defines supported CBC transforms: 3DES, Blowfish, CAST, and AES.
- Initializes cipher-specific key schedules.
- Performs in-place encryption/decryption.
- Manages rolling IV state.
- Clones key state for exchange processing.

Important data and functions:
- `transforms[]`: table of `struct crypto_xf` entries with IDs, names, key ranges, block sizes, and function pointers.
- `des3_init`, `des3_encrypt`, `des3_decrypt`
- `blf_init`, `blf_encrypt`, `blf_decrypt`
- `cast_init`, `cast1_encrypt`, `cast1_decrypt`
- `aes_init`, `aes_encrypt`, `aes_decrypt`
- `crypto_get()`: finds transform by enum ID.
- `crypto_init()`: validates key length, allocates `keystate`, initializes IV pointers, and runs transform init.
- `crypto_init_iv()`, `crypto_update_iv()`: set and swap IV buffers.
- `crypto_encrypt()` and `crypto_decrypt()`: call transform methods and update IV state.
- `crypto_clone_keystate()`: copies state and rebinds IV pointers to the clone’s storage.

Notable behavior:
- Blowfish CBC is implemented manually using big-endian block helpers and XOR macros.
- 3DES, CAST, and AES use OpenSSL/libcrypto routines.
- AES keeps separate encrypt and decrypt key schedules.
- Debug logging can dump keys, IVs, and buffers depending on log level.

Dependencies:
- `crypto.h` for transform and key state structures.
- OpenSSL DES/CAST/AES APIs and OpenBSD Blowfish support.
- Logging framework.

Research notes:
- This is IKE payload encryption support, not kernel ESP encryption.
- Key length policy is enforced before cipher initialization.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/crypto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/crypto.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/crypto.h

This header defines IKE crypto transform types, key state, block helpers, and crypto APIs.

Key contents:
- Includes OpenSSL DES, CAST, AES, and OpenBSD Blowfish types.
- Defines XOR/copy macros for 64-bit block operations, currently using the 32-bit implementation path.
- Defines big-endian 32-bit set/get macros.
- Defines `BLOCKSIZE` as 8 and `MAXBLK` as `AES_BLOCK_SIZE`.
- `struct keystate`: transform back pointer, IV buffers, active IV pointers, and cipher key schedule union.
- Cipher key schedule aliases: `ks_des`, `ks_blf`, `ks_cast`, `ks_aes`.
- `enum transform`: Oakley transform IDs for DES, IDEA, Blowfish, RC5, 3DES, CAST, AES.
- `enum cryptoerr`: crypto initialization error codes.
- `struct crypto_xf`: transform descriptor with ID, name, key range, block size, optional state pointer, and function pointers.
- Prototypes for transform lookup, initialization, IV management, encryption/decryption, and state cloning.

Research notes:
- The header exposes a generic transform interface used by exchange/keying code.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/crypto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/dh.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/dh.c

This file implements Diffie-Hellman group support for `isakmpd`.

Key responsibilities:
- Defines supported IKE DH groups, including MODP groups 1, 2, 5, 14-18 and elliptic-curve groups 19-21 and 26-30, with optional EC2N groups when OpenSSL supports them.
- Instantiates group objects by numeric group ID.
- Initializes MODP or EC group-specific state.
- Generates public exchange values.
- Computes shared secrets.
- Converts EC points between raw IKE wire format and OpenSSL `EC_POINT`.

Important data and functions:
- `ike_groups[]`: group metadata including type, ID, bit size, MODP prime/generator strings, or EC NID.
- `group_get()`: finds group metadata, allocates `struct group`, assigns function pointers, and initializes it.
- `group_free()`: frees DH/EC state and group memory.
- `dh_getlen()`, `dh_secretlen()`, `dh_create_exchange()`, `dh_create_shared()`: generic wrappers.
- `modp_init()`: builds OpenSSL `DH` parameters from hex prime/generator.
- `modp_create_exchange()`: generates DH public key and zero-pads to fixed group length.
- `modp_create_shared()`: computes shared key and zero-pads.
- `ec_init()`: creates and validates an EC key for the configured curve.
- `ec_getlen()` and `ec_secretlen()`: compute public exchange and shared-secret sizes.
- `ec_create_exchange()`: serializes the local EC public point.
- `ec_create_shared()`: validates peer point, multiplies by private key, and serializes x-coordinate only.
- `ec_point2raw()` and `ec_raw2point()` handle fixed-width EC coordinate serialization.

Notable behavior:
- ECP shared secret uses only the x-coordinate per RFC 5903.
- EC peer public keys are validated through an `EC_KEY` wrapper before shared secret computation.
- Sensitive BIGNUMs and EC points are cleared during cleanup.
- `DH_MAXSZ` in the header allows up to 8192-bit MODP output.

Dependencies:
- OpenSSL DH, EC, ECDH, BN, and object NID APIs.
- `dh.h` structures.

Research notes:
- This file is the daemon’s central key agreement implementation and must remain aligned with IKE group IDs exposed in configuration defaults and transform negotiation.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/dh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/dh.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/dh.h

This header defines DH group metadata, runtime group state, and the public DH API.

Key contents:
- `enum group_type`: MODP, EC2N, and ECP group classes.
- `struct group_id`: static group specification with type, ID, bit size, MODP parameters, and EC NID.
- `struct group`: runtime group object with ID, spec pointer, DH/EC backend pointers, and method callbacks.
- `DH_MAXSZ` set to 1024 bytes for 8192-bit groups.
- Prototypes for group initialization/free/lookup and DH exchange/shared-secret operations.

Research notes:
- The runtime `struct group` is backend-polymorphic through function pointers assigned in `group_get`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/dh.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/dnssec.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/dnssec.c

This file implements optional DNSSEC KEY record retrieval for IKE authentication keys.

Key responsibilities:
- Builds DNS names from peer ID payloads.
- Fetches DNS KEY records through `getrrsetbyname`.
- Requires validated DNSSEC responses.
- Filters KEY records for IPsec protocol and requested algorithm.
- Converts DNS RSA KEY wire format into an OpenSSL RSA object.

Important functions:
- `dns_get_key(int type, struct message *msg, int *keylen)`: retrieves a matching DNS KEY record for RSA signature authentication.
- `dns_RSA_dns_to_x509(u_int8_t *key, int keylen, RSA **rsa_key)`: parses DNS RSA exponent/modulus format into `RSA`.

Notable behavior:
- Supports RSA signature lookup; RSA encryption and DSS paths are stubbed out.
- IPv4 IDs are converted to reverse `in-addr.arpa` names.
- FQDN IDs get a trailing dot.
- USER_FQDN IDs are converted from `user@host` to `user._ipsec.host.` by default.
- IPv6 ID DNS lookup is not implemented.
- Unvalidated DNS responses are rejected.
- Only the first matching usable key is returned.

Dependencies:
- Optional LWRES headers when built with `LWRES`; otherwise standard resolver headers.
- Exchange/message ID data.
- IPsec/IKE numeric constants.
- OpenSSL RSA and BIGNUM APIs.

Research notes:
- The file is not in the default Makefile source list unless DNSSEC support is enabled.
- It mutates the USER_FQDN ID buffer temporarily by inserting a NUL at `@`, which callers must account for if sharing that storage.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/dnssec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/dnssec.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/dnssec.h

This header declares optional DNSSEC key lookup helpers.

Key contents:
- Includes `libcrypto.h` and `message.h`.
- Prototypes:
  - `dns_get_key`
  - `dns_RSA_dns_to_x509`
- Fallback defines:
  - `DNS_KEYALG_RSA`
  - `DNS_KEYPROTO_IPSEC`

Research notes:
- This header exposes DNS KEY retrieval and RSA conversion to authentication code when DNSSEC support is compiled in.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/dnssec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/doi.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/doi.c

This file implements the DOI registry for `isakmpd`.

Key responsibilities:
- Maintains a global list of registered Domain of Interpretation handlers.
- Initializes the registry.
- Looks up a DOI by ID.
- Registers DOI handler structures.

Important functions:
- `doi_init()`: initializes the DOI list.
- `doi_lookup(u_int8_t doi_id)`: linear search by DOI ID.
- `doi_register(struct doi *doi)`: inserts a handler into the registry.

Dependencies:
- `struct doi` from `doi.h`.
- BSD list macros.

Research notes:
- This is a small dispatcher registry; most DOI-specific behavior lives behind the function pointers in `struct doi`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/doi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/doi.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/doi.h

This header defines the DOI handler interface for `isakmpd`.

Key contents:
- Forward declarations for exchange, message, payload, protocol, SA, and keystate structures.
- `struct doi`: a large vtable for DOI-specific behavior, including:
  - object size declarations for exchange/SA/proto data
  - attribute debugging, validation, and incompatibility checks
  - SPI deletion and extraction
  - exchange script selection
  - exchange finalization and cleanup
  - keystate lookup
  - leftover payload handling
  - informational pre/post hooks
  - protocol initialization
  - situation setup/validation
  - SPI size, protocol, transform, notification, ID, and key validation
  - initiator/responder handlers
  - ID decoding for reports/debugging
- Registry API prototypes:
  - `doi_init`
  - `doi_lookup`
  - `doi_register`

Research notes:
- This is the abstraction boundary between generic ISAKMP exchange machinery and IPsec DOI-specific policy/proposal semantics.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/doi.h -->