# Group Research: group_1377_openbsd_src_sources_os_bsd_openbsd_src_sbin_pdisk_partition_map_c_s_25849e24d037

Scope verified against `Docs/research_subset_a.md`: `sources/os/bsd/openbsd-src` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pdisk/partition_map.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/pdisk/partition_map.c

Implements Apple Partition Map loading, validation, creation, mutation, and writing for `pdisk`.

Key responsibilities:
- Opens an existing partition map from block zero plus DPME entries.
- Validates block-zero signature, sector size, media size, partition-entry count, DPME signatures, and logical-block ranges.
- Maintains two linked-list orderings of entries: `disk_order` by partition-map entry number and `base_order` by physical block start.
- Creates a default map with block zero, an initial `Apple_Free` span, and an `Apple_partition_map` entry.
- Adds partitions by splitting an enclosing `Apple_Free` entry into before/target/after pieces.
- Deletes partitions by converting them back into free space and coalescing adjacent `Apple_Free` entries.
- Renumbers disk addresses and updates each entry’s `dpme_map_entries`.
- Resizes the partition map entry when adjacent free space and map-capacity constraints allow.
- Writes block zero and each DPME entry back to disk.
- Detects and optionally removes driver descriptor references from block zero when deleting a containing partition.

Important functions and data:
- `open_partition_map()` allocates and initializes a map, reads block zero, validates it, reads DPME entries, or prompts to create a default map.
- `read_partition_map()` reads every declared DPME entry and checks count consistency, logical ranges, overlap, disk-end extension, and unmapped physical-block gaps.
- `create_partition_map()` constructs a new in-memory Apple partition map.
- `add_partition_to_map()` splits free space and inserts the requested partition.
- `delete_partition_from_map()`, `delete_entry()`, and `combine_entry()` remove entries and merge free space.
- `create_entry()` initializes DPME fields, names, types, logical size, flags, and list membership.
- `dpme_init_flags()` assigns special flags for free, map, HFS, and general data partitions.
- `move_entry_in_map()` swaps two map positions except partition 1.
- `resize_map()` shrinks or expands the map entry around adjacent free space.
- `contains_driver()` and `remove_driver()` consult and update the block-zero driver descriptor map.

Notable behavior:
- Media size is capped to `UINT32_MAX` in `open_partition_map()`, matching 32-bit Apple partition-map fields.
- The partition-map entry itself and free-space entries cannot be deleted through normal deletion.
- New OpenBSD/data partitions get valid, allocated, readable, and writable flags; `Apple_HFS` receives the legacy HFS flag value.
- Free entries have no logical blocks, while non-free entries default logical blocks to the full physical partition size.
- `add_partition_to_map()` rejects allocations outside an existing free partition and rejects changes that would exceed map capacity.
- `resize_map()` temporarily clears the map entry type before routing through deletion logic, then recreates the map entry at block 1.

Dependencies:
- Uses structures and constants from `partition_map.h`.
- Uses disk I/O helpers from `io.h`.
- Uses `read_block0`, `read_dpme`, `write_block0`, and `write_dpme`.
- Uses OpenBSD `sys/queue.h` list macros and standard allocation/diagnostic helpers.

Research notes:
- This file is the stateful partition-map engine behind `pdisk.c`.
- The dual-order list model is central: disk order controls DPME write positions, while base order controls allocation, overlap checks, and free-space coalescing.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pdisk/partition_map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pdisk/partition_map.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/pdisk/partition_map.h

Declares the Apple Partition Map data model and public partition-map API for `pdisk`.

Key contents:
- Defines Apple block-zero and DPME signatures:
  - `BLOCK0_SIGNATURE` as `0x4552` (`ER`)
  - `DPME_SIGNATURE` as `0x504D` (`PM`)
- Defines `DPISTRLEN` as the 32-byte Apple partition name/type string length.
- Defines `struct ddmap`, the block-zero driver descriptor entry.
- Defines `struct partition_map`, including:
  - disk-order and base-order entry lists
  - device name and file descriptor
  - changed flag
  - map capacity/count fields
  - media size
  - block-zero fields and driver descriptor array
- Defines `struct entry`, including:
  - list links for both orderings
  - parent map and disk address
  - DPME on-disk fields
  - NUL-extended partition name/type strings
  - partition flags, boot fields, checksum, processor ID, and reserved data
- Defines DPME flag bits such as valid, allocated, in-use, bootable, readable, writable, and OS-specific flags.

Exported symbols:
- Partition type strings: `kFreeType`, `kMapType`, `kUnixType`, and `kHFSType`.
- Global mode flags from `pdisk.c`: `lflag` and `rflag`.
- Map creation/loading: `create_partition_map()`, `open_partition_map()`.
- Entry lookup: `find_entry_by_disk_address()`, `find_entry_by_type()`, `find_entry_by_base()`.
- Mutation: `add_partition_to_map()`, `delete_partition_from_map()`, `move_entry_in_map()`, `resize_map()`.
- I/O/lifecycle: `write_partition_map()`, `free_partition_map()`.
- Helpers: `contains_driver()`, `dpme_init_flags()`.

