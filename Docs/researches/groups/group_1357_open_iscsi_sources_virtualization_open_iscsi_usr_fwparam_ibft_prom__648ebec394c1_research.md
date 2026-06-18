# Group Research: group_1357_open_iscsi_sources_virtualization_open_iscsi_usr_fwparam_ibft_prom__648ebec394c1

Scope confirmed against `Docs/research_subset_a.md`: `sources/virtualization/open-iscsi` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_lex.c -->
# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_lex.c

Generated Flex scanner for Open Firmware / OBP iSCSI boot-path parsing. It is generated from `prom_lex.l` using Flex 2.5.35 and includes the full scanner runtime: buffer management, `yy_scan_*` helpers, restart/switch APIs, global scanner state, token text storage, and allocation wrappers.

Project-specific behavior is embedded from `prom_lex.l`. It includes `prom_parse.h`, fills `yylval.str` with the matched token text through `upval(d)`, updates `yylloc` columns, and returns parser tokens for Open Firmware path components.

Recognized token classes include boot property names (`bootpath`, `bootargs`, `iscsi-bootargs`, `nas-bootdevice`), virtual device components (`vdevice`, `gscsi`, `dev`, `rawio`), bus names, boot devices, IPv4 addresses, IQNs, OBP qualifiers, OBP parameters, short and long hex strings, and escaped filenames. Whitespace is consumed while preserving column progress. Any unmatched single character is returned literally, which lets the Bison grammar consume delimiters such as `/`, `@`, `,`, `:`, and `=`.

Important implementation detail: scanner output uses `%option array`, so `yytext` is a fixed array with `YYLMAX` defaulting to 8192. Token transfer uses `strcat(yylval.str, yytext)` after clearing the destination first. The parser union buffer is larger (`STR_LEN` 16384), so scanner token size is the tighter bound.

This file should normally be regenerated from `prom_lex.l`, not edited directly. Behavioral changes belong in the `.l` source.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_lex.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_lex.l -->
# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_lex.l

Hand-authored Flex lexer for parsing Open Firmware boot paths and OBP iSCSI boot arguments. It feeds tokens and string values to the Bison parser declared through `prom_parse.h`.

The lexer defines token regexes for Open Firmware device paths: bus names (`ata`, `pci`, `scsi`, `usb`, and others), boot devices (`disk`, `cdrom`, `ethernet`, `iscsi-diskN`, `iscsi-toe`, `sd`), CHOSEN boot properties, OBP qualifiers (`bootp`, `ipv6`, `iscsi`, `dhcpv6`), OBP parameters such as CHAP fields and target identifiers, IPv4 literals, IQNs, hex chunks, and escaped filenames.

The `upval(d)` macro is the central action: it copies matched text into `yylval.str`, updates parser location columns, and returns the token kind. Whitespace is skipped with location updates. All other single characters are returned as literal grammar tokens.

The lexer is non-interactive, has no `yywrap`, disables `input` and `unput`, and uses array-backed `yytext`. It is tightly coupled to `prom_parse.y` token names and to `YYSTYPE.str`.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_lex.l -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_parse.h -->
# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_parse.h

Shared parser/lexer interface header for the firmware parameter parser. It includes standard allocation/string headers and `iscsi_obp.h`, forward-declares `struct ofw_dev`, and exposes `yyerror`, `yylex`, `yyin`, `yytext`, `yyleng`, and `yydebug`.

The header includes the generated Bison interface `prom_parse.tab.h`, which defines token numbers, semantic value storage, location type, and `yyparse(struct ofw_dev *ofwdev)`.

`YY_NO_UNPUT` is defined to match the Flex scanner configuration. This keeps the generated scanner/parser interface consistent and avoids expecting Flex `unput` support.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_parse.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_parse.tab.c -->
# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_parse.tab.c

Generated GNU Bison 3.0.4 LALR parser implementation for `prom_parse.y`. Most of the file is standard Bison skeleton code: token translation tables, parse stacks, debug printing, error handling, memory growth, location tracking, and the `yyparse(struct ofw_dev *ofwdev)` driver.

