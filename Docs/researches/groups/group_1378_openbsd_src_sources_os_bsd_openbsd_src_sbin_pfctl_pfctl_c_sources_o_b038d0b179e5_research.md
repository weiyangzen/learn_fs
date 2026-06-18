# Group Research: group_1378_openbsd_src_sources_os_bsd_openbsd_src_sbin_pfctl_pfctl_c_sources_o_b038d0b179e5

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/openbsd-src` is in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl.c

`pfctl.c` is the main command implementation for OpenBSD `pfctl`. It owns CLI option parsing, `/dev/pf` access mode selection, high-level command dispatch, PF enable/disable/reset paths, rule loading transactions, anchor recursion, state/source-node operations, queue loading, state/source limiter loading, and display flows for rules, labels, state, sources, status, limits, timeouts, tables, queues, interfaces, and OS fingerprints.

Primary responsibilities:
- Defines global command state such as selected clear/show/table/debug options, PF device path, interface/table/anchor selectors, kill keys, `dev`, title formatting state, label state, and final `exit_val`.
- Implements fatal/nonfatal wrappers `pfctl_err()` and `pfctl_errx()` that honor `PF_OPT_IGNFAIL` for recursive best-effort operations.
- Implements direct PF controls through ioctls including `DIOCSTART`, `DIOCSTOP`, `DIOCCLRSTATUS`, `DIOCCLRIFFLAG`, `DIOCCLRSTATES`, `DIOCCLRSRCNODES`, `DIOCKILLSTATES`, `DIOCKILLSRCNODES`, `DIOCGETSTATUS`, `DIOCGETSYNFLWATS`, `DIOCGETTIMEOUT`, `DIOCGETLIMIT`, and option-setting ioctls.
- Drives rule loading through `pfctl_rules()`, which initializes parser state, creates ruleset/table transactions, parses config with `parse_config()`, validates queue assignments, loads queues/state limiters/source limiters/options, recursively loads anchors/rules/tables, and commits or rolls back transactions.
- Handles anchor traversal and recursive clear/show operations through `pfctl_walk_anchors()`, `pfctl_get_anchors()`, and `pfctl_recurse()`.
- Maintains local RBT caches for state limiter and source limiter lookup by id/name so rule printing can resolve limiter names on demand.

Important control flow:
- `main()` parses flags with `getopt()`, validates mutually exclusive DNS modes and table command pairing, normalizes anchor wildcard syntax, opens `/dev/pf` unless `-n` no-action prevents mutation, reads current PF limits, and then dispatches show, clear, kill, table, rule-load, enable, debug, state-store, and state-load operations.
- No-action mode clears mutating flags and may still open `/dev/pf` read-only to populate current limits for realistic parse/load simulation.
- Rule loading uses transaction buffers from `pfctl_add_trans()`/`pfctl_get_ticket()`/`pfctl_trans()`. Main ruleset loading begins transactions before parsing because table definitions are still loaded at parse time.
- `pfctl_load_ruleset()` recurses over in-memory parser-created `pf_ruleset` trees, optionally optimizes a ruleset, expands labels, calls `pfctl_load_rule()`, descends into child anchors, and finally loads tables scoped to each anchor.
- Queue definitions are collected in global `qspecs` and `rootqs`; `pfctl_check_qassignments()` builds hierarchy and enforces leaf assignment before `pfctl_load_queues()` sends them with `DIOCADDQUEUE`.

Integration points:
- Depends on parser state and helpers from `pfctl_parser.h`/`pfctl_parser.c`, including `parse_config()`, `print_rule()`, host/address helpers, table buffers, limiter structs, queue structs, and option setters.
- Depends on table/radix wrappers from `pfctl_radix.c` for table transactions and table buffer handling.
- Calls OS fingerprint functions from `pfctl_osfp.c` when showing/loading rules or loading the main ruleset.
- Calls queue display from `pfctl_queue.c`; queue loading itself is in this file.
- Calls optimizer from `pfctl_optimize.c` when optimization is enabled.
- Relies heavily on kernel ABI structures from `<net/pfvar.h>` and ioctls against `/dev/pf`.

Data and state:
- `limit_curr[]` snapshots current PF limits so temporary load failures can restore settings via `pfctl_restore_limits()`.
- `pfctl_init_options()` fills parser/runtime defaults for timeouts, limits, syncookie watermarks, debug level, and reassembly. Fragment/table limits are derived partly from `sysctl()` values and current kernel limits.
- State and source limiter caches are RBTs embedded in `struct pfctl`.

Notable risks and edge cases:
- The file is process-oriented: many allocations are intentionally not freed on success because `pfctl` exits shortly after command completion.
- Recursive anchor modification sets `PF_OPT_IGNFAIL`, so failures in one anchor do not abort cleanup of later anchors; callers must rely on accumulated return value.
- String copying consistently uses `strlcpy()`/fixed-size kernel ABI fields, with explicit fatal errors on overflow.
- State/source kill paths resolve hostnames unless `PF_OPT_NODNS` is set and deduplicate only adjacent `getaddrinfo()` duplicates.
- `pfctl_key_kill_states()` requires an exact four-token key format: protocol, host:port, direction, host:port.
- Anchor names beginning with `_` are protected from command-line modification because those anchors are reserved for unnamed brace notation.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl.h

`pfctl.h` is the shared public header for non-parser `pfctl` modules. It defines shared table-buffer infrastructure, anchor-list structures, user-kernel table wrappers, display mode enums, and cross-file prototypes for PF table, interface, state, queue, error, printing, and transaction helpers.

Primary responsibilities:
- Defines `DBGPRINT()` as a compile-time optional debug macro under `PFCTL_DEBUG`.
- Defines `enum pfctl_show` for rule/label/no-output display formats.
- Defines `PFRB_*` buffer types and `struct pfr_buffer`, a typed dynamic array used for tables, table stats, addresses, address stats, interfaces, and transaction entries.
- Provides `PFRB_FOREACH()` iteration over typed buffers via `pfr_buf_next()`.
- Defines `struct pfr_anchoritem` and `SLIST_HEAD(pfr_anchors, ...)` for recursive anchor traversal.
- Defines `struct pfr_uktable`, the userland table wrapper that embeds a kernel table plus initializer address buffer and list linkage.
- Exposes `pfr_ktables`, the global RB tree of parser-created table definitions.

Important exported APIs:
- Table operations: `pfr_clr_tables()`, `pfr_add_tables()`, `pfr_del_tables()`, `pfr_get_tables()`, `pfr_get_tstats()`, `pfr_clr_tstats()`, `pfr_*_addrs()`, `pfr_tst_addrs()`, and `pfr_ina_define()`.
- Buffer operations: `pfr_buf_clear()`, `pfr_buf_add()`, `pfr_buf_next()`, `pfr_buf_grow()`, and `pfr_buf_load()`.
- User-visible command helpers: `pfctl_clear_tables()`, `pfctl_show_tables()`, `pfctl_table()`, `pfctl_show_ifaces()`, and `pfctl_show_queues()`.
- Printing helpers shared across modules: address, host, sequence, state, title, and error functions.
- Transaction helpers: `pfctl_add_trans()`, `pfctl_get_ticket()`, and `pfctl_trans()`.
- Limiter name resolution: `pfctl_statelim_id2name()` and `pfctl_sourcelim_id2name()`.

Integration points:
- Implemented primarily by `pfctl_radix.c`, `pfctl.c`, `pfctl_parser.c`, `pfctl_queue.c`, and table/interface modules elsewhere in the pfctl directory.
- Includes forward declaration for `struct pfctl` because detailed parser/runtime state lives in `pfctl_parser.h`.
- Mirrors kernel PF structures from `<net/pfvar.h>` but keeps userland buffer and wrapper abstractions local to `pfctl`.

Notable risks and edge cases:
- `struct pfr_buffer` correctness depends on `pfrb_type`; the implementation maps each type to a fixed element size.
- The `pfr_uktable` field-alias macros expose embedded kernel table fields, which keeps parser code terse but couples field layout to `struct pfr_ktable`.
- This header is central shared ABI within `pfctl`; changes here affect several C files.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_optimize.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_optimize.c

`pfctl_optimize.c` implements conservative userland rule optimization before rules are loaded into the kernel. It groups compatible adjacent rules into superblocks, removes duplicates/subsets, combines many address-differing rules into generated PF tables, reorders rules to improve kernel skip-step behavior, and optionally uses current kernel rule counters as a profile to prioritize quick rules.

Primary responsibilities:
- Defines optimization metadata for `struct pf_rule` fields via `pf_rule_desc[]`, classifying fields as `BARRIER`, `BREAK`, `NOMERGE`, `COMBINED`, `DC`, or `NEVER`.
- Defines `struct superblock`, a sequence of adjacent semantically compatible rules that may be optimized internally.
- Defines `struct pf_skip_step`, per-skip-dimension groups used to find common fields for skip-step-friendly ordering.
- Implements `pfctl_optimize_ruleset()` as the top-level transform from `struct pf_rule` queue to optimized rule queue.
- Creates optimizer-generated const tables when enough similar rules differ only by source or destination address.

Optimization pipeline:
- `construct_superblocks()` partitions the ruleset into superblocks using `superblock_inclusive()`.
- `remove_identical_rules()` removes exact duplicate or covered rules after normalizing don't-care fields and supersets.
- `combine_rules()` detects rules that differ only by source or destination address and builds an optimizer table once the rule count reaches `TABLE_THRESHOLD` (6).
- `reorder_rules()` builds skip-step lists for interface, direction, rdomain, AF, protocol, source/destination address, and source/destination port, then reorders or recursively splits blocks to maximize common skip jumps.
- `load_feedback_profile()` fetches the active kernel ruleset, constructs comparable superblocks, and attaches matching profile blocks.
- `block_feedback()` orders quick rules by observed packet counts from the active ruleset when profile optimization is requested.

Generated table flow:
- `add_opt_table()` creates a temporary `pf_opt_tbl`, appends addresses with `append_addr_host()`, and stores printable nodes for verbose output.
- `pf_opt_create_table()` snapshots existing tables, chooses a collision-resistant name using `PF_OPTIMIZER_TABLE_PFX`, `arc4random()`, and a counter, then calls `pfctl_define_table()`.
- Once a table is generated, the rule address is rewritten to `PF_ADDR_TABLE` and the generated table name is copied into the rule.

Semantic safety:
- `BARRIER` fields force a rule into its own block and prevent reordering.
- `BREAK` fields must be equal across a superblock.
- `NOMERGE` fields may allow reordering but prevent rule combination.
- `COMBINED` fields are the only address fields that can be replaced by generated tables.
- Interface groups are treated as superblock breaks when names differ, because group membership can change at runtime and could invalidate reordering assumptions.
- Per-rule source tracking (`PFRULE_RULESRCTRACK`) also forces a hard break.

Integration points:
- Called by `pfctl_load_ruleset()` in `pfctl.c` when optimization is enabled.
- Uses parser structures from `pfctl_parser.h`: `pf_opt_rule`, `pf_opt_tbl`, node initializers, and table helpers.
- Uses address/table helpers from `pfctl_parser.c` and `pfctl_radix.c`: `append_addr_host()`, `unmask()`, `pfr_get_tables()`, `pfctl_define_table()`, and `print_tabledef()`.
- Reads live kernel rules via `DIOCGETRULES`/`DIOCGETRULE` for profile optimization.

Notable risks and edge cases:
- The optimizer intentionally avoids many possible optimizations to preserve PF semantics; labels, anchors, probability, max-state fields, and several state/queue/route attributes block movement.
- Table generation only combines address masks, not ports or mixed v4/v6 rules.
- Several internal TODO comments call out possible improvements and protocol-specific skip-step nuances.
- Memory ownership is mostly process-lifetime oriented; table refs are reference-counted, but optimization exits soon after load.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_optimize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_osfp.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_osfp.c

`pfctl_osfp.c` handles passive OS fingerprint loading, parsing, importing, lookup, and display for PF. It parses `/etc/pf.os`-style colon-delimited fingerprint records, maintains a local hierarchy of OS class/version/subtype names, packs those names into PF OS fingerprint ids, and syncs fingerprints to or from the kernel through OSFP ioctls.

Primary responsibilities:
- Parses fingerprint files in `pfctl_file_fingerprints()`.
- Clears kernel fingerprints with `DIOCOSFPFLUSH` and local fingerprints by recursively freeing the `classes` name tree.
- Loads active kernel fingerprints through repeated `DIOCOSFPGET` calls until kernel indicates completion.
- Shows fingerprints as class/version/subtype trees.
- Resolves string names to packed `pf_osfp_t` ids and packed ids back to printable names.
- Adds fingerprints to kernel with `DIOCOSFPADD`, or to fake-kernel test builds via `pf_osfp_add()`.

Data model:
- `struct name_entry` nodes form nested `LIST` trees: classes contain versions, versions contain subtypes.
- Each name entry has a numeric id assigned on first insert/import.
- Global `classes`, `class_count`, and `fingerprint_count` track current local state.
- PF ids are packed/unpacked through PF OSFP macros and validated against class/version/subtype bit widths.

File parsing:
- Each nonblank, noncomment line is split into fields: window size, TTL, DF, packet size, TCP options, OS class, version, subtype, and description.
- Integer fields support modifiers such as don't-care, MSS multiple, MTU multiple, and modulus where allowed.
- TCP options support NOP, SACK, timestamp, MSS, and window scale, with support for wildcard/modulus MSS and window scale.
- For each IPv4 fingerprint, the loader also creates an IPv6 variant by setting `PF_OSFP_INET6`, forcing DF, and adjusting packet size for IPv6 header length.
- Class names starting with `@` are generic; names starting with `*` suppress detail.

Lookup behavior:
- `pfctl_get_fingerprint()` recognizes `"unknown"`, direct class-only names, class/version names, and class/version/subtype names.
- It performs fuzzy subtype matching for common version-subtype separators such as `.`, whitespace, tab, and `-`.
- `pfctl_lookup_fingerprint()` prints `"unknown"`, `"any"`, `"nomatch"`, or a reconstructed class/version/subtype string with separator heuristics.
- Version and subtype ranges like `2.0-2.4` can be expanded by `add_fingerprint()` into multiple fingerprints.

Integration points:
- Called by `pfctl.c` before showing rules and when loading the main ruleset from `PF_OSFP_FILE`.
- Called by parser/rule printing through `pfctl_get_fingerprint()` and `pfctl_lookup_fingerprint()`.
- Uses `pfctl_fopen()` to reject directories as fingerprint input.
- Depends on PF OSFP kernel structures and ioctls from `<net/pfvar.h>`.

Notable risks and edge cases:
- Parsing is permissive about comments/whitespace but strict about field count and field-specific modifiers.
- `get_tcpopts()` stops at `PF_OSFP_MAX_OPTS`; extra option text beyond that can be accepted only as far as parsing permits.
- Duplicate kernel signatures are reported as warnings, while most other add failures are fatal.
- `pfctl_get_fingerprint()` warns and returns no match if packed ids overflow allocated bit fields.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_osfp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_parser.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_parser.c

`pfctl_parser.c` is shared parser support rather than the grammar itself. It provides symbolic ICMP/log/timeouts lookup, rule/status/source/queue/table printing, TCP flag parsing, address and interface resolution, netmask handling, address-buffer appending, and PF transaction helpers used by the grammar and main command code.

Primary responsibilities:
- Defines ICMP/ICMPv6 type and code name tables.
- Defines `pf_timeouts[]`, the canonical string-to-timeout mapping used by set/show timeout paths.
- Implements printable reconstruction of PF kernel structs: rules, pools, state/source limiters, source nodes, status, queue specs, and table definitions.
- Implements host/interface/DNS address resolution into `struct node_host` lists.
- Converts `node_host` lists into PF table address buffers through `append_addr()` and `append_addr_host()`.
- Provides transaction buffer helpers `pfctl_add_trans()`, `pfctl_get_ticket()`, and `pfctl_trans()`.

Printing behavior:
- `print_rule()` reconstructs a rule in pf.conf-like syntax, covering action, anchor calls, return behavior, direction, logging, quick, interface/rdomain, AF, protocol, from/to, ports, OS fingerprint, UID/GID, flags, ICMP type/code, TOS, priority, packet rate, set clauses, state options, probability, state/source limiters, scrub options, labels, tags, rtable, divert, NAT/RDR/af-to, and route/reply/dup-to.
- `print_status()` formats runtime, hostid/checksum, interface counters, state/source/fragments/counters/limit counters, and syncookie watermarks.
- `print_src_node()`, `print_statelim()`, `print_sourcelim()`, `print_tabledef()`, and `print_queuespec()` provide focused formatters for PF subobjects.
- Service names are used for ports only when `PF_OPT_PORTNAMES` is set.

Address/interface handling:
- `set_ipmask()` builds IPv4/IPv6 masks and masks address bits.
- `check_netmask()` validates IPv4 masks do not exceed 32 bits.
- `gen_dynnode()` clones dynamic interface table nodes and clamps IPv4 masks.
- `ifa_load()` snapshots `getifaddrs()` into `iftab`, including AF_LINK indexes, IPv4/IPv6 addresses, netmasks, broadcast, peer, and scope ids.
- `ifa_exists()` checks both real interfaces and interface groups via `SIOCGIFGMEMB`.
- `ifa_grouplookup()` expands interface groups by recursively resolving members.
- `ifa_lookup()` resolves interface selectors, `self`, broadcast/peer/network/noalias modifiers, and prefix matching for interface families.
- `host()` attempts interface lookup, numeric IP parsing, then DNS lookup unless numeric/no-DNS mode is requested.
- `host_ip()` supports both normal numeric addresses and IPv4 network shorthand such as `10/8`.
- `host_dns()` supports `:0` no-alias selection.

Integration points:
- `parse_config()` and `pfctl_load_anchors()` are declared elsewhere but depend on these helpers.
- `pfctl.c` uses the print helpers for show paths, option setters for parser actions, and transaction helpers for load/clear operations.
- `pfctl_radix.c` calls `append_addr()` through `pfr_buf_load()`.
- `pfctl_optimize.c` uses `append_addr_host()`, `unmask()`, and `print_tabledef()`.
- OS fingerprint printing uses `pfctl_lookup_fingerprint()`.

Notable risks and edge cases:
- `append_addr()` uses static state to apply a following `weight` token to addresses added by the previous call; callers must preserve token order.
- Interface-group expansion and `self` can produce many addresses and mixes IPv4/IPv6 depending on system state.
- DNS lookup behavior is controlled by parser options; reproducibility differs between `PF_OPT_NODNS`, numeric mode, and default mode.
- Many functions allocate linked `node_host` lists; callers usually free only simple lists or rely on process exit.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_parser.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_parser.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_parser.h

`pfctl_parser.h` is the main shared declaration header for parser/runtime state, parser-created intermediate nodes, optimizer containers, queue specification trees, option flags, and cross-module prototypes used by `pfctl`.

Primary responsibilities:
- Defines option bit flags such as enable/disable, verbose/no-action/quiet/debug/show-all/optimize/no-DNS/recurse/port-names/ignore-fail/call-show.
- Defines parser constants including `PF_OSFP_FILE`, NAT proxy port range, optimizer modes, and counter-name override macro `FCNT_NAMES`.
- Defines `struct pfctl`, the central runtime/parser state containing device fd, options, optimization mode, anchor stack, transaction buffer, active anchor, queued table state, ruleset name, limiter trees, and pending `set` option values plus set flags.
- Defines parser AST/intermediate structs: `node_if`, `node_host`, `node_os`, queue bandwidth/HFSC option nodes, table initializer nodes, optimizer table/rule wrappers, queue spec tree items, and syncookie watermarks.
- Declares RBT heads for state/source limiter lookup by id/name.
- Declares parser, loader, optimizer, table, queue, print, address, OS fingerprint, ICMP, loglevel, and transaction helper functions.

Important structures:
- `struct pfctl` binds parser actions to eventual kernel load, including anchor stack depth, current anchor, transaction buffer, limit/timeout/debug/logif/hostid/reassembly/syncookie settings, and RBT limiter registries.
- `struct node_host` is the parser’s normalized address/interface host node, with address wrap, broadcast/peer fields, AF, negation, link-local index, load-balancing weight, interface name, and list/tail pointers.
- `struct pf_opt_tbl` and `struct pf_opt_rule` are optimizer containers that extend PF kernel objects with generated table refs, profile counts, and queue entries.
- `struct pfctl_qsitem` forms queue definition trees for validation/loading.

Integration points:
- Included by `pfctl.c`, `pfctl_parser.c`, `pfctl_optimize.c`, `pfctl_osfp.c`, `pfctl_queue.c`, and likely grammar-generated parser sources in the same directory.
- Complements `pfctl.h`: `pfctl.h` owns table-buffer and command-facing declarations; this header owns parser/runtime state and parser support declarations.
- Uses kernel PF structures heavily, so field layout and constants track `<net/pfvar.h>`.

Notable risks and edge cases:
- `PFCTL_ANCHOR_STACK_DEPTH` is fixed at 64 for parser anchor nesting.
- The option bitmask is shared by CLI, parser, and output code; new flags must avoid collisions.
- Many prototypes expose mutable raw kernel structs, reflecting the C codebase’s direct ABI-oriented style rather than encapsulation.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_parser.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_queue.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_queue.c

`pfctl_queue.c` implements queue display and live queue statistics formatting for `pfctl -s queue`. It fetches queue specs/stats from the PF kernel, maintains a local list keyed by queue name and interface, computes moving averages, and prints HFSC/FQ-CoDel related counters.

Primary responsibilities:
- Defines `struct queue_stats`, containing either HFSC class stats or FQ-CoDel stats, moving-average state, and previous byte/packet counters.
- Defines `struct pfctl_queue_node`, tying a `pf_queuespec` to current stats in the global `qnodes` list.
- Implements `pfctl_show_queues()` as the public display entry point.
- Implements `pfctl_update_qstats()` to fetch all queues and refresh or insert local nodes.
- Implements display helpers for queue specs, verbose stats, debug ids, measured rates, and FQ-CoDel delay stats.
- Implements `rate2str()` for human-readable bit-rate formatting.

Control flow:
- `pfctl_show_queues()` calls `pfctl_update_qstats()`, optionally prints a title, filters by interface, and prints each queue.
- With second-level verbosity (`verbose2`), it loops every `STAT_INTERVAL` seconds, refreshes stats, and reprints measured rates until interrupted or an update fails.
- `pfctl_update_qstats()` first calls `DIOCGETQUEUES` to get count/ticket. A ticket change resets the cached queue-node list. It then iterates with `DIOCGETQSTATS`.
- Existing nodes preserve moving-average history; new nodes are inserted and initialized.

Integration points:
- Called by `pfctl.c` show dispatch.
- Uses `print_queuespec()` from `pfctl_parser.c` for base queue rendering.
- Depends on kernel queue/stat structs from `<net/pfvar.h>`, `<net/hfsc.h>`, and `<net/fq_codel.h>`.
- Uses `PF_OPT_VERBOSE`, `PF_OPT_DEBUG`, and `PF_OPT_SHOWALL` option flags from shared headers.

Notable risks and edge cases:
- Queue-node storage is process-lifetime oriented; nodes are removed from the TAILQ but not explicitly freed before process exit.
- The stats union is interpreted as HFSC for generic packet/byte/drop fields and as FQ-CoDel for flow delay fields when queue flags indicate a top-level flow queue.
- Moving average only updates when counters are monotonic; counter resets/ticket changes clear node state.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_queue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_radix.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_radix.c

`pfctl_radix.c` provides PF table/radix ioctl wrappers, interface ioctl wrappers, typed dynamic buffer management, and token loading for table address files. It is the low-level bridge between `pfctl` table operations and `/dev/pf` ioctls.

Primary responsibilities:
- Defines the global `pfr_ktables` RB tree and generates RB functions for parser-created table definitions.
- Implements `pfr_ktable_compare()` ordering by table name and anchor.
- Wraps table ioctls for clearing/adding/deleting/getting tables, getting/clearing table stats, clearing/adding/deleting/setting/getting/testing addresses, getting/clearing address stats, inactive-define operations, and interface listing.
- Implements typed `struct pfr_buffer` operations used throughout pfctl.
- Implements `pfr_buf_load()` to read address tokens from a file or stdin and append them as table addresses.
- Implements `pfr_next_token()` to parse whitespace-separated tokens while skipping comments.

Table/ioctl wrappers:
- Table functions prepare `struct pfioc_table`, validate pointer/size combinations, fill flags, table filters, buffer pointers, element sizes, sizes/tickets, then call the appropriate `DIOCR*` ioctl.
- `pfr_ina_define()` supports inactive transaction table definition with a ticket, used during ruleset loads.
- `pfi_get_ifaces()` wraps `DIOCIGETIFACES` for interface status display elsewhere.

Buffer handling:
- `buf_esize[]` maps each `PFRB_*` type to its element size.
- `pfr_buf_add()` grows as needed, copies one typed element, and increments size.
- `pfr_buf_next()` supports `PFRB_FOREACH()` iteration.
- `pfr_buf_grow()` allocates at least 64 entries initially or doubles capacity, using `reallocarray()` and zeroing the new region.
- `pfr_buf_clear()` frees backing memory and resets counters.

Input parsing:
- `pfr_buf_load()` opens files through `pfctl_fopen()` unless input is `-`, then repeatedly tokenizes and calls `append_addr()`.
- `pfr_next_token()` skips whitespace and `#` comments, enforces `BUF_SIZE`, and uses a static `next_ch` to preserve one-character lookahead across calls.

Integration points:
- Uses global `dev` from `pfctl.c` for all ioctl calls.
- Exposes wrappers via `pfctl.h`.
- Calls parser address conversion through `append_addr()`.
- Used by table command implementation, parser table loading, optimizer table generation, and transaction handling.

Notable risks and edge cases:
- All wrappers reject negative sizes and missing buffers for nonzero sizes with `EINVAL`.
- `pfr_clr_astats()` requires an address pointer even when size validation otherwise allows some null table cases, matching its specific ioctl semantics.
- `pfr_next_token()` has static lookahead state, so it is not reentrant and assumes sequential file loading.
- Initial buffer growth handles `pfrb_msize == 0`; callers must set a valid `pfrb_type` before using buffer operations.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_radix.c -->