Dependencies:
- Requires `sys/queue.h`-style `LIST_HEAD` and `LIST_ENTRY`.
- Uses fixed-width integer types.

Research notes:
- This header mirrors Apple Partition Map on-disk layout closely, including fixed reserved-field sizes.
- It is the boundary between the interactive editor, dump code, I/O code, and partition-map mutation engine.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pdisk/partition_map.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pdisk/pdisk.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/pdisk/pdisk.c

Implements the `pdisk` command-line entry point and interactive editor for Apple Partition Maps.

Key responsibilities:
- Parses `-l` list-only and `-r` read-only options.
- Opens the target disk as a character device using `opendev`.
- Verifies the device is a character device.
- Reads the OpenBSD disklabel and requires 512-byte sectors.
- Pledges to `stdio` after device setup.
- Opens an Apple partition map and either dumps it or enters interactive editing.
- Implements the interactive command loop and command dispatch.
- Prompts for partition base/length/name/type and map-editing parameters.
- Calls partition-map engine functions for create, delete, reorder, resize, rename, type change, display, and write.

Important functions:
- `main()` handles argument parsing, disk open/validation, disklabel checks, pledge, map loading, list/edit mode, cleanup, and exit.
- `edit()` prints command help and dispatches all interactive commands.
- `do_create_partition()` creates either a typed partition or the default OpenBSD partition type.
- `get_base_argument()` accepts a block number or `<n>p` partition-base modifier.
- `get_size_argument()` accepts a block count, byte multiplier, or `<n>p` partition-length modifier.
- `do_rename_partition()` and `do_change_type()` update DPME name/type fields and mark the map changed.
- `do_delete_partition()`, `do_reorder()`, `do_change_map_size()`, and `do_write_partition_map()` wrap corresponding map operations.
- `do_display_entry()` prints block zero or a full partition entry.
- `do_dump_map()` selects normal or verbose/internal dump output.
- `usage()` prints `usage: pdisk [-lr] disk`.

Interactive commands:
- `?` verbose help
- `h` command help
- `p` print partition map
- `P` show internal data structures
- `f` full display of one entry
- `i` reinitialize map
- `c` create an OpenBSD partition
- `C` create a partition with a specified type
- `d` delete
- `n` rename
- `t` change type
- `r` reorder entries
- `s` resize map
- `w` write
- `q` quit, prompting before discarding changes

Notable behavior:
- `-l` and `-r` both open the disk read-only; only `-l` automatically dumps instead of editing.
- Writes are blocked when `rflag` is set.
- Creating a partition with type `Apple_Free` or `Apple_partition_map` is rejected.
- Renaming clears the whole fixed-size DPME name buffer before copying the new string.
- Changing type clears with `memset` then copies the new type string and marks the map changed.
- Reinitialization creates a fresh default map only after user confirmation.

Dependencies:
- Uses `partition_map.h` for map operations and constants.
- Uses `io.h` for interactive input helpers.
- Uses `dump.h` for map and entry display.
- Uses OpenBSD disklabel, disk ioctl, device open, pledge, and `libutil` helpers.

Research notes:
- This file contains little partition logic itself; it is the user-interface shell over `partition_map.c`.
- Safety checks are mostly interactive confirmations and read-only/write-state gates, while structural map validation lives in `partition_map.c`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pdisk/pdisk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/Makefile -->
# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/Makefile

Builds the OpenBSD `pfctl` packet-filter control utility.

Key contents:
- Sets `PROG=pfctl`.
- Builds from:
  - `pfctl.c`
  - `parse.y`
  - `pfctl_parser.c`
  - `pf_print_state.c`
  - `pfctl_osfp.c`
  - `pfctl_radix.c`
  - `pfctl_table.c`
  - `pfctl_optimize.c`
  - `pf_ruleset.c`
  - `pfctl_queue.c`
- Enables `-Wall`, `-Wmissing-prototypes`, `-Wstrict-prototypes`, and includes the current directory.
- Leaves `YFLAGS` empty for yacc processing of `parse.y`.
- Installs `pfctl.8`.
- Adds `.PATH` to `../../sys/net` for ruleset and anchor handling sources.
- Links against `libm`.
- Includes OpenBSD `bsd.prog.mk`.

Research notes:
- `pf_ruleset.c` is pulled from the kernel network source path rather than the local `sbin/pfctl` directory.
- The parser, optimizer, table handling, queue handling, state printer, and main control program are built into one utility.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/parse.y -->
# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/parse.y

