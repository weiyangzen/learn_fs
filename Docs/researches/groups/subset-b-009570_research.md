# Research Group subset-b-009570

This grouped report covers the requested cifs-utils build, mount, keyring, Kerberos upcall, ID mapping, ACL, resolver, PAM, helper-library, request-key, and manpage files under `sources/user-network-fs/cifs-utils`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/Makefile.am -->
# sources/user-network-fs/cifs-utils/Makefile.am

## Purpose

`Makefile.am` is the top-level Automake recipe for cifs-utils. It wires the always-built `mount.cifs` helper and conditional utilities such as `cifs.upcall`, `cifscreds`, `cifs.idmap`, `getcifsacl`, `setcifsacl`, `idmapwb.so`, `pam_cifscreds.so`, Python scripts, and generated man pages.

## Important APIs, Types, and Functions

The important variables are `AM_CFLAGS`, `root_exec_sbindir`, `root_exec_sbin_PROGRAMS`, `mount_cifs_SOURCES`, `resolve_hosts_SOURCES`, `resolve_hosts_LDADD`, `rst_man_pages`, `CLEANFILES`, and the conditional program/source/link groups guarded by `CONFIG_CIFSUPCALL`, `CONFIG_CIFSCREDS`, `CONFIG_CIFSIDMAP`, `CONFIG_CIFSACL`, `CONFIG_SMBINFO`, `CONFIG_PYTHON_TOOLS`, `CONFIG_PLUGIN`, `CONFIG_PAM`, and `CONFIG_MAN`.

## Control Flow

Automake expands the conditionals from `configure.ac`. `mount.cifs` is always built from `mount.cifs.c`, `mtab.c`, DNS/CLDAP resolver sources, and `util.c`; optional programs append to `bin_PROGRAMS`, `sbin_PROGRAMS`, `bin_SCRIPTS`, `plugin_PROGRAMS`, or `pam_PROGRAMS`. RST inputs are converted to `.1` or `.8` man pages through the `RST2MAN` suffix rules. Template rules substitute `@sbindir@` and `@pluginpath@` into generated RST files.

## State and Persistence Behavior

The file persists build outputs, generated manpage intermediates, generated request-key snippets, install-time symlinks, and cleanup lists. Runtime persistence is outside the Makefile, but install hooks create `mount.smb3` and manpage symlinks to the CIFS helper.

## Dependencies and Integration Points

It integrates with Autoconf substitutions from `configure.ac`, libtalloc/libresolv for resolver sources, keyutils for keyring helpers, Kerberos/GSSAPI for `cifs.upcall`, `dl` for idmap plugin loading, wbclient for `idmapwb.so`, PAM for `pam_cifscreds.so`, and docutils `rst2man` for manpage generation.

## Risks and Edge Cases

Conditional build drift can silently omit a utility or manpage when a dependency check changes. The plugin and PAM shared objects are hand-linked with `-shared -fpic`, so flags and library ordering matter. Generated RST files must stay listed in `CLEANFILES` or stale substituted paths can survive rebuilds. The uninstall hook references destination paths directly and must keep `DESTDIR` handling correct.

## Test Signals

Useful signals are `autoreconf && ./configure` with all optional features enabled and disabled, `make distcheck`, install/uninstall dry runs with `DESTDIR`, generated manpage diffs, and package builds that confirm every conditional utility links with the expected libraries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/asn1.c -->
# sources/user-network-fs/cifs-utils/asn1.c

## Purpose

`asn1.c` implements a small BER/ASN.1 writer used by cifs-utils for CLDAP query generation and SPNEGO-related encoding. It allocates expandable talloc-backed buffers, writes primitive bytes and octet strings, encodes OID strings, and fixes up nested tag lengths after payloads are written.

## Important APIs, Types, and Functions

The public functions are `asn1_init`, `asn1_free`, `asn1_write`, `asn1_write_uint8`, `asn1_push_tag`, `asn1_pop_tag`, `ber_write_OID_String`, `asn1_write_OID`, and `asn1_write_OctetString`. `asn1_push_tag` records the current offset in a `struct nesting`; `asn1_pop_tag` computes payload length and rewrites BER short or long-form length bytes.

## Control Flow

Callers create `ASN1_DATA`, push a tag, write nested fields, and pop the tag once the payload is complete. `asn1_write` grows `data->data` with `talloc_realloc` and advances `ofs`. `asn1_pop_tag` initially assumes a one-byte length placeholder; if the payload exceeds 127, 255, 65535, or 16777215 bytes, it appends padding bytes, `memmove`s payload data forward, and emits the corresponding long-form BER length.

## State and Persistence Behavior

All state is in `struct asn1_data`: the byte buffer, allocated length, current offset, nested tag stack, and sticky `has_error` flag. Once an error is set, later writes fail. No process-global or filesystem state is used. Returned OID blobs and ASN.1 buffers are talloc-owned and must be freed with `data_blob_free` or `asn1_free`.

## Dependencies and Integration Points

The file depends on `talloc`, `stdint`, `stdbool`, `data_blob.h`, and `asn1.h`. `cldap_ping.c` uses the tag writer to build LDAP search requests. SPNEGO helpers can also rely on OID encoding semantics shared with Samba-derived code.

## Risks and Edge Cases

Length parameters mix signed `int` with `size_t`, so negative lengths from a bad caller would be dangerous. `ber_write_OID_String` assumes the BER representation is no longer than the input string and only supports component values up to the emitted 35-bit pattern implied by the shifts. `asn1_write_OctetString` does not individually check each nested write and relies on the sticky error flag. Large nesting payloads use in-place `memmove`, so offset correctness is critical.

## Test Signals

Tests should compare encoded tags, OIDs, and octet strings against known BER vectors for short and long lengths, inject allocation failures if possible, and exercise CLDAP query generation as an integration signal. Boundary lengths of 127, 128, 255, 256, 65535, and 65536 are important.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/asn1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/asn1.h -->
# sources/user-network-fs/cifs-utils/asn1.h

## Purpose

`asn1.h` declares the minimal ASN.1/BER writer interface and tag constants used inside cifs-utils.

## Important APIs, Types, and Functions

The header defines `struct nesting`, `struct asn1_data`, `ASN1_DATA`, tag construction macros such as `ASN1_APPLICATION`, `ASN1_SEQUENCE`, `ASN1_CONTEXT`, and constants for common ASN.1 types including OID, integer, boolean, octet string, bit string, enumerated, set, and general string. It declares the writer and OID encoding functions implemented in `asn1.c`.

## Control Flow

The API is stack-shaped: allocate with `asn1_init`, open nested fields with `asn1_push_tag`, write bytes or helper primitives, close nested fields with `asn1_pop_tag`, then free with `asn1_free`. Callers must check boolean returns or `has_error`.

## State and Persistence Behavior

The structures store only transient encoder state. The nested-tag linked list is owned by the `ASN1_DATA` talloc context.

## Dependencies and Integration Points

Consumers must include talloc-visible types and C integer/bool definitions before or around this header. The main in-tree consumer in this work item is `cldap_ping.c`; `data_blob.h` is used for OID output.

## Risks and Edge Cases

The structure layout is not opaque, so callers can mutate internal offsets and error state. `off_t` in `struct nesting` and `struct asn1_data` requires suitable system headers from consumers. `ASN1_MAX_OIDS` is defined but not enforced by the visible writer.

## Test Signals

Compile tests should include this header from C files with the normal project includes. Behavioral tests come through `asn1.c` and any CLDAP or SPNEGO encoder tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/asn1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/checkopts -->
# sources/user-network-fs/cifs-utils/checkopts

## Purpose

`checkopts` is a Python 3 maintenance script that compares CIFS mount options implemented by the kernel with options documented in `mount.cifs.rst`. It reports duplicated documentation, undocumented kernel options, documented-but-missing options, and negative options without positive counterparts.

## Important APIs, Types, and Functions

Key functions are `extract_canonical_opts`, `extract_kernel_opts`, `extract_man_opts`, `format_code`, `sortedset`, `opt_neg`, and `main`. The helper class `RX` wraps `re.search` while preserving the last match for easy capture access.