The embedded project grammar parses Open Firmware paths and iSCSI OBP parameters into an `ofw_dev`. It recognizes root-only paths, physical bus paths with boot devices, disk labels, OBP qualifiers and parameters, and a virtual-device form. It constructs intermediate strings in fixed-size `STR_LEN` semantic buffers.

Semantic actions set `ofwdev->dev_path` for bus + boot-device paths, deliberately excluding disk labels and OBP parameter suffixes from the stored device path. OBP parameters are handed to helper functions from `iscsi_obp.h`: `obp_parm_hexnum`, `obp_parm_addr`, `obp_parm_iqn`, `obp_parm_str`, and `obp_qual_set`.

The grammar handles IPv4, IPv6-style hex sequences including `::`, optional IPv4 tails, disk partitions, and escaped filenames. It also has debug-only `DPRINT` tracing controlled by `YYDEBUG`.

Operational risks are inherited from the grammar actions: `ofwdev->dev_path` allocations are not checked for `NULL`, and repeated successful parses into the same `ofw_dev` would need ownership discipline outside this file. Direct edits should be avoided; changes belong in `prom_parse.y`.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_parse.tab.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_parse.tab.h -->
# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_parse.tab.h

Generated Bison parser interface for the firmware parser. It declares token enum values for lexer/parser coordination: bus names, boot devices, IPv4, IQN, OBP parameter/qualifier names, hex tokens, virtual-device tokens, CHOSEN tokens, and filenames.

The semantic value union contains `char str[STR_LEN]` with `STR_LEN` defined as 16384 from the grammar. All grammar tokens and nonterminals carry string data through this buffer.

The header also defines `YYLTYPE` with first/last line and column fields, declares global `yylval` and `yylloc`, and exposes `yyparse(struct ofw_dev *ofwdev)`.

This file is generated from `prom_parse.y` and should be regenerated rather than manually changed.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_parse.tab.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_parse.y -->
# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_parse.y

Hand-authored Bison grammar for Open Firmware / OBP boot paths. It includes `prom_parse.h` and `iscsi_obp.h`, defines `YYSTYPE` as a large string buffer, enables locations, and passes `struct ofw_dev *ofwdev` into parse actions.

Top-level `devpath` alternatives cover `/`, physical bus chains plus boot device, optional disk labels, optional OBP qualifiers and parameters, and a virtual-device path form. For physical boot-device paths, actions allocate and store `ofwdev->dev_path` as `/<busses><bootdev>`, omitting disk labels and parameter suffixes.

The grammar builds path component strings for buses, boot devices, virtual-device parameters, OBP qualifier lists, OBP parameter lists, IPv4/IPv6 addresses, hex sequences, disk labels, and disk partitions.

OBP parameter actions have side effects on `ofwdev`: numeric/hex parameters call `obp_parm_hexnum`, IP parameters call `obp_parm_addr`, IQNs call `obp_parm_iqn`, filenames call `obp_parm_str`, and qualifiers call `obp_qual_set`.

Notable constraints: semantic buffers are fixed at 16384 bytes; most concatenations use `snprintf`, but some copies use `strcpy` where the lexer’s token length bounds are assumed to keep data safe. `malloc` results for `dev_path` are not checked.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_parse.y -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/host.c -->
# File Research: sources/virtualization/open-iscsi/usr/host.c

iSCSI host display and CHAP netlink configuration helper implementation.

The host-info path matches kernel iSCSI hosts to active sessions by mapping session SID to host number through sysfs, then prints host information in flat or tree forms. It formats transport, initiator name, IP address, hardware address, netdev, host state, per-host iface records, and optional session trees. IPv6 addresses are bracketed in output.

`host_info_print()` supports info levels 0 through 4. Level 0 / -1 prints flat host rows. Higher levels print tree output and progressively include session state, iface information, iSCSI parameters, SCSI devices, and kernel/userspace version information. It probes offload transports before tree enumeration.

The CHAP path builds netlink attributes for host CHAP records. `chap_fill_param_uint()` writes fixed-width integer values into `iscsi_param_info` attributes, supporting 1-, 2-, and 4-byte values. `chap_fill_param_str()` writes string attributes. `chap_build_config()` starts at iovec index 2 to leave room for netlink header and event slots, then appends index, CHAP type, username, password, and password length attributes.