This is the yacc grammar, lexer, macro processor, and semantic rule-expansion core for `pfctl` configuration files.

Key responsibilities:
- Parses `pf.conf` syntax into PF rules, anchors, tables, queues, options, state/source limiters, antispoof rules, and deferred anchor loads.
- Implements the scanner for keywords, strings, quoted strings, comments, numbers, operators, macros, and include files.
- Tracks parser file stack, line numbers, unget buffers, EOF behavior, and nested includes.
- Supports macro assignment and expansion with command-line persistent macros.
- Converts parsed rule syntax into `struct pf_rule`, queue specs, table definitions, limiter definitions, and PF option calls.
- Expands list syntax into cross-product rule combinations across interfaces, protocols, hosts, ports, users, groups, OS fingerprints, and ICMP types.
- Validates rule consistency before inserting expanded rules.
- Handles inline brace anchors by temporarily parsing into generated internal anchors and moving rules/tables to the final anchor path.
- Defers `load anchor ... from ...` statements for later loading.
- Parses and applies NAT, rdr, binat, af-to, route-to, reply-to, dup-to, divert, scrub, tag, label, queue, probability, TOS, prio, delay, and state options.

Major grammar areas:
- Top-level `ruleset` accepts includes, options, state/source limiters, filter rules, anchor rules, load rules, queue specs, variable assignments, antispoof rules, table definitions, and inline anchors.
- `option` handles `set` directives: reassembly, optimization, ruleset optimization, timeouts, limits, loginterface, hostid, block-policy, fingerprints, state-policy, debug, skip, state-defaults, and syncookies.
- `anchorrule`, `pfa_anchor`, and `loadrule` handle named anchors, inline anchors, and deferred anchor-file loads.
- `tabledef` and `table_opts` parse table flags, inline addresses, and file-backed table initialization.
- `queuespec`, `queue_opts`, `scspec`, and `bandwidth` parse HFSC/FQ-style queue definitions.
- `statelim` and `sourcelim` define named/id-based limiters with limits, rates, table thresholds, entries, and address masks.
- `pfrule` builds pass/block/match rules and applies state defaults, TCP flag defaults, state tracking, adaptive timeouts, routing, and divert handling.
- `filter_opts` collects user/group, flags, ICMP, priority, TOS, state, fragment, label, queue, tags, probability, limiters, rtable, divert, scrub, NAT/rdr/binat/af-to, route handling, received-on, once, and max-packet-rate options.
- `host`, `dynaddr`, `portspec`, `uids`, `gids`, `flags`, `icmpspec`, and `tos` parse address and match primitives.

Important semantic functions:
- `parse_config()` initializes parser globals, pushes the main config file, runs `yyparse()`, pops files, frees macros, and reports success/failure.
- `pfctl_cmdline_symset()`, `symset()`, and `symget()` implement macro storage, persistent command-line definitions, and usage tracking.
- `pushfile()` and `popfile()` manage the include stack.
- `check_file_secrecy()` verifies ownership and permissions for secret files when requested.
- `yylex()`, `lgetc()`, `igetc()`, `lungetc()`, and `findeol()` implement lexical scanning, macro-expansion pushback, continuation lines, comments, quoted strings, and error recovery.
- `lookup()` maps reserved words to yacc tokens through a sorted keyword table.
- `process_tabledef()` loads table addresses from files/hosts, defines tables, and postpones non-root table materialization for anchor path resolution.
- `expand_queue()` converts parsed queue options into `pf_queuespec` entries.
- `filteropts_to_rule()` copies parsed filter options into a `struct pf_rule` and enforces option-specific constraints.
- `expand_rule()` performs the main cross-product expansion and calls `pfctl_add_rule()`.
- `collapse_redirspec()` turns translation/routing address pools into a rule pool or generated table.
- `apply_redirspec()` applies proxy ports, pool type, source-hash keys, sticky-address, and static-port behavior.
- `rule_consistent()` enforces protocol/action/address-family constraints.
- `expand_divertspec()` validates and applies divert options.
- `expand_label*()` expands `$if`, `$srcaddr`, `$dstaddr`, `$srcport`, `$dstport`, `$proto`, and later `$nr`.
- `mv_rules()` and `mv_tables()` move inline-anchor rules and tables from temporary anchors to final anchors.
- `lookup_rtable()` verifies route table IDs via `sysctl`.
- `parseport()`, `getservice()`, `parseicmpspec()`, `map_tos()`, and `atoul()` parse service names, numeric ports, ICMP codes, TOS/DSCP names, and numeric strings.