## Control Flow

`main` parses a kernel `connect.c` path and a mount manpage RST path. `extract_kernel_opts` scans `fsparam_*("name", enum, ...)` lines and later `case Opt_*` blocks to map option names to parser enums and implementation code. `extract_man_opts` scans the RST `OPTION` section and records short option declarations. `main` then computes set differences and alias/negation relationships before printing diagnostics.

## State and Persistence Behavior

The script is stateless except for local dictionaries and stdout output. It reads input files and does not modify them.

## Dependencies and Integration Points

It depends on Python 3 standard modules (`os`, `sys`, `re`, `subprocess`, `argparse`, `collections`). Its integration point is a developer workflow that has both the kernel CIFS parser source and cifs-utils manpage source available.

## Risks and Edge Cases

The parser is regex-based and tightly coupled to current kernel `fsparam_*` and `case Opt_*` formatting plus current RST option layout. It can miss options if macros span lines or documentation formatting changes. It compares names, not semantic behavior, so aliases and negative options need heuristics.

## Test Signals

Run the script against a known kernel CIFS `connect.c` and `mount.cifs.rst` and verify stable output. Unit tests can feed miniature kernel/manpage fixtures with aliases, negations, duplicate docs, ignored options, and malformed sections.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/checkopts -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifs.idmap.c -->
# sources/user-network-fs/cifs-utils/cifs.idmap.c

## Purpose

`cifs.idmap.c` implements the request-key helper that maps CIFS owner/group SIDs to local UID/GID values and maps local UID/GID values back to binary SIDs for kernel CIFS ACL handling.

## Important APIs, Types, and Functions

Important functions are `usage`, `strget`, `str_to_uint`, `cifs_idmap`, and `main`. It uses `struct cifs_sid`, `struct cifs_uxid`, plugin entry points from `idmap_plugin.h`, and keyutils calls `keyctl_set_timeout`, `keyctl_describe_alloc`, and `keyctl_instantiate`.

## Control Flow

`main` parses `--timeout`, `--version`, and a key serial, initializes the ID mapping plugin, sets the key timeout, obtains the key description, and calls `cifs_idmap`. `cifs_idmap` inspects description substrings: `os:` maps owner string to SID then UID, `gs:` maps group string to SID then GID, `oi:` maps owner UID to SID, and `gi:` maps group GID to SID. Successful mappings instantiate the kernel key with either a `uid_t`, `gid_t`, or packed `struct cifs_sid`.

## State and Persistence Behavior

The helper has a process-global plugin handle and emits results into the kernel keyring. The key timeout defaults to 600 seconds but can be set to zero for no expiry. It does not persist data on disk.

## Dependencies and Integration Points

It depends on keyutils, syslog, `cifsacl.h`, `cifsidmap.h`, and the dynamically loaded idmap plugin configured by `IDMAP_PLUGIN_PATH`. It is normally invoked by request-key for `cifs.idmap` keys when CIFS mounts use `cifsacl`.

## Risks and Edge Cases

Description parsing uses substring searches rather than a strict grammar, so malformed descriptions can choose unintended branches. UID/GID parsing validates conversion and overflow, but casts through `unsigned int` before assigning to uid/gid carriers. Plugin failures must propagate correctly or the kernel may cache negative behavior. The allocated description buffer is not freed on the success path shown, which is small but worth noting.

## Test Signals

Tests should mock or provide an idmap plugin and exercise all four key-description forms, bad numeric values, timeout parsing, missing plugin symbols, key instantiation failures, and request-key integration. Winbind-backed integration should confirm SID endian correctness through `idmapwb.so`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifs.idmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifs.idmap.rst.in -->
# sources/user-network-fs/cifs-utils/cifs.idmap.rst.in

## Purpose

`cifs.idmap.rst.in` is the manual-page template for the `cifs.idmap` request-key helper.

## Important APIs, Types, and Functions

The template documents the command synopsis, `--help`, `--timeout`, `--version`, the `cifs.idmap` key type, request-key configuration, plugin path substitution via `@pluginpath@`, and helper path substitution through `@sbindir@`.

## Control Flow

During the build, `Makefile.am` substitutes configured paths and `rst2man` converts the resulting RST into `cifs.idmap.8`. At runtime the documented flow is kernel request-key invoking `cifs.idmap` with a key id, after which the helper maps SID/ID data and instantiates the key.

## State and Persistence Behavior

The document describes key timeout behavior and the operational dependency on the configured plugin symlink. It does not itself persist state.

## Dependencies and Integration Points

It integrates with request-key configuration, `mount.cifs(8)`, the `cifsacl` mount option, and the ID mapping plugin path.

## Risks and Edge Cases

If `@pluginpath@` or `@sbindir@` substitutions are stale, packaged docs will point users to wrong paths. The fallback behavior when helper/plugin is unavailable should remain aligned with kernel and utility behavior.

## Test Signals

Build tests should generate the manpage and inspect substituted paths. Documentation tests should compare option names and defaults with `cifs.idmap.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifs.idmap.rst.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifs.upcall.c -->
# sources/user-network-fs/cifs-utils/cifs.upcall.c

## Purpose

`cifs.upcall.c` implements the CIFS request-key helper for Kerberos/SPNEGO session setup and legacy DNS resolver keys. It decodes kernel key descriptions, switches to the initiating process namespace when requested, obtains Kerberos service tickets or uses GSSAPI/gssproxy, packages session key plus SPNEGO security blob, and instantiates the kernel key.

## Important APIs, Types, and Functions

Important types are `sectype_t`, `struct namespace_file`, and `struct decoded_args`. Major functions include `trim_capabilities`, `drop_all_capabilities`, `get_tgt_time`, `switch_to_process_ns`, `get_cachename_from_process_env`, `get_existing_cc`, `init_cc_from_keytab`, `check_service_ticket_exists`, `cifs_krb5_get_req`, `cifs_gss_get_req`, `handle_krb5_mech`, `decode_key_description`, `setup_key`, `cifs_resolver`, `ip_to_fqdn`, `lowercase_string`, and `main`.

## Control Flow

`main` parses options such as `--no-env-probe`, `--trust-dns`, `--legacy-uid`, `--krb5conf`, `--keytab`, and `--expire`, then describes the key. Resolver keys are handled immediately by `cifs_resolver`, which resolves a hostname and instantiates an IP-address key with a timeout. SPNEGO keys are decoded in a low-privilege child into shared memory, validated for required host/version/sec fields, and checked against `CIFS_SPNEGO_UPCALL_VERSION`. The helper chooses `creduid` unless legacy mode forces `uid`, optionally switches to the application process namespaces, trims capabilities, sets gid/uid, probes the initiating environment for `KRB5CCNAME`, initializes Kerberos, obtains an existing credential cache or keytab-backed memory cache, then attempts a service ticket for the supplied host. If direct host lookup fails it may try a canonical FQDN and, with `--trust-dns`, reverse-resolve the supplied IP. Successful Kerberos data is packed into `struct cifs_spnego_msg` and instantiated.

## State and Persistence Behavior

Process state includes global `krb5_context`, transient credential cache handles, talloc `DATA_BLOB`s, key description buffers, namespace file descriptors, and shared-memory decoded arguments. Persistent effects are kernel key instantiation, DNS resolver key timeout, and optional use of credential caches. The helper scrapes `/proc/<pid>/environ` only before dropping uid and avoids env probing for uid 0.

## Dependencies and Integration Points

It depends on keyutils, MIT/Heimdal Kerberos, GSSAPI/Kerberos extensions, optional libcap-ng, `/proc` namespaces and environment files, passwd/group NSS, syslog, `data_blob.h`, `spnego.h`, and `cifs_spnego.h`. It is invoked by request-key for `cifs.spnego`, `cifs.resolver`, or `dns_resolver`-style descriptions.

## Risks and Edge Cases

This is security-sensitive setuid/capability-adjacent code. Namespace switching, env scraping, credential-cache selection, and uid/gid changes must occur in the intended order. `get_cachename_from_process_env` reads attacker-controlled environment strings and must stay bounded. DNS trust mode can be unsafe if reverse DNS is compromised. There is an apparent error-path condition `if (rc != 0 && key == 0)` before negating keys; if `key` is nonzero on normal request-key failures, this condition may not negate as intended. GSSAPI lucid context handling depends on Kerberos implementation support.

## Test Signals

Strong signals include request-key integration for `cifs.spnego` and DNS resolver keys, Kerberos cache and keytab flows, gssproxy flow with `GSS_USE_PROXY`, container namespace tests, uid versus creduid tests, malformed key descriptions, long host/user fields, reverse-DNS fallback, and key instantiation/negative-instantiation behavior. Static analysis should cover privilege drop ordering and buffer bounds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifs.upcall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifs.upcall.rst.in -->
# sources/user-network-fs/cifs-utils/cifs.upcall.rst.in

## Purpose

`cifs.upcall.rst.in` is the manual-page template for the CIFS Kerberos/SPNEGO and DNS resolver request-key helper.

## Important APIs, Types, and Functions

The template documents CLI options `-c`, `--no-env-probe`, `--krb5conf`, `--keytab`, `--trust-dns`, `--legacy-uid`, `--expire`, and `--version`; the `GSS_USE_PROXY` environment variable; and request-key entries for `cifs.spnego` and `dns_resolver`.

## Control Flow

The build substitutes `@sbindir@` and converts the RST to `cifs.upcall.8`. The documented runtime flow is request-key invoking the helper with a key id, with different behavior for SPNEGO versus DNS resolver keys.

## State and Persistence Behavior

The document describes credential-cache probing, keytab use, default DNS resolver timeout of 600 seconds, and request-key configuration. It does not persist state itself.

## Dependencies and Integration Points

It integrates with `request-key.conf(5)`, `mount.cifs(8)`, `key.dns_resolver(8)`, Kerberos configuration, keytab files, and gssproxy.

## Risks and Edge Cases

Documentation must stay synchronized with option parsing in `cifs.upcall.c`, especially `--no-env-probe`, `--legacy-uid`, and DNS trust warnings. Incorrect request-key examples can break Kerberos mounts system-wide.

## Test Signals

Generate the manpage and compare documented options with `getopt_long` in `cifs.upcall.c`. Packaging tests should verify substituted helper paths and request-key snippets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifs.upcall.rst.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifs_spnego.h -->
# sources/user-network-fs/cifs-utils/cifs_spnego.h

## Purpose

`cifs_spnego.h` defines the userspace/kernel packet contract for CIFS SPNEGO upcalls.

## Important APIs, Types, and Functions

The key constant is `CIFS_SPNEGO_UPCALL_VERSION`, currently `2`. `struct cifs_spnego_msg` contains `version`, `flags`, `sesskey_len`, `secblob_len`, and flexible payload storage in `data[1]`, where callers concatenate session key bytes followed by the security blob.

## Control Flow

`cifs.upcall.c` fills this structure after obtaining Kerberos/GSS material and passes it to `keyctl_instantiate`. The kernel CIFS key type interprets the same layout.

## State and Persistence Behavior

The header defines an in-memory wire format stored in kernel key payloads. It has no independent state.

## Dependencies and Integration Points

It depends on fixed-width integer types from surrounding includes and conditionally declares the kernel key type under `__KERNEL__`. It is a compatibility boundary between cifs-utils and the Linux CIFS client.

## Risks and Edge Cases

Changing field order, version, or payload packing would break kernel/userspace compatibility. `data[1]` is the classic flexible-array idiom, so allocation must include both variable-length regions.

## Test Signals

Tests should validate packet size calculation, version checks, zero-length fields, and kernel acceptance of generated key payloads from `cifs.upcall`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifs_spnego.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifsacl.h -->
# sources/user-network-fs/cifs-utils/cifsacl.h

## Purpose

`cifsacl.h` defines CIFS/NTFS ACL constants, xattr names, ACE kind classification, and packed security descriptor structures used by ACL utilities.

## Important APIs, Types, and Functions

Important definitions include `ATTRNAME_ACL`, `ATTRNAME_NTSD`, `ATTRNAME_NTSD_FULL`, file/standard/generic access masks, common composite masks such as `FULL_CONTROL`, `EREAD`, and `CHANGE`, ACE flags, ACE types, comparison bitmasks, `DEFAULT_ACL_REVISION`, `ace_kinds`, `struct cifs_ntsd`, `struct cifs_ctrl_acl`, and `struct cifs_ace`.

## Control Flow

The header has no executable flow. `getcifsacl.c` reads packed descriptors through these structures and prints owner, group, DACL, and SACL fields. `setcifsacl.c` in the broader tree uses the same constants for construction and comparison.

## State and Persistence Behavior

The structures represent on-the-wire or xattr-backed little-endian data obtained from the CIFS client. Persistent state is the server-side security descriptor surfaced through CIFS xattrs; the header only describes the layout.

## Dependencies and Integration Points

It includes `cifsidmap.h` for SID layout. It integrates with Linux extended attributes `system.cifs_acl`, `system.cifs_ntsd`, and `system.cifs_ntsd_full` and with idmap plugins for SID-to-name presentation.

## Risks and Edge Cases

The structures are packed and multi-byte fields are little-endian. Callers must bounds-check every offset and ACE size before dereferencing. `DACL_VTYPES` and `SACL_VTYPES` are bitwise ORs of numeric type values rather than masks indexed by type, so callers should use them carefully.

## Test Signals

Tests should parse sample security descriptors with owner/group/DACL/SACL, unknown ACE types, maximum SID subauthorities, raw and mapped output, and endian conversions on big-endian build targets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifsacl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifscreds.c -->
# sources/user-network-fs/cifs-utils/cifscreds.c

## Purpose

`cifscreds.c` implements the `cifscreds` CLI for adding, clearing, clearing all, and updating CIFS username/password logon keys in the caller's session keyring.

## Important APIs, Types, and Functions

Important types are `struct cmdarg` and `struct command`. Major functions are `usage`, `key_search_all`, `cifscreds_add`, `cifscreds_clear`, `cifscreds_clearall`, `cifscreds_update`, `check_session_keyring`, and `main`. It uses `key_search` and `key_add` from `cifskey.c`.

## Control Flow

`main` parses global options `--username`, `--domain`, and `--timeout`, resolves a command by exact or unambiguous prefix, defaults the username from `getusername(getuid())`, checks for a session keyring, then dispatches. Host commands resolve hostnames into one or more addresses; domain mode uses the domain string directly. Add checks for existing keys before prompting via `getpass`, then adds a key per address and sets permissions. Clear unlinks matching keys. Clearall scans the session keyring for descriptions beginning with `cifs:` and unlinks them. Update finds existing matching keys and re-adds payloads with the new password.

## State and Persistence Behavior

The persistent state is the keyutils `logon` key payload in `KEY_SPEC_SESSION_KEYRING`; optional timeouts are set on add. Passwords are held transiently in process memory through `getpass` and key payload strings.

## Dependencies and Integration Points

It depends on keyutils, resolver helpers, `cifskey.h`, `mount.h` exit constants, and utility functions. `pam_cifscreds.c` shares the same key format through `cifskey.c`.

## Risks and Edge Cases

The command parser accepts prefixes and must detect ambiguity. The fixed `addrs[16]` array in update matches resolver limits but depends on `MAX_ADDRESSES` staying 16. Password memory is not explicitly scrubbed in this CLI path. Domain and username disallowed-character checks are important because key descriptions are colon-delimited.

## Test Signals

Tests should cover add/update/clear/clearall against an isolated session keyring, multi-address hosts, domain mode, invalid usernames/domains, duplicate key handling, timeout behavior, missing session keyring warnings, and ambiguous command prefixes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifscreds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifsidmap.h -->
# sources/user-network-fs/cifs-utils/cifsidmap.h

## Purpose

`cifsidmap.h` defines the binary SID and Unix-ID mapping structures and plugin ABI that CIFS idmap helpers and plugins share.

## Important APIs, Types, and Functions

The header defines `NUM_AUTHS`, `SID_MAX_SUB_AUTHORITIES`, packed `struct cifs_sid`, mapping type constants `CIFS_UXID_TYPE_UNKNOWN`, `CIFS_UXID_TYPE_UID`, `CIFS_UXID_TYPE_GID`, `CIFS_UXID_TYPE_BOTH`, packed `struct cifs_uxid`, and plugin symbols `cifs_idmap_init_plugin`, `cifs_idmap_exit_plugin`, `cifs_idmap_sid_to_str`, `cifs_idmap_str_to_sid`, `cifs_idmap_sids_to_ids`, and `cifs_idmap_ids_to_sids`.

## Control Flow

Helpers load plugin symbols dynamically and call initialization to obtain an opaque handle. Conversion calls operate on preallocated arrays, with per-element unknown/revision-zero markers for partial failures.

## State and Persistence Behavior

The structures are transient binary payloads for kernel key instantiation, ACL xattr parsing, and plugin conversion. Plugin state is opaque and owned by the plugin handle.

## Dependencies and Integration Points

It requires `uid_t`, `gid_t`, `size_t`, and fixed-width integer types from system headers. It is consumed by `cifs.idmap.c`, `idmap_plugin.c`, `idmapwb.c`, `getcifsacl.c`, and ACL utilities.

## Risks and Edge Cases

The SID subauthority array is always stored little-endian in `struct cifs_sid`, while plugins may use host-endian representations. The ABI is symbol-name based; missing functions become runtime failures. The packed layout is compatibility-sensitive.

## Test Signals

Tests should validate struct sizes/layouts, max subauthority handling, partial mapping semantics, BOTH-type behavior, and raw key payload compatibility with the kernel CIFS client.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifsidmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifskey.c -->
# sources/user-network-fs/cifs-utils/cifskey.c

## Purpose

`cifskey.c` provides the small keyutils wrapper used by `cifscreds` and `pam_cifscreds` to search, add, and update CIFS logon keys.

## Important APIs, Types, and Functions

The public functions are `key_search` and `key_add`. `key_search` builds a `cifs:<type>:<addr>` description and searches `DEST_KEYRING`. `key_add` builds the same description, formats payload `user:pass`, adds a `logon` key, and optionally sets a timeout.

## Control Flow

Callers resolve an address or domain first, then call `key_search` to detect existing credentials or `key_add` to create/replace them. Both functions validate that formatted strings fit fixed buffers.

## State and Persistence Behavior

Persistent state is stored in the caller's session keyring as keyutils `logon` keys. Payloads contain plaintext `username:password` available only through key permissions.

## Dependencies and Integration Points

It depends on keyutils, `cifskey.h`, and `resolve_host.h` for address size constants. It is shared by the CLI and PAM module.

## Risks and Edge Cases

Description and payload buffers are fixed-size and reject overlong inputs with `EINVAL`. Key permission setting is the caller's responsibility after `key_add`. Password material remains in stack buffers until overwritten naturally.

## Test Signals

Use an isolated keyring to verify search misses/hits, add with and without timeout, overlong user/password/address rejection, and permission setting by callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifskey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifskey.h -->
# sources/user-network-fs/cifs-utils/cifskey.h

## Purpose

`cifskey.h` defines the CIFS credential key format, size limits, validation character sets, destination keyring, permissions, default timeout, and key helper prototypes.

## Important APIs, Types, and Functions

Key definitions are `KEY_PREFIX`, `MAX_USERNAME_SIZE`, `MOUNT_PASSWD_SIZE`, `MAX_DOMAIN_SIZE`, `USER_DISALLOWED_CHARS`, `DOMAIN_DISALLOWED_CHARS`, `DEST_KEYRING`, `CIFS_KEY_TYPE`, `CIFS_KEY_PERMS`, `DEFAULT_KEY_TIMEOUT`, `key_search`, and `key_add`.

## Control Flow

There is no executable flow; callers include the header and use the constants to validate inputs and call the key helper functions.

## State and Persistence Behavior

The constants define session-keyring persistence and permissions for stored credential keys.

## Dependencies and Integration Points

It requires keyutils types and is used by `cifscreds.c`, `cifskey.c`, and `pam_cifscreds.c`.

## Risks and Edge Cases

The limits here are smaller than the mount helper's credential limits, so PAM/CLI stashed credentials may reject inputs that mount options can carry. Any change to `KEY_PREFIX` or description format breaks key lookup compatibility.

## Test Signals

Compile tests plus keyring integration tests should verify constants match caller behavior and key permissions remain restrictive enough for logon-key payloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifskey.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cldap_ping.c -->
# sources/user-network-fs/cifs-utils/cldap_ping.c

## Purpose

`cldap_ping.c` sends an Active Directory CLDAP ping to domain controllers to learn the client's site name, allowing `resolve_host.c` to prefer site-local DC addresses for DFS/domain mounts.

## Important APIs, Types, and Functions

Important functions are `parse_ber_size`, `read_dns_string`, `generate_cldap_query`, `extract_netlogon_section`, `netlogon_get_client_site`, and `cldap_ping`. It uses ASN.1 writer helpers, resolver `dn_expand`, UDP sockets, and CLDAP/LDAP/NetLogon constants.

## Control Flow

`cldap_ping` creates a UDP socket, builds an LDAP search request for `DnsDomain=<domain>` and `NtVer=\x06\x00\x00\x00`, sends it to port 389, receives a response, extracts the `NetLogon` octet string, and parses the `NETLOGON_SAM_LOGON_RESPONSE_EX` variable DNS-compressed strings until the client site name is reached. `CLDAP_PING_TRYNEXT` tells callers to try another DC; other negative values are fatal parse or network errors.

## State and Persistence Behavior

All state is transient: socket, ASN.1 buffer, response buffer, and caller-provided `site_name`. It does not persist data.

## Dependencies and Integration Points

It depends on libtalloc, libresolv, sockets, `data_blob.h`, `asn1.h`, and `cldap_ping.h`. `resolve_host.c` calls it while processing AD SRV records.

## Risks and Edge Cases

The BER parser is manually pointer-based and has limited bounds enforcement after each step. `generate_cldap_query` returns an `ASN1_DATA` that is not freed if socket option or send setup fails after allocation. DNS-compressed NetLogon strings depend on `dn_expand` offsets and a caller-provided `MAXCDNAME` buffer. The function assumes AD additional records contain usable IPs.

## Test Signals

Tests should use captured CLDAP responses and malformed BER/NetLogon buffers, verify `CLDAP_PING_TRYNEXT` on pause responses, cover IPv4/IPv6 socket paths, and run resolver integration against a controlled AD-like DNS/CLDAP fixture.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cldap_ping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cldap_ping.h -->
# sources/user-network-fs/cifs-utils/cldap_ping.h

## Purpose

`cldap_ping.h` declares the CLDAP ping API and error codes used by the host resolver.

## Important APIs, Types, and Functions

The header defines `CLDAP_PING_NETWORK_ERROR`, `CLDAP_PING_TRYNEXT`, `CLDAP_PING_PARSE_ERROR_LDAP`, `CLDAP_PING_PARSE_ERROR_NETLOGON`, and `cldap_ping(char *domain, sa_family_t family, void *addr, char *site_name)`.

## Control Flow

Callers pass a domain, address family, raw address pointer, and `MAXCDNAME`-sized output buffer. `CLDAP_PING_TRYNEXT` is explicitly recoverable by trying another DC; other negative errors are fatal for the current resolver attempt.

## State and Persistence Behavior

The header defines no state. `site_name` is caller-owned output.

## Dependencies and Integration Points

It requires socket address family types from system headers included by consumers. `resolve_host.c` is the direct consumer.

## Risks and Edge Cases

The API uses `void *addr` and mutable `char *domain`, so type safety is caller-enforced. The comment requiring `site_name` to be `MAXCDNAME` sized is not encoded in the type.

## Test Signals

Compile tests and resolver tests should verify error-code handling and buffer-size assumptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cldap_ping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/configure.ac -->
# sources/user-network-fs/cifs-utils/configure.ac

## Purpose

`configure.ac` is the Autoconf entry point for cifs-utils. It defines package metadata, feature toggles, install paths, dependency checks, compatibility probes, Automake conditionals, and generated configuration files.

## Important APIs, Types, and Functions

Important macros include `AC_INIT`, `AC_CONFIG_SRCDIR`, `AC_CONFIG_HEADERS`, `AC_CONFIG_FILES`, `AM_INIT_AUTOMAKE`, feature `AC_ARG_ENABLE` blocks, `AC_ARG_WITH(idmap-plugin)`, `AC_ARG_WITH(pamdir)`, `AC_ARG_VAR(ROOTSBINDIR)`, compiler/header/function checks, `AC_TEST_WBCHL`, `AC_TEST_WBC_IDMAP_BOTH`, `LIBCAP_NG_PATH`, `AC_LIBCAP`, and `AM_CONDITIONAL` definitions.

## Control Flow

Configure starts by capturing feature choices with default `"maybe"`. It verifies compiler and libc facilities, requires `setfsuid`, `talloc`, and common headers/functions, then conditionally checks Kerberos/GSSAPI/keyutils/PAM/wbclient/manpage tooling. Missing optional dependencies disable features unless the user forced `--enable-...=yes`, in which case configure errors. The final conditionals drive `Makefile.am`.

## State and Persistence Behavior

It writes `config.h`, generated Makefiles, substituted variables such as `pluginpath`, `pamdir`, `PIE_CFLAGS`, `RELRO_CFLAGS`, `KRB5_LDADD`, `GSSAPI_LDADD`, and feature macros such as `HAVE_KRB5_KEYBLOCK_KEYVALUE` and `ENABLE_SYSTEMD`.

## Dependencies and Integration Points

It integrates with local `aclocal` macros for wbclient and capabilities, docutils `rst2man`, Kerberos variants, keyutils, PAM headers, libtalloc, libresolv through Makefile link settings, and Automake conditional sections.

## Risks and Edge Cases

Default `"maybe"` behavior can hide missing optional utilities in developer builds. PIE/RELRO flags are applied without probing compiler/linker support. The `ROOTSBINDIR` empty test is unquoted. Kerberos compatibility probes must remain consistent with `cifs.upcall.c` macro branches.

## Test Signals

Run configure matrices with all optional dependencies present, absent, and forced enabled. Validate `config.h` macro choices for MIT and Heimdal Kerberos, wbclient BOTH support, libcap-ng versus libcap fallback, and manpage generation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/configure.ac -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/contrib/Makefile.am -->
# sources/user-network-fs/cifs-utils/contrib/Makefile.am

## Purpose

`contrib/Makefile.am` delegates the contrib build subtree to `request-key.d`.

## Important APIs, Types, and Functions

The only build variable is `SUBDIRS = request-key.d`.

## Control Flow

Automake recurses into `contrib/request-key.d` during build, clean, install, and dist targets as appropriate.

## State and Persistence Behavior

No direct state is created here; generated request-key snippets are handled in the child directory.

## Dependencies and Integration Points

It integrates top-level `SUBDIRS = contrib` from `Makefile.am` with request-key configuration template generation.

## Risks and Edge Cases

If new contrib subdirectories are added but not listed here, they will not participate in Automake recursion.

## Test Signals

`make distcheck` and `make -C contrib` should traverse into `request-key.d`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/contrib/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/contrib/request-key.d/Makefile.am -->
# sources/user-network-fs/cifs-utils/contrib/request-key.d/Makefile.am

## Purpose

`contrib/request-key.d/Makefile.am` generates request-key configuration snippets for CIFS idmap and SPNEGO upcalls.

## Important APIs, Types, and Functions

It defines `noinst_DATA = cifs.idmap.conf cifs.spnego.conf`, template substitution rules for both `.conf` files, and `clean-local`.

## Control Flow

Each generated `.conf` target runs `sed` to replace `@sbindir@` in the `.in` template, writes a temporary `-t` file, then atomically moves it into place. `clean-local` removes generated snippets.

## State and Persistence Behavior

The generated snippets are build artifacts and are not installed automatically by this Makefile (`noinst_DATA`).

## Dependencies and Integration Points

It depends on the `SED` Autoconf substitution and the two template files. Administrators or packages can use the generated snippets under request-key configuration.

## Risks and Edge Cases

Since snippets are `noinst`, packagers must explicitly install them if desired. Wrong `sbindir` substitution breaks request-key invocation paths.

## Test Signals

Build tests should verify generated snippets contain the configured helper path and are removed by clean targets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/contrib/request-key.d/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/contrib/request-key.d/cifs.idmap.conf.in -->
# sources/user-network-fs/cifs-utils/contrib/request-key.d/cifs.idmap.conf.in

## Purpose

`cifs.idmap.conf.in` is a one-line request-key template for invoking `cifs.idmap`.

## Important APIs, Types, and Functions

The template line is `create cifs.idmap * * @sbindir@/cifs.idmap %k`, where `%k` is the key serial passed by request-key.

## Control Flow

Build substitution replaces `@sbindir@`; request-key later matches `cifs.idmap` key creation and executes the helper.

## State and Persistence Behavior

Installed under request-key configuration, this line controls kernel key upcall behavior. It does not store mapping state itself.

## Dependencies and Integration Points

It integrates Linux keyutils request-key with `cifs.idmap`.

## Risks and Edge Cases

Incorrect helper paths prevent CIFS ACL SID/ID mapping. The snippet assumes default request-key field ordering and wildcard constraints.

## Test Signals

Install in a test request-key configuration and trigger a `cifs.idmap` key request from a CIFS ACL mount or keyutils simulation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/contrib/request-key.d/cifs.idmap.conf.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/contrib/request-key.d/cifs.spnego.conf.in -->
# sources/user-network-fs/cifs-utils/contrib/request-key.d/cifs.spnego.conf.in

## Purpose

`cifs.spnego.conf.in` is a one-line request-key template for invoking `cifs.upcall` for CIFS SPNEGO keys.

## Important APIs, Types, and Functions

The template line is `create cifs.spnego * * @sbindir@/cifs.upcall %k`.

## Control Flow

Build substitution replaces `@sbindir@`; request-key executes `cifs.upcall` with the key serial when the CIFS kernel client requests `cifs.spnego`.

## State and Persistence Behavior

The installed snippet controls key instantiation behavior but does not persist credentials itself.

## Dependencies and Integration Points

It integrates request-key, the Linux CIFS client, Kerberos/GSSAPI authentication, and `cifs.upcall`.

## Risks and Edge Cases

Wrong paths or missing `cifs.upcall` break Kerberos CIFS mounts. Administrators may also need separate `dns_resolver` configuration not represented by this one-line snippet.

## Test Signals

Trigger a Kerberos CIFS mount under a test request-key setup and confirm `cifs.upcall` is invoked with the expected key.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/contrib/request-key.d/cifs.spnego.conf.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/data_blob.c -->
# sources/user-network-fs/cifs-utils/data_blob.c

## Purpose

`data_blob.c` implements Samba-style arbitrary byte blob helpers used by ASN.1, SPNEGO, and Kerberos upcall code.

## Important APIs, Types, and Functions

It defines `data_blob_null`, `data_blob_named`, `data_blob_talloc_named`, and `data_blob_free`.

## Control Flow

`data_blob_named` returns a zeroed blob for `(NULL, 0)`, duplicates provided data with `talloc_memdup`, or allocates an uninitialized byte array with `talloc_array` when only a length is supplied. `data_blob_talloc_named` creates a blob and steals the allocation into a supplied context. `data_blob_free` talloc-frees the payload and resets pointer and length.

## State and Persistence Behavior

Blob state is heap/talloc memory owned by the caller. There is no global mutable state except the constant null blob.

## Dependencies and Integration Points

It depends on talloc through `data_blob.h` and is used by ASN.1/OID encoding, SPNEGO wrapping, and Kerberos ticket/session-key transport.

## Risks and Edge Cases

Callers must free blobs exactly once and respect that `data_blob_named` copies input data. Allocation failure returns `data == NULL` and `length == 0`, which callers must check before use. Sensitive ticket/session-key blobs should be scrubbed by callers if needed; `data_blob_free` does not zero memory first.

## Test Signals

Unit tests should cover null blobs, copied input independence, uninitialized allocation length, talloc parent stealing, and double-free-safe caller patterns.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/data_blob.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/data_blob.h -->
# sources/user-network-fs/cifs-utils/data_blob.h

## Purpose

`data_blob.h` declares the `DATA_BLOB` byte-buffer type and allocation/free helpers.

## Important APIs, Types, and Functions

The header defines `typedef struct datablob { uint8_t *data; size_t length; } DATA_BLOB`, `struct data_blob_list_item`, macro alias `ldb_val`, convenience macros `data_blob`, `data_blob_talloc`, `data_blob_dup_talloc`, function declarations, and `data_blob_null`.

## Control Flow

Callers construct blobs with the macros or named functions and release them with `data_blob_free`.

## State and Persistence Behavior

The header defines caller-owned talloc-backed memory conventions. It does not persist state.

## Dependencies and Integration Points

It depends on `talloc.h` and `stdint.h`, and it is shared by ASN.1, CLDAP, SPNEGO, and upcall code.

## Risks and Edge Cases

The macros use `__location__`, a talloc/Samba convention that must be available from included headers. The ABI comment implies signature changes may require shared-library version consideration in upstream contexts.

## Test Signals

Compile tests should verify macro expansion under the project compiler flags, and blob allocation tests should include parent contexts and duplication.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/data_blob.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/getcifsacl.c -->
# sources/user-network-fs/cifs-utils/getcifsacl.c

## Purpose

`getcifsacl.c` implements the `getcifsacl` CLI, which reads CIFS security descriptor xattrs and prints owner, group, DACL, SACL, ACE type/flags/masks, and SID or mapped name information.

## Important APIs, Types, and Functions

Important functions are `print_each_ace_mask`, `print_ace_mask`, `print_ace_flags`, `print_ace_type`, `print_sid`, `print_ace`, `parse_acl`, `parse_sid`, `parse_sec_desc`, `getcifsacl_usage`, `getcifsacl`, `recursive`, and `main`. It uses `struct cifs_ntsd`, `struct cifs_ctrl_acl`, and `struct cifs_ace`.

## Control Flow

`main` parses `-v`, `-r`, and `-R`, optionally initializes the idmap plugin for SID-to-name conversion, then processes each path directly or through `nftw`. `getcifsacl` attempts to read `system.cifs_ntsd_full` into a growing buffer; on insufficient privilege or unsupported SACL retrieval it falls back to `system.cifs_acl`. `parse_sec_desc` computes owner, group, DACL, and SACL pointers from little-endian offsets, prints descriptor metadata, validates SID/ACL ranges, and iterates ACEs.

## State and Persistence Behavior

The utility reads server-backed CIFS xattr state and emits text. Global process state includes `plugin_handle`, `plugin_loaded`, `execname`, and `raw`. It does not modify ACLs.

## Dependencies and Integration Points

It depends on Linux xattrs, `nftw`, endian helpers, `cifsacl.h`, and `idmap_plugin.h`. It integrates with CIFS mounts that expose `system.cifs_acl` or NTSD xattrs and the configured idmap plugin.

## Risks and Edge Cases

Descriptor parsing is pointer arithmetic over untrusted xattr data. The code checks several boundaries but computes some offset-derived pointers before validating the offsets are inside the buffer. Recursive mode does not propagate `getcifsacl` failures into `ret` in the same way direct mode does. Raw mode avoids plugin dependency.

## Test Signals

Tests should use fixture xattrs or mock `getxattr` data for owner/group/DACL/SACL, ERANGE growth, SACL EPERM/EIO fallback, malformed offsets and ACE sizes, raw mode, plugin mapping failure, recursive traversal, and big-endian conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/getcifsacl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/getcifsacl.rst.in -->
# sources/user-network-fs/cifs-utils/getcifsacl.rst.in

## Purpose

`getcifsacl.rst.in` is the manual-page template for displaying CIFS/NTFS ACL security descriptors.

## Important APIs, Types, and Functions

It documents `getcifsacl [-v|-r]`, the `-R` recursive option, raw mode, plugin path substitution through `@pluginpath@`, output formatting expectations, and related tools.

## Control Flow

The build substitutes the plugin path and converts RST to `getcifsacl.1`. Runtime flow described is reading a file object's security descriptor and printing ACE fields separated by `/`.

## State and Persistence Behavior

The manpage describes read-only inspection of CIFS xattr-backed descriptors and plugin-based SID mapping.

## Dependencies and Integration Points

It integrates with `mount.cifs(8)`, `setcifsacl(1)`, CIFS kernel support, and idmap plugins.

## Risks and Edge Cases

The synopsis omits `-R` even though the options section documents it and the code supports it. Documentation should also remain aligned with SACL fallback behavior and raw output.

## Test Signals

Generated manpage checks should compare documented options with `getcifsacl.c` and verify `@pluginpath@` substitution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/getcifsacl.rst.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/idmap_plugin.c -->
# sources/user-network-fs/cifs-utils/idmap_plugin.c

## Purpose

`idmap_plugin.c` is the runtime loader and dispatch wrapper for CIFS ID mapping plugins.

## Important APIs, Types, and Functions

Important symbols are global `plugin_errmsg`, static `plugin`, `resolve_symbol`, `open_plugin`, `init_plugin`, `exit_plugin`, `sid_to_str`, `str_to_sid`, `sids_to_ids`, and `ids_to_sids`.

## Control Flow

`init_plugin` opens `IDMAP_PLUGIN_PATH` with `dlopen`, resolves `cifs_idmap_init_plugin`, and calls it to obtain a plugin handle. Each conversion wrapper resolves the corresponding symbol with `dlsym` and dispatches to it, reporting `-ENOSYS` when missing. `exit_plugin` resolves and calls plugin exit if available.

## State and Persistence Behavior

The shared object handle is process-global and left open for program lifetime. The plugin-specific handle is caller-managed. Error text is exposed through global `plugin_errmsg`.

## Dependencies and Integration Points

It depends on `dlopen`/`dlsym`, Autoconf-defined `IDMAP_PLUGIN_PATH`, `cifsidmap.h`, and `idmap_plugin.h`. It is used by `cifs.idmap`, `getcifsacl`, and related ACL utilities.

## Risks and Edge Cases

Function pointer assignment through `*(void **)(&entry)` is a common dlsym workaround but compiler-sensitive. Re-resolving symbols on each call is simple but adds runtime failure points. Global `plugin_errmsg` and `plugin` are not thread-safe, although these helpers are single-process command tools.

## Test Signals

Tests should load a fake plugin, verify every symbol path, missing-symbol errors, plugin init failure, conversion failure messages, and configured path handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/idmap_plugin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/idmap_plugin.h -->
# sources/user-network-fs/cifs-utils/idmap_plugin.h

## Purpose

`idmap_plugin.h` declares the helper-facing ID mapping plugin wrapper API.

## Important APIs, Types, and Functions

It exposes `plugin_errmsg`, `init_plugin`, `exit_plugin`, `sid_to_str`, `str_to_sid`, `sids_to_ids`, and `ids_to_sids`, all operating on types from `cifsidmap.h`.

## Control Flow

Programs initialize a plugin handle once, call conversion helpers as needed, inspect `plugin_errmsg` on failure, and call `exit_plugin`.

## State and Persistence Behavior

Plugin state is opaque and handle-based. Error message state is global and not caller-owned.

## Dependencies and Integration Points

It includes `cifsidmap.h` and is consumed by idmap and ACL utilities.

## Risks and Edge Cases

The API does not carry an error buffer per handle, so concurrent or nested calls could overwrite `plugin_errmsg`. Callers must free names returned by `sid_to_str`.

## Test Signals

Compile and fake-plugin tests should verify caller ownership, missing symbol handling, and consistent error strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/idmap_plugin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/idmapwb.c -->
# sources/user-network-fs/cifs-utils/idmapwb.c

## Purpose

`idmapwb.c` implements `idmapwb.so`, a CIFS ID mapping plugin backed by Samba winbind.

## Important APIs, Types, and Functions

Important functions are `csid_to_wsid`, `wsid_to_csid`, `cifs_idmap_sid_to_str`, `cifs_idmap_str_to_sid`, `wuxid_to_cuxid`, `cifs_idmap_sids_to_ids`, `cifs_idmap_ids_to_sids`, `cifs_idmap_init_plugin`, and `cifs_idmap_exit_plugin`.

## Control Flow

Conversion from CIFS SID to winbind SID copies authority bytes and converts subauthorities from little-endian to host endian. SID-to-string uses `wbcLookupSid` and returns `DOMAIN\name`. String-to-SID accepts either raw SID strings or `DOMAIN\name`/name lookups. SID-to-ID maps arrays through `wbcSidsToUnixIds`; ID-to-SID iterates UID/GID/BOTH inputs and calls winbind UID/GID lookup functions.

## State and Persistence Behavior

The plugin stores only a pointer to the caller's error-message pointer. Persistent mapping state lives in winbind/Samba configuration and databases outside this plugin.

## Dependencies and Integration Points

It depends on libwbclient, endian conversion macros, `cifsidmap.h`, and optional `HAVE_WBC_ID_TYPE_BOTH`. It is built as `idmapwb.so` and loaded through `idmap_plugin.c`.

## Risks and Edge Cases

Winbind availability and configuration determine behavior. Partial array mapping sets unknown types or revision zero markers. The BOTH case prefers UID mapping before GID. String parsing treats names without `\` first as possible raw SID, then as default-domain names.

## Test Signals

Tests should cover SID endian round-trips, raw SID string conversion, domain-name conversion, unknown identities, BOTH behavior, partial array failures, and operation with winbind stopped or returning errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/idmapwb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/idmapwb.rst.in -->
# sources/user-network-fs/cifs-utils/idmapwb.rst.in

## Purpose

`idmapwb.rst.in` is the manual-page template for the winbind ID mapping plugin.

## Important APIs, Types, and Functions

It documents the plugin role, `@pluginpath@` symlink convention, winbind dependency, and related tools.

## Control Flow

Build substitution fills the configured plugin path, then `rst2man` generates `idmapwb.8`. Runtime flow is indirect: utilities load the plugin via the configured path.

## State and Persistence Behavior

The document describes dependency on winbind state and plugin symlink configuration.

## Dependencies and Integration Points

It integrates with `getcifsacl`, `setcifsacl`, `cifs.idmap`, Samba, `smb.conf`, and `winbindd`.

## Risks and Edge Cases

The page is concise and depends on other pages for operational details. It should keep the plugin path and winbind requirements explicit for packagers.

## Test Signals

Generated manpage checks should verify `@pluginpath@` substitution and related-tool references.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/idmapwb.rst.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/mount.cifs.c -->
# sources/user-network-fs/cifs-utils/mount.cifs.c

## Purpose

`mount.cifs.c` implements the setuid/capability-aware mount helper for CIFS and SMB3 filesystems. It validates user mounts, parses UNC paths and mount options, obtains credentials, resolves target addresses, invokes the kernel `mount(2)` call, retries selected failures, and updates mtab when appropriate.

## Important APIs, Types, and Functions

The central type is `struct parsed_mount_info`, which carries flags, host/share/prefix, options, domain, username, passwords, address list, and parsing state bits across the privilege-separated parent/child boundary. Major functions include `check_setuid`, `check_fstab`, `mount_usage`, `set_password`, `drop_capabilities`, `toggle_dac_capability`, `parse_cred_line`, `open_cred_file`, `get_password_from_file`, `parse_opt_token`, `parse_options`, `parse_unc`, `get_pw_from_env`, `uppercase_string`, `check_mtab`, `add_mtab`, `del_mtab`, `drop_child_privs`, optional `get_passwd_by_systemd`, `get_password`, `assemble_mountinfo`, `acquire_mountpoint`, and `main`.

## Control Flow

`main` validates setuid/root capability, drops to a restricted capability set, parses top-level mount options, canonicalizes the mountpoint, and forks. The child drops privileges, checks `/etc/fstab` for unprivileged users, reads environment and credential files, parses option strings, validates user mount flags, parses the UNC, resolves host addresses, defaults username, and prompts for a password when needed. The parent then iterates the comma-separated address list, assembles kernel options (`ip=`, `unc=`, parsed options, prefix path, passwords), calls `mount(orig_dev, ".", cifs_fstype, flags, options)`, retries connection errors against alternate addresses, retries uppercase share names for `ENXIO`, and can reassemble with `SUDO_UID` as `cruid` on Kerberos `ENOKEY`. It updates mtab unless `-n`, fake mount, or unusable mtab conditions apply.

## State and Persistence Behavior

Runtime state includes shared anonymous memory for parsed mount info, capability sets, fsuid/fsgid during mountpoint acquisition, password buffers, generated option strings, current working directory, and mtab lock files. Persistent effects are the kernel mount, optional `/etc/mtab` updates, and symlinked `mount.smb3` behavior through `argv[0]`.

## Dependencies and Integration Points

It depends on libc mount APIs, NSS passwd/group, libcap-ng or libcap/prctl fallbacks, systemd ask-password when enabled, keyring/Kerberos semantics through kernel CIFS options, `resolve_host`, `mtab.c`, and `util.c`. It integrates with `/etc/fstab`, environment variables `PASSWD`, `PASSWD_FD`, `PASSWD_FILE`, `PASSWD2*`, `USER`, and `SUDO_UID`.

## Risks and Edge Cases

This is security-critical. Option parsing mutates a copied option string in place and comma escaping for passwords must remain correct. Privilege separation depends on no pointers in `struct parsed_mount_info`. `set_password` checks `j > pass_length` after writes, which requires careful boundary tests. Mtab writes are legacy and must be skipped for symlinked mtab. The helper constructs a kernel option string bounded to one page; every append path must preserve the limit.

## Test Signals

Tests should cover root and unprivileged fstab mounts, credentials files, password env/file/fd inputs, Kerberos/noauth/guest password suppression, multi-address retry, uppercase retry, `SUDO_UID` cruid fallback, snapshot token conversion, mtab add/delete, fake mounts, systemd ask-password fallback, and static analysis of capability transitions and option bounds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/mount.cifs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/mount.h -->
# sources/user-network-fs/cifs-utils/mount.h

## Purpose

`mount.h` centralizes mount-helper exit status bits, mtab path helpers, and mtab function prototypes.

## Important APIs, Types, and Functions

It defines `EX_USAGE`, `EX_SYSERR`, `EX_SOFTWARE`, `EX_USER`, `EX_FILEIO`, `EX_FAIL`, `EX_SOMEOK`, `_PATH_MOUNTED_LOCK`, `_PATH_MOUNTED_TMP`, and prototypes for `mtab_unusable`, `lock_mtab`, `unlock_mtab`, and `my_endmntent`.

## Control Flow

There is no executable flow. `mount.cifs.c`, resolver code, and credential tools use the exit constants for consistent error reporting.

## State and Persistence Behavior

The mtab path macros describe filesystem lock/temp state used by `mtab.c`.

## Dependencies and Integration Points

It relies on `_PATH_MOUNTED` from system path headers included by consumers. It integrates `mount.cifs.c` with `mtab.c`.

## Risks and Edge Cases

Exit constants are bit flags, but many callers return them as discrete values. Path macros inherit platform-specific `_PATH_MOUNTED` behavior.

## Test Signals

Compile tests and mtab update tests should ensure prototypes and constants match implementations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/mount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/mtab.c -->
# sources/user-network-fs/cifs-utils/mtab.c

## Purpose

`mtab.c` implements legacy `/etc/mtab` usability checks, locking, unlocking, and safe close/fsync helpers for `mount.cifs`.

## Important APIs, Types, and Functions

Important functions are `mtab_unusable`, `unlock_mtab`, `lock_mtab`, and `my_endmntent`; internal helpers include signal handlers and `mono_time`.

## Control Flow

`mtab_unusable` rejects missing or symlinked mtab. `lock_mtab` installs signal handlers, creates a per-pid link target, attempts to atomically link it to the mtab lock path, and combines link ownership with `fcntl` locking and a 30-second timeout. `unlock_mtab` removes the lock file only if this process created it. `my_endmntent` flushes and fsyncs the mtab stream, truncating back to a known size on failure before closing.

## State and Persistence Behavior

Static state tracks whether this process created the lock, the lock fd, and whether signal handlers were installed. Persistent filesystem state includes `_PATH_MOUNTED_LOCK` and temporary link-target files.

## Dependencies and Integration Points

It depends on system mtab paths, fcntl locks, signals, monotonic time when available, and `mount.h`. `mount.cifs.c` calls it before adding or deleting mtab entries.

## Risks and Edge Cases

Signal handler installation is broad and can alter process signal behavior after mtab work. Stale lock files, read-only filesystems, symlinked mtab, and concurrent mount processes are the main edge cases. Timeout arithmetic uses seconds only for the stop condition.

## Test Signals

Tests should simulate concurrent lockers, stale locks, symlinked `/etc/mtab`, fsync failure/truncation, signal interruption, and clock_gettime fallback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/mtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/pam_cifscreds.c -->
# sources/user-network-fs/cifs-utils/pam_cifscreds.c

## Purpose

`pam_cifscreds.c` implements a PAM module that captures a user's authentication token and stores CIFS credential keys in the session keyring when a PAM session opens, with update support on password change.

## Important APIs, Types, and Functions

Important functions are `parse_args`, `free_password`, `cleanup_free_password`, `cifscreds_pam_add`, `cifscreds_pam_update`, `pam_sm_authenticate`, `pam_sm_open_session`, `pam_sm_close_session`, `pam_sm_setcred`, and `pam_sm_chauthtok`. It uses argument flags `ARG_DOMAIN` and `ARG_DEBUG`.

## Control Flow

`pam_sm_authenticate` parses module args, obtains PAM user and `PAM_AUTHTOK`, and stores a duplicated password in PAM data with a cleanup scrubber. `pam_sm_open_session` retrieves that password, requires a `host=` or `domain=` argument, checks the session keyring, and calls `cifscreds_pam_add`. Add/update paths validate host/domain and username, resolve host addresses unless domain mode is set, search for existing keys, and add or update `logon` keys using `key_add`. `pam_sm_chauthtok` updates existing credentials during `PAM_UPDATE_AUTHTOK`.

## State and Persistence Behavior

PAM data holds a duplicated password until cleanup. Credential persistence is in keyutils session keyring keys with `DEFAULT_KEY_TIMEOUT`. The password cleanup function overwrites memory before free.

## Dependencies and Integration Points

It depends on PAM headers, keyutils, resolver helpers, `cifskey.h`, `mount.h`, and `util.h`. It integrates with PAM service configuration that supplies `host=` or `domain=`, and with `pam_keyinit` for session keyrings.

## Risks and Edge Cases

`parse_args` can leave `hostdomain` unset if no host/domain is provided; callers must enforce this. `cifscreds_pam_update` counts existing keys but then loops using `currentaddress` after the scan has advanced it to NULL, so update appears unable to update the actual matched addresses. Existing-key behavior in add returns a service error rather than refreshing. PAM applications that do not preserve module data across callbacks will skip key setup.

## Test Signals

PAM integration tests should cover authenticate/open-session sequencing, host and domain modes, missing host/domain, duplicate keys, password cleanup, missing session keyring, password-change update behavior, and the suspected update-address bug.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/pam_cifscreds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/resolve_host.c -->
# sources/user-network-fs/cifs-utils/resolve_host.c

## Purpose

`resolve_host.c` resolves a hostname to a comma-separated bounded list of IPv4/IPv6 address strings for mount and credential helpers. For AD/DFS-like domains with multiple DC addresses, it can use DNS SRV records plus CLDAP ping to prioritize domain controllers in the client's site.

## Important APIs, Types, and Functions

The public function is `resolve_host(const char *host, char *addrstr)`. It uses `getaddrinfo`, `inet_ntop`, resolver APIs `res_init`, `res_query`, `ns_initparse`, `ns_parserr`, `ns_msg_count`, DNS record types `A`, `AAAA`, and `SRV`, and `cldap_ping`.

## Control Flow

The function first calls `getaddrinfo`, filters TCP IPv4/IPv6 results, limits them to `MAX_ADDRESSES`, and appends printable addresses to `addrstr`. If more than one IPv4 or IPv6 address exists, it queries `_ldap._tcp.dc._msdcs.<host>` for global DC SRV data. With multiple DCs, it pings additional A/AAAA addresses to learn `site_name`, queries `_ldap._tcp.<site>._sites.dc._msdcs.<host>`, rebuilds `addrstr` with site-local addresses first, then appends non-duplicate global addresses up to the limit.

## State and Persistence Behavior

The function is stateless apart from resolver library state initialized by `res_init`. Output is caller-owned `addrstr`. No disk state is written.

## Dependencies and Integration Points

It depends on libc name resolution, libresolv, `mount.h` exit codes, `util.h`, `cldap_ping.h`, and `resolve_host.h`. It is used by `mount.cifs`, `cifscreds`, and `pam_cifscreds`.

## Risks and Edge Cases

The initial comma insertion checks `addr == addrlist`, but skipped leading `addrinfo` entries can leave `addrstr` uninitialized when the first usable address is not the first list node. Duplicate detection uses substring search with separator checks. DNS/CLDAP errors in the optimization path mostly fall through to returning the original address list, but `rc` must remain meaningful. Buffer sizing uses `MAX_ADDR_LIST_LEN`, which must account for IPv6 scope ids and commas.

## Test Signals

Tests should cover IPv4, IPv6 with scope id, non-TCP addrinfo entries before usable entries, more than `MAX_ADDRESSES`, DNS failures, AD site-local prioritization with mocked resolver/CLDAP data, duplicate suppression, and callers' handling of `EX_USAGE` versus `EX_SYSERR`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/resolve_host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/resolve_host.h -->
# sources/user-network-fs/cifs-utils/resolve_host.h

## Purpose

`resolve_host.h` declares the shared host resolver API and address-list size constants.

## Important APIs, Types, and Functions

It defines `MAX_ADDRESS_LEN` as `INET6_ADDRSTRLEN`, `MAX_ADDRESSES` as 16, `MAX_ADDR_LIST_LEN` as `(MAX_ADDRESS_LEN + 1) * MAX_ADDRESSES`, and declares `resolve_host`.

## Control Flow

Callers allocate a buffer of `MAX_ADDR_LIST_LEN`, call `resolve_host`, and receive a comma-separated list of address strings or an error code compatible with `mount.h`.

## State and Persistence Behavior

No state is defined. The caller owns the output buffer.

## Dependencies and Integration Points

It includes `<arpa/inet.h>` for address string sizes and is consumed by mount, credential, PAM, and key helpers.

## Risks and Edge Cases

`MAX_ADDRESS_LEN` does not include IPv6 scope-id suffix text, though `resolve_host.c` may append `%<scopeid>` into a larger temporary buffer before copying into the aggregate list. `MAX_ADDR_LIST_LEN` assumes one separator per address and no final NUL margin beyond the expression's arithmetic, so caller buffers should use exactly the macro.

## Test Signals

Compile tests and resolver integration tests should validate buffer sizing for IPv4, IPv6, scoped IPv6, and maximum address counts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/resolve_host.h -->