Error handling returns open-iscsi error codes for invalid info levels, empty host lists, allocation failures, and sysfs enumeration failures. The CHAP helper returns a count of successfully built iovecs and silently skips fields that fail allocation.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/host.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/host.h -->
# File Research: sources/virtualization/open-iscsi/usr/host.h

Public header for iSCSI host helpers. It includes libopeniscsiusr, local type/config definitions, and declares the host information and CHAP configuration APIs.

It defines host-related constants: `MAX_HOST_NO`, CHAP table size limit, CHAP buffer size, and request buffer size including `struct iscsi_uevent`.

`struct host_info` combines an `iface_rec` with a `host_no`. Exported functions are `host_info_print()` for CLI-style host/session output and `chap_build_config()` for turning an `iscsi_chap_rec` into netlink iovecs.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/host.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/idbm.c -->
# File Research: sources/virtualization/open-iscsi/usr/idbm.c

Core iSCSI discovery database manager. It owns conversion between in-memory records and the on-disk open-iscsi database under node, discovery, static, firmware, and iSNS directories.

The first major layer builds `recinfo_t` arrays for discovery records, node records, iface records, host CHAP records, and flashnode records. Macros populate typed fields, current string values, backing data pointers, visibility, valid options, and mutability. Sensitive password values are marked masked for printing. CHAP algorithm lists support MD5, SHA1, SHA256, and conditionally SHA3-256.

Printing uses `idbm_print()` to emit `ISCSI_BEGIN_REC` / `ISCSI_END_REC` records, optionally masking passwords. Config parsing in `idbm_recinfo_config()` reads `name = value` lines, strips comments/blank lines, warns about malformed or overlong lines, and updates recinfo-backed structures through `idbm_rec_update_param()`.

Parameter update logic supports integer, uint8/16/32, string, enumerated integer options, and integer-list options. It also auto-updates password length fields when password fields change. `idbm_verify_param()` blocks modification of identity fields used to locate records.

Default setup covers discovery defaults, session operational defaults, connection operational defaults, and full node defaults. Defaults include startup policy, login/reopen timers, command limits, queue depth, CHAP defaults, digest settings, connection timeouts, and iface defaults. `idbm_sync_config()` overlays defaults from the global config file when available.

Persistence supports old and new database layouts. Node records may be stored as old-style portal files or new-style target/portal/tpgt/iface paths. Write paths create missing directories, convert old portal files into directories when needed, and preserve backward compatibility. Discovery records are stored under sendtargets or iSNS roots and also support old file-vs-directory formats.

Iteration helpers traverse discovery records, target nodes, portals, and iface-bound records. They expose callback-based enumeration for printing, updating, and matching. Discovery printing groups sendtargets, iSNS, static, and firmware records, with compatibility logic for older iSNS layouts.

Locking uses a global `db` object with recursive reference counting and a hard-link based write lock under `LOCK_DIR`. It retries for up to `DB_LOCK_RETRIES` with `DB_LOCK_USECS_WAIT` sleeps, then removes `LOCK_WRITE_FILE` on unlock.

Discovery-to-node relationships are represented by symlinks. `setup_disc_to_node_link()` computes link paths for sendtargets, firmware, static, and iSNS records, including old iSNS compatibility. Add/delete paths create or remove these links while writing/removing node records.

`idbm_add_node()` optionally overwrites existing records, applies discovery metadata, marks firmware-discovered nodes as onboot, writes the node, and creates discovery links when TPGT is known. `idbm_delete_node()` removes discovery links, node config files, empty portal directories, and empty target directories. `idbm_delete_discovery()` removes discovery config and associated node links.

The file also provides user parameter allocation/free helpers, node/discovery parameter setters, default-copy helpers for sendtargets and iSNS, session autoscan lookup, database init/terminate, record creation from explicit parameters, record creation from firmware boot context, and list search by session identity.

Notable risks: path construction relies heavily on fixed `PATH_MAX` buffers and formatted strings; many paths assume global `db` has been initialized; some compatibility branches can continue after partial cleanup failures; and record file parsing is permissive, warning and continuing on malformed lines.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/idbm.c -->