Notable behavior:
- Pass rules default to `keep state` unless explicitly changed.
- Stateful TCP rules default to `flags S/SA` unless flags are specified or the rule is fragment-only.
- `modulate state` and `synproxy state` degrade to normal state for non-TCP protocol expansions.
- `route-to`, `reply-to`, and `dup-to` require state and, except `dup-to`, require an explicit direction.
- `nat-to` and `rdr-to` require state except on match rules, and also require a direction.
- `af-to` is only accepted on inbound rules and cannot be combined with route handling.
- `binat-to` expands into outbound NAT plus a generated inbound rdr rule.
- Tables and multi-address dynamic interfaces are disallowed for pool types that cannot support them.
- Multiple translation/routing addresses may be converted into optimizer-generated tables.
- Dynamic interface addresses support modifiers such as `:network`, `:broadcast`, `:peer`, and `:0`; incompatible modifier combinations are rejected.
- `@if` host syntax is explicitly rejected in ordinary `from`/`to` and translation/routing contexts.
- ICMP type/code rules require an address family and must match ICMP/ICMPv6 protocol selection.
- `allow-opts` is pass-only; keep state is pass-only; routing is unsupported on block/match where invalid.
- IPv6 rejects scrub options that only apply to IPv4, such as `no-df` and `random-id`.
- State limiter and source limiter references are pass-only.
- Source tracking options reject incompatible global/rule-scoped combinations.
- Labels and tags can interpolate rule attributes before insertion, while `$nr` is expanded after optimization.
- Includes and macros are integrated at lexer level, so grammar productions see expanded token streams.

Dependencies:
- Uses `pfctl_parser.h` and `pfctl.h`.
- Consumes many PF kernel ABI structures and constants from `net/pfvar.h`.
- Calls PF control helpers such as `pfctl_set_*`, `pfctl_add_rule`, `pfctl_define_table`, `pfctl_add_queue`, `pfctl_rules`, limiter helpers, table helpers, and optimizer/table support.
- Uses libc resolver/user/group/service APIs, `sysctl`, MD5, random key generation, and OpenBSD queue/tree macros.

Research notes:
- This file is the main semantic bridge between human `pf.conf` syntax and the internal PF ruleset representation.
- Changes here affect both accepted syntax and the exact rule expansion sent to the kernel, especially around anchors, tables, NAT/rdr/af-to, and state defaults.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/parse.y -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/pf_print_state.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/pf_print_state.c

Formats PF state-table entries and address objects for `pfctl` output.

Key responsibilities:
- Prints `pf_addr_wrap` values in rule/state syntax.
- Prints raw IPv4/IPv6 addresses and optional DNS names.
- Prints host/port pairs with optional rdomain, DNS lookup, and service-name lookup.
- Prints TCP sequence windows and sequence-difference information.
- Prints one `struct pfsync_state` in compact or verbose form.
- Converts netmasks into prefix lengths.

Important functions:
- `print_addr()` handles dynamic interface addresses, tables, ranges, address/mask pairs, `no-route`, `urpf-failed`, and route labels.
- `print_addr_str()` prints numeric IPv4/IPv6 addresses with `inet_ntop`.
- `print_name()` performs reverse lookup via `getnameinfo`.
- `print_host()` prints an address plus optional port, including rdomain and service-name formatting.
- `print_seq()` prints TCP state peer sequence low/high/diff fields.
- `print_state()` formats a full PF state, including interface, protocol, translated and original endpoints, routing address, direction arrow, protocol state names, counters, timers, rule/anchor IDs, flags, and state ID.
- `unmask()` calculates the prefix length from a `struct pf_addr` mask.

Notable behavior:
- Dynamic interface output includes modifiers such as `:network`, `:broadcast`, `:peer`, and `:0`, and verbose mode includes dynamic address/table counters.
- A zero address and zero mask prints as `any`.
- Table addresses print as `<name>` or `<name:count>` in verbose mode.
- For inbound versus outbound states, `print_state()` swaps source/destination peers and wire/stack keys to present traffic direction coherently.
- ICMP and ICMPv6 state printing copies relevant key ports because ICMP identifiers/types are represented through port fields.
- NAT or address-family translation is shown by printing translated endpoints with original endpoints in parentheses.
- Verbose TCP output includes sequence windows and window scaling.
- Verbose state output includes age, expiry, packet/byte counters, anchor/rule IDs, sloppy/pflow flags, source-track, and sticky-address markers.
- Extra-verbose output includes state ID and creator ID.
- Packet and byte counters are copied out and decoded as big-endian 64-bit values.

Dependencies:
- Uses PF and pfsync structures from `net/pfvar.h`.
- Uses TCP state names from `netinet/tcp_fsm.h`.
- Uses address formatting helpers and options from `pfctl_parser.h` and `pfctl.h`.
- Uses resolver APIs for protocol, service, and host-name display.

Research notes:
- This is a presentation-only module, but it depends closely on PF state-key semantics, NAT key layout, and byte-order conventions.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/pf_print_state.c -->