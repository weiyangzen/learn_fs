# Group Research: FreeBSD pfctl control, ALTQ, optimizer, and OS fingerprint support

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/freebsd-src`. Files read completely: `pfctl.c`, `pfctl.h`, `pfctl_altq.c`, `pfctl_ioctl.h`, `pfctl_optimize.c`, `pfctl_osfp.c`.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl.c

## Purpose

`pfctl.c` is the main userland control program for FreeBSD PF. It parses `pfctl` command-line options, opens the PF device/netlink handle, dispatches show/flush/load/kill operations, and coordinates parser output with kernel/libpfctl transactions.

It is the central integration file for:
- Enabling/disabling PF and ALTQ.
- Loading rules, NAT, Ethernet rules, tables, ALTQ, options, state limiters, and source limiters.
- Showing status, rules, anchors, tables, states, source nodes, timeouts, limits, OS fingerprints, creator IDs, and queue state.
- Flushing rules/NAT/tables/states/statistics/source nodes/fingerprints/options.
- Killing PF states or source tracking entries by network, gateway, label, ID, key, source limiter entry, or interface.
- Managing anchor recursion and rule transaction lifecycles.

## Main Data And Globals

Key globals:
- `dev`: opened PF device descriptor.
- `pfh`: global `struct pfctl_handle *` used by libpfctl calls.
- `loadopt`: bitmask of requested load categories such as NAT/filter/table/option/ALTQ/Ethernet.
- `altqsupport`: runtime ALTQ availability flag.
- `pf_main_anchor`, `pf_eth_main_anchor`, `pf_anchors`: parser/load anchor state.
- `skip_b`: cached interface list used when preserving or adjusting `set skip` interface flags.
- command option globals such as `clearopt`, `rulesopt`, `showopt`, `debugopt`, `anchoropt`, `ifaceopt`, `tableopt`, `tblcmdopt`, and kill argument arrays.

The file uses FreeBSD PF structs from `<net/pfvar.h>`, parser-owned structs from `pfctl_parser.h`, and shared declarations from `pfctl.h`.

## CLI Dispatch

`main()` parses the `pfctl` CLI:
- `-e` / `-d`: enable or disable PF.
- `-f`: load rules from file.
- `-F`: flush selected data.
- `-s`: show selected data.
- `-T` / `-t`: table command and table name.
- `-k`: kill states, with special modes `label`, `id`, `gateway`, `key`, and `source`.
- `-K`: kill source nodes.
- `-a`: operate on an anchor, with trailing `*` enabling recursion.
- `-o`: select optimizer level: `none`, `basic`, or `profile`.
- `-n`: no-action parse/check mode.
- `-m`: merge mode.
- `-M`: kill matching states.
- `-S` and `-r`: DNS resolution behavior.

After option parsing, `main()` opens PF, tests ALTQ support, reads current limits, dispatches show/flush/kill/table/load/debug/enable operations, and closes `dev`/`pfh` on successful exit to avoid the registered limit restore handler.

## Error Handling

`pfctl_err()` and `pfctl_errx()` wrap `err`/`errx` behavior with `PF_OPT_IGNFAIL` support. In ignore-failure mode, they warn, set `exit_val`, and let recursive clearing continue where possible.

`pf_strerror()` maps selected PF errors to user-facing anchor/table messages.

## Protocol Name Cache

`pfctl_proto2name()` caches protocol number to name translations for protocol IDs up to 258, avoiding repeated `getprotobynumber()` calls during large state dumps. It duplicates names because libc protocol lookup storage may be overwritten on subsequent calls.

## Enable, Disable, And Status Clearing

- `pfctl_enable()` calls `pfctl_startstop(pfh, 1)`, reports common errors, optionally starts ALTQ with `DIOCSTARTALTQ`, and prints `pf enabled`.
- `pfctl_disable()` calls `pfctl_startstop(pfh, 0)`, optionally stops ALTQ with `DIOCSTOPALTQ`, and prints `pf disabled`.
- `pfctl_clear_stats()` clears PF status counters through `pfctl_clear_status()`.

## Interface Skip Flags

The file caches and adjusts interface skip flags around ruleset loads:
- `pfctl_get_skip_ifaces()` grows `skip_b` and fetches interfaces with `pfi_get_ifaces()`.
- `pfctl_check_skip_ifaces()` clears cached skip flags for interfaces referenced by new rules, including group members.
- `pfctl_adjust_skip_ifaces()` reapplies or clears skip flags after parsing options.
- `pfctl_clear_interface_flags()` clears all `PFI_IFLAG_SKIP` flags through `DIOCCLRIFFLAG`.

## Flush Operations

Implemented flush helpers include:
- `pfctl_flush_eth_rules()`: clear Ethernet rules for an anchor.
- `pfctl_flush_rules()`: clear filter rules for an anchor.
- `pfctl_flush_nat()`: clear NAT/RDR/binat rules.
- `pfctl_clear_altq()`: clears ALTQ through a transaction.
- `pfctl_clear_src_nodes()`: `DIOCCLRSRCNODES`.
- `pfctl_clear_iface_states()`: clears states, optionally scoped to interface and `PF_OPT_KILLMATCH`.

`main()` combines these for `-F all`, `-F Reset`, and recursive anchor operations.

## Address And Kill Helpers

`pfctl_addrprefix()` parses host/network strings with optional CIDR suffix and returns `addrinfo` plus a PF mask.

State/source kill paths:
- `pfctl_kill_src_nodes()` kills source nodes by source and optional destination.
- `pfctl_net_kill_states()` kills states by source/destination network, including special `nat` handling.
- `pfctl_gateway_kill_states()` kills states by route gateway.
- `pfctl_label_kill_states()` kills states by rule label.
- `pfctl_id_kill_states()` kills states by state ID and optional creator ID.
- `pfctl_key_kill_states()` parses `protocol host1:port1 direction host2:port2`.
- `pfctl_kill_source()` clears one source limiter entry by limiter ID and address.
- `pfctl_parse_host()` parses host/port strings into `struct pf_rule_addr`.

## Rule Pool Handling

`pfctl_get_pool()` fetches NAT/RDR/route pool addresses for a kernel rule and builds a `TAILQ` of `pfctl_pooladdr`.

`pfctl_move_pool()` moves pool entries between rule structs without copying allocations.

`pfctl_clear_pool()` releases pool entries.

These are used by show and load paths so pool state survives parser/ruleset copying.

## Showing Rules And Counters

Display helpers include:
- `pfctl_print_eth_rule_counters()`: Ethernet rule evaluation/packet/byte/last-active counters.
- `pfctl_print_rule_counters()`: skip-step debug data, queue IDs, expiration, packet/byte/state/source-node counters, insertion identity, and last-active time.
- `pfctl_print_title()`: section title formatting for `-s all`.

Rule display paths:
- `pfctl_show_eth_rules()`: walks Ethernet rules and wildcard anchors.
- `pfctl_show_rules()`: shows scrub/filter rules, labels, counters, pools, and recursive anchor bodies.
- `pfctl_show_nat()`: shows NAT/RDR/binat rules.
- `pfctl_show_src_nodes()`: prints source tracking nodes.
- `pfctl_show_states()`: fetches states, optionally including rule data for verbose output.
- `pfctl_show_status()`: prints status and syncookie settings.
- `pfctl_show_running()`: reports running state and uses exit status for scripts.
- `pfctl_show_timeouts()` and `pfctl_show_limits()` print current PF timers and limits.
- `pfctl_show_statelims()` and `pfctl_show_sourcelims()` display limiter configuration and counters.
- `pfctl_show_creators()` lists PF state creator IDs.

## Loading Rules

`pfctl_rules()` is the core load operation:
1. Initializes anchor and Ethernet anchor roots.
2. Creates or reuses a transaction buffer.
3. Initializes default PF options.
4. Opens transactions before parsing because tables may be loaded during parse.
5. Calls `parse_config(filename, &pf)`.
6. Adjusts skip interfaces when options are loaded.
7. Loads state/source limiters for the main filter ruleset.
8. Loads scrub, Ethernet, NAT/RDR/binat, and filter rulesets in order.
9. Validates ALTQ with `check_commit_altq()`.
10. Loads nested anchors.
11. Loads global options and commits the transaction, or rolls back on error.

The function respects no-action mode and anchor scoping. ALTQ is disabled for non-root anchors.

## Loading Individual Rules And Rulesets

- `pfctl_init_rule()` initializes a `pfctl_rule` and its pool queues.
- `pfctl_append_rule()` appends parser-produced rules into the current anchor ruleset.
- `pfctl_append_eth_rule()` appends Ethernet rules and creates non-brace anchor structures when needed.
- `pfctl_ruleset_trans()` adds needed rule/table/ALTQ transaction entries before load.
- `pfctl_eth_ruleset_trans()` handles Ethernet-only transactions.
- `pfctl_load_ruleset()` recursively loads anchor rulesets, expands labels/tags, invokes optimization for filter rules, and loads tables tied to anchors.
- `pfctl_load_rule()` begins address pools, loads RDR/NAT/route pools, adds the rule with `pfctl_add_rule_h()`, handles `EEXIST`, prints verbose output, and clears pools.
- `pfctl_load_eth_ruleset()` and `pfctl_load_eth_rule()` perform the same for Ethernet rules.
- `pfctl_add_altq()` adds ALTQ entries and records them for later scheduler validation.

## Options, Defaults, And Reset

`pfctl_init_options()` sets default PF timeout, limit, debug, reassembly, and syncookie values. Some defaults preserve current kernel values when available.

`pfctl_load_options()` applies configured limits, adaptive timeout defaults, all timeouts, debug level, log interface, hostid, reassembly, keepcounters, and syncookies. Merge mode only applies explicitly set fields.

Other option helpers:
- `pfctl_apply_limit()`, `pfctl_load_limit()`
- `pfctl_apply_timeout()`, `pfctl_load_timeout()`
- `pfctl_set_reassembly()`
- `pfctl_set_optimization()`
- `pfctl_set_logif()`, `pfctl_load_logif()`
- `pfctl_set_hostid()`, `pfctl_load_hostid()`
- `pfctl_cfg_syncookies()`, `pfctl_load_syncookies()`
- `pfctl_do_set_debug()`, `pfctl_load_debug()`, `pfctl_debug()`
- `pfctl_set_interface_flags()`

`pfctl_reset()` constructs a default `pfctl` option state, marks all limits/timeouts/options as set, commits them in a transaction, and clears interface skip flags.

## Anchors And Recursion

Anchor functions:
- `pfctl_walk_anchors()` recursively enumerates filter anchors.
- `pfctl_show_anchors()` prints filter anchors.
- `pfctl_show_eth_anchors()` prints Ethernet anchors.
- `pfctl_get_anchors()` builds an SLIST of anchor names, including root.
- `pfctl_recurse()` walks anchor lists for recursive clear/show operations.

Callback wrappers:
- `pfctl_call_cleartables()`
- `pfctl_call_clearrules()`
- `pfctl_call_clearanchors()`
- `pfctl_call_showtables()`

## Limiters

The file defines red-black trees for parsed state and source limiters by ID and name:
- `pfctl_statelim_ids`, `pfctl_statelim_nms`
- `pfctl_sourcelim_ids`, `pfctl_sourcelim_nms`

Load/show functions use `pfctl_state_limiter_*` and `pfctl_source_limiter_*` libpfctl calls.

Notable implementation detail: `pfctl_get_statelim_id()` and `pfctl_get_sourcelim_id()` build an ID key but call `RB_FIND()` on the name tree, which appears inconsistent with their names and the generated ID trees. That should be checked against callers and upstream history before changing, but it is a suspicious local defect.

## External Dependencies

Important functions/types come from:
- `libpfctl`: modern PF accessors such as `pfctl_open`, `pfctl_get_status_h`, `pfctl_add_rule_h`, `pfctl_kill_states_h`, limiter APIs, and state APIs.
- kernel ioctls: `DIOC*` operations for legacy/direct PF controls.
- parser modules: `parse_config`, table routines, anchor setup, print routines, ALTQ validation, fingerprint loading.
- `pfctl_altq.c`, `pfctl_optimize.c`, `pfctl_osfp.c`, and table/parse support files.

## Role In Subset A

This is userland OS/filesystem-adjacent infrastructure rather than filesystem code. In the FreeBSD source tree, it is a high-value OS control-plane example: transaction-oriented kernel configuration loading, stable CLI dispatch, kernel state inspection, recursive namespace/anchor traversal, and conservative semantics-preserving rule transformation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl.h

## Purpose

`pfctl.h` is the shared local header for the pfctl userland modules. It declares common structs, macros, globals, and cross-file functions used by rule loading, parsing, tables, ALTQ, state display, and OS fingerprint support.

## Main Contents

The header includes `<libpfctl.h>` and exposes the global PF handle:

- `extern struct pfctl_handle *pfh;`

It defines:
- `DBGPRINT(...)`: conditional debug printing under `PFCTL_DEBUG`.
- `enum pfctl_show`: output mode for rules, labels, or no output.
- `struct pfr_buffer`: local growable buffer abstraction used for tables, addresses, interface lists, transactions, and stats.
- `PFRB_FOREACH`: iterator over `pfr_buffer`.
- `struct pfr_ktable` and `struct pfr_uktable`: pfctl-side table representations used while parsing/loading table state.
- `struct pfr_anchoritem` and `SLIST_HEAD(pfr_anchors, ...)`: anchor-list representation for recursive operations.
- `struct segment`: service-curve segment used by ALTQ admission control.

## Buffer And Table Interfaces

The header declares table and address buffer functions:
- `pfr_add_table`, `pfr_del_table`, `pfr_get_tables`
- `pfr_clr_astats`, `pfr_clr_addrs`
- `pfr_add_addrs`, `pfr_del_addrs`, `pfr_set_addrs`
- `pfr_get_addrs`, `pfr_get_astats`, `pfr_tst_addrs`
- `pfr_ina_define`
- `pfr_buf_clear`, `pfr_buf_add`, `pfr_buf_next`, `pfr_buf_grow`, `pfr_buf_load`

These support parser-driven table definitions and runtime table commands.

## pfctl Cross-Module Declarations

The header declares shared front-end functions:
- table operations: `pfctl_do_clear_tables`, `pfctl_show_tables`, `pfctl_table`
- ALTQ display: `pfctl_show_altq`
- interface display: `pfctl_show_ifaces`
- creator ID display: `pfctl_show_creators`
- safe file open: `pfctl_fopen`
- title printing: `pfctl_print_title`
- parse macro definition: `pfctl_cmdline_symset`

It also declares print helpers used by multiple files:
- `print_addr`
- `print_addr_str`
- `print_host`
- `print_seq`
- `print_state`

## Transaction And Ruleset Interfaces

Important rule-loading declarations:
- `pfctl_add_trans`
- `pfctl_get_ticket`
- `pfctl_trans`
- `pf_get_ruleset_number`
- `pf_init_ruleset`
- `pfctl_anchor_setup`
- `pf_remove_if_empty_ruleset`
- `pf_find_ruleset`
- `pf_find_or_create_ruleset`
- `pf_init_eth_ruleset`
- `pfctl_eth_anchor_setup`
- `pf_find_or_create_eth_ruleset`
- `pf_remove_if_empty_eth_ruleset`
- `expand_label`

These are the glue between parser output, anchor/ruleset trees, and kernel transactions.

## FreeBSD-Specific Definitions

Under `__FreeBSD__`, the header exposes:
- `extern int altqsupport;`
- `extern int dummynetsupport;`
- `HTONL(x)` macro wrapping `htonl`.

It also supplies default queue constants if not already defined:
- `DEFAULT_PRIORITY`
- `DEFAULT_QLIMIT`

## ALTQ Declarations

ALTQ-related declarations include:
- `check_commit_altq()`
- `pfaltq_store()`
- `rate2str()`

The `struct segment` definition supports generalized service-curve math in `pfctl_altq.c`.

## Error And Protocol Helpers

Declared shared helpers:
- `pfctl_proto2name()`
- `pfctl_err()`
- `pfctl_errx()`
- `pf_strerror()`

## Role In This Group

This header is a coordination point rather than a behavior-heavy module. It defines the local ABI between pfctl’s parser, table manager, queueing support, optimizer, display code, and main command dispatcher.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_altq.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_altq.c

## Purpose

`pfctl_altq.c` implements pfctl’s ALTQ queueing support. It stores parsed ALTQ and queue definitions, resolves queues by interface/name, computes scheduler-specific parameters, validates queue hierarchies before commit, and prints ALTQ configuration.

Supported schedulers in this file include:
- CBQ
- PRIQ
- HFSC
- FAIRQ
- CODEL

## Initialization And Maps

The file keeps:
- `interfaces`: STAILQ of interface-level ALTQ definitions.
- `queue_map`: hash table keyed by `ifname:qname`.
- `if_map`: hash table keyed by interface name.
- `qid_map`: hash table keyed by queue name.

`pfctl_altq_init()` is a constructor that creates all three hash tables with `hcreate_r()`.

`pfaltq_store()` copies a `struct pf_altq` into pfctl-owned storage:
- Interface entries are inserted into `if_map` and `interfaces`.
- Queue entries are inserted into `queue_map`.
- Queue names are mapped to queue IDs through `qid_map`.

Lookup helpers:
- `pfaltq_lookup(ifname)`
- `qname_to_pfaltq(qname, ifname)`
- `qname_to_qid(qname)`

The queue ID lookup enforces the convention that queues with the same name across interfaces share the same ID.

## Printing

`print_altq()` prints top-level `altq on <if>` definitions, scheduler options, bandwidth, qlimit, and token bucket size.

`print_queue()` prints queue definitions, optionally including the interface, bandwidth, priority, qlimit, and scheduler options.

Scheduler option printers:
- `print_cbq_opts()`
- `print_priq_opts()`
- `print_hfsc_opts()`
- `print_fairq_opts()`
- `print_codel_opts()`

Service curve printers:
- `print_hfsc_sc()`
- `print_fairq_sc()`

`rate2str()` formats bit rates into compact `b`, `Kb`, `Mb`, or `Gb` strings using a static ring of buffers.

## Evaluating Top-Level ALTQ

`eval_pfaltq()` computes interface-level ALTQ parameters:
- Uses absolute bandwidth if supplied.
- Otherwise queries interface speed through `getifspeed()`.
- Applies percent bandwidth specifications.
- Caps bandwidth to `UINT_MAX` for non-HFSC schedulers.
- Evaluates queue options.
- Computes default `tbrsize` from interface bandwidth and MTU when omitted.

`getifspeed()` queries `SIOCGIFDATA`.

`getifmtu()` queries `SIOCGIFMTU`; on FreeBSD failure it falls back to 1500.

## Evaluating Queues

`eval_pfqueue()` resolves a parsed queue against its parent interface and optional parent queue. It:
- Copies scheduler and interface bandwidth from the top-level ALTQ definition.
- Rejects duplicate queue names on the same interface.
- Resolves or assigns queue IDs.
- Resolves parent queues and parent queue IDs.
- Sets default qlimit.
- Computes queue bandwidth for CBQ/HFSC/FAIRQ.
- Checks child bandwidth against interface and parent bandwidth for non-HFSC schedulers.
- Applies scheduler-specific options with `eval_queue_opts()`.
- Tracks parent child counts.
- Dispatches to scheduler-specific evaluation functions.

`eval_queue_opts()` copies parsed option structures into the kernel `pf_altq` union and resolves bandwidth specifications in HFSC/FAIRQ service curves.

`eval_bwspec()` converts an absolute or percent bandwidth specification into a numeric bandwidth, capped to the reference bandwidth.

## Commit Validation

`check_commit_altq()` walks every interface-level ALTQ entry and runs scheduler-specific validation:
- `check_commit_cbq()`: requires exactly one root queue and exactly one default queue.
- `check_commit_priq()`: requires exactly one default queue.
- `check_commit_hfsc()`: requires exactly one default queue.
- `check_commit_fairq()`: requires exactly one default queue.

The result is used by `pfctl_rules()` before committing an ALTQ transaction.

## CBQ Support

`eval_pfqueue_cbq()` validates priority, sets packet-size defaults from MTU, marks root queues, counts root/default classes, and computes CBQ timing parameters.

`cbq_compute_idletime()` computes:
- `ns_per_byte`
- `maxidle`
- `minidle`
- `offtime`
- `minburst`
- `maxburst`

It uses CBQ’s filter gain constants and clamps values that would overflow kernel integer fields for very low bandwidth queues.

CBQ option flags printed include RED, ECN, RIO, CODEL, clear DSCP, flowvalve, borrow, WRR, efficient, root, and default.

## PRIQ Support

`eval_pfqueue_priq()` validates priority range, enforces unique queue priority per interface via a bitset, and counts default classes.

PRIQ option flags printed include RED, ECN, RIO, CODEL, clear DSCP, and default.

## HFSC Support

`eval_pfqueue_hfsc()` handles HFSC hierarchy and service-curve admission:
- Root queue gets interface-bandwidth linkshare.
- First child initializes parent real-time and linkshare generalized service curves.
- A default queue cannot have children.
- Missing linkshare `m2` defaults to queue bandwidth.
- Convex curve constraints are validated.
- Real-time curves are limited to 80% of interface bandwidth.
- Child linkshare sum must fit under the parent curve.
- Upper-limit curves must not exceed interface bandwidth and must not be lower than real-time curves.

HFSC options printed include RED, ECN, RIO, CODEL, clear DSCP, default, realtime, linkshare, and upperlimit.

## FAIRQ Support

`eval_pfqueue_fairq()` is similar to HFSC but only validates link-sharing curves:
- Root queue gets interface-bandwidth linkshare.
- Default queue cannot have children.
- Missing linkshare `m2` defaults to queue bandwidth.
- Child linkshare sum must fit under the parent FAIRQ curve.

FAIRQ options printed include RED, ECN, RIO, CODEL, clear DSCP, default, and linkshare.

## Generalized Service Curve Math

The file implements an internal generalized service curve representation using `struct segment`.

Functions:
- `gsc_add_sc()`: adds a two-piece service curve into a generalized curve.
- `is_gsc_under_sc()`: checks if a generalized curve is no greater than a target service curve.
- `gsc_getentry()`: finds or creates a segment boundary at a given x-coordinate.
- `gsc_add_seg()`: adds a segment contribution across a curve interval.
- `sc_x2y()`: projects a service curve to y at x.

This code is central to HFSC/FAIRQ admission control.

## Role In This Group

`pfctl_altq.c` is the queueing and traffic-shaping companion to the main pfctl loader. It translates human-readable ALTQ queue syntax into scheduler-specific kernel structures while enforcing hierarchy and bandwidth invariants before rules are committed.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_altq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_ioctl.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_ioctl.h

## Purpose

`pfctl_ioctl.h` is present but empty.

Observed file state:
- 0 lines
- 0 bytes

## Behavior

There are no declarations, macros, includes, comments, or code in this file. It has no direct compile-time behavior as read in this repository snapshot.

## Role In This Group

The empty header may be a placeholder, compatibility remnant, or generated/source-tree alignment artifact. All actual ioctl/libpfctl declarations used by the surrounding pfctl files come from system headers, `<net/pfvar.h>`, `<libpfctl.h>`, and local headers such as `pfctl.h` and `pfctl_parser.h`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_optimize.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_optimize.c

## Purpose

`pfctl_optimize.c` implements pfctl’s filter-rule optimizer. It rewrites parsed filter rules before kernel load while preserving rule semantics. Its major goals are:
- Remove duplicate or fully shadowed rules.
- Combine similar rules into PF tables when enough addresses are present.
- Reorder rules inside safe semantic blocks to improve kernel skip-step behavior.
- Optionally use live rule counters to reorder `quick` rules by observed traffic.

## Core Concepts

### Superblocks

A `superblock` is a contiguous list of rules with compatible semantics. Rules inside a superblock may be reordered or combined without changing observable policy. Rules that cannot safely move become barriers or force a new block.

Each superblock contains:
- `sb_rules`: optimized rule list.
- `sb_profiled_block`: matched current-kernel rule block for profile-guided optimization.
- `sb_skipsteps[PF_SKIP_COUNT]`: skip-step grouping lists.

### pf_skip_step

`struct pf_skip_step` groups rules sharing a field used by PF skip steps, such as interface, direction, address family, protocol, source/destination address, or source/destination port. Reordering tries to put common groups adjacent.

### Rule Field Descriptor

`pf_rule_desc[]` classifies fields in `struct pfctl_rule`:
- `BARRIER`: nonzero field forces the rule into its own block.
- `BREAK`: field must match within a superblock.
- `NOMERGE`: may reorder but cannot differ for table-combine merging.
- `COMBINED`: field may be merged into generated tables.
- `DC`: ignored for comparisons, generally kernel counters or derived fields.
- `NEVER`: should not be set in pass/block rules.

Fields such as labels, probability, max states, source limits, and anchors are barriers. Action, logging, quickness, tags, queueing, NAT/RDR/route pools, and similar behavior-affecting fields are breaks.

## Main Optimization Flow

`pfctl_optimize_ruleset()`:
1. Returns immediately for an empty filter ruleset.
2. Initializes skip comparators and table generation state.
3. Moves active rules into the inactive list.
4. Copies each rule into `struct pf_opt_rule`, preserving pool lists.
5. Partitions the flat queue into superblocks with `construct_superblocks()`.
6. Optionally loads feedback profile data when `PF_OPTIMIZE_PROFILE` is enabled.
7. Optimizes each superblock with `optimize_superblock()`.
8. Rebuilds the active filter ruleset with new rule numbers.
9. Releases table references and temporary optimizer state.

On errors it frees outstanding optimizer queues and superblocks.

## Optimization Passes

`optimize_superblock()` runs passes in this order:
1. `remove_identical_rules()`
2. `combine_rules()`
3. profile-guided `block_feedback()` for quick rules when available, otherwise `reorder_rules()`

The comment explicitly says no passes should be added after `reorder_rules()` because it can split a superblock into smaller blocks.

## Duplicate And Superset Removal

`remove_identical_rules()` compares each pair of rules after:
- Reducing them with `comparable_rule(..., DC)`.
- Applying `exclude_supersets()` in both directions.

If one rule is identical to or covered by another, it removes the redundant rule.

`exclude_supersets()` normalizes a sub-rule when a super-rule has broader fields:
- Empty interface matches all interfaces.
- `PF_INOUT` covers direction.
- Protocol zero covers any protocol.
- Empty port operator covers ports.
- Zero netmask covers all source/destination addresses.
- Broader CIDR masks can cover narrower CIDR addresses.
- Address family zero covers any family.

## Combining Rules Into Tables

`combine_rules()` searches for rules that differ only in source or destination address and whose differing addresses can become table members.

Requirements:
- Table loading must be enabled in `pf->loadopt`.
- Only one side may differ at a time.
- The different address must be `PF_ADDR_ADDRMASK`.
- Port operators, port values, negation, and other non-combinable fields must match.
- `rules_combineable()` must succeed.

`TABLE_THRESHOLD` is 6. Before reaching the threshold, related rules keep references to the candidate table. Once the threshold is reached:
- A generated const table is created.
- One remaining rule is rewritten to reference that table.
- Duplicate covered rules are removed.
- Verbose mode prints the generated table definition.

`add_opt_table()` creates temporary optimizer tables and appends host nodes.

`pf_opt_create_table()` picks a collision-resistant generated table name using an `arc4random()` identifier and current global table list, then calls `pfctl_define_table()`.

## Reordering For Skip Steps

`reorder_rules()`:
1. Builds skip-step grouping lists for each comparator.
2. Ignores fields that either match all rules or match only one rule.
3. Finds the largest useful grouping.
4. Moves matching rules adjacent.
5. If the group is large enough, splits it into a new superblock and recurses.
6. Leaves unmatched rules in original order when no useful commonality remains.

Skip comparators:
- `skip_cmp_ifp`
- `skip_cmp_dir`
- `skip_cmp_af`
- `skip_cmp_proto`
- `skip_cmp_src_addr`
- `skip_cmp_dst_addr`
- `skip_cmp_src_port`
- `skip_cmp_dst_port`

`skip_init()` maps PF skip constants to comparator functions.

`remove_from_skipsteps()` maintains the skip-step lists after a rule is extracted.

## Profile-Guided Optimization

`load_feedback_profile()` fetches currently loaded pass rules from the kernel and partitions them into profiled superblocks. It tries to align current-kernel superblocks with the new superblocks using `BREAK`-level comparable rules.

`block_feedback()` copies packet counters from matching profiled rules to new rules, then sorts rules in descending profile count. This pass is only applied to suitable `quick` superblocks.

## Superblock Construction

`construct_superblocks()` walks the optimizer queue and starts a new superblock when `superblock_inclusive()` rejects the next rule.

`superblock_inclusive()` rejects inclusion when:
- A barrier field is nonzero.
- Per-rule source tracking is enabled.
- Interface groups differ in a way that could change runtime semantics.
- `NOMERGE`-level comparable rules differ from the first rule in the block.

The interface-group logic is intentionally conservative because group membership can change at runtime.

`interface_group()` uses `SIOCGIFGMEMB` to determine whether an interface name is a group.

## Comparison And Table Helpers

- `addrs_equal()` compares PF rule address wrappers.
- `addrs_combineable()` checks table-combine eligibility.
- `rules_combineable()` compares rules with `COMBINED` fields zeroed.
- `comparable_rule()` copies a rule and zeroes fields at or above a requested descriptor class.
- `pf_opt_table_ref()` / `pf_opt_table_unref()` manage optimizer table reference counts.

## Memory Management

The optimizer copies parsed rules into temporary `pf_opt_rule` nodes, moves pool lists carefully, and frees temporary tables through reference counting. `superblock_free()` recursively frees superblocks, profiled blocks, rule wrappers, and table references.

## Role In This Group

This file is a compact example of conservative source-to-source policy optimization. It balances performance improvements against the risk of changing firewall behavior by enforcing explicit semantic barriers and only transforming rules inside compatible contiguous blocks.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_optimize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_osfp.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_osfp.c

## Purpose

`pfctl_osfp.c` implements passive OS fingerprint management for pfctl. It parses fingerprint files, loads fingerprints into the kernel, imports active fingerprints from the kernel, maintains local name-to-ID trees, resolves fingerprint names used in rules, and prints fingerprint data.

It handles PF OS fingerprint identities as a hierarchy:
- class
- version
- subtype

## Data Structures

`struct name_entry` stores one class/version/subtype name:
- `nm_num`: numeric ID assigned for PF packing.
- `nm_name`: display/lookup name.
- `nm_sublist`: nested list for versions or subtypes.
- `nm_sublist_num`: next numeric ID within that sublist.

Global state:
- `classes`: root list of OS classes.
- `class_count`: assigned class count.
- `fingerprint_count`: total loaded/imported fingerprints.

## Loading Fingerprints From File

`pfctl_file_fingerprints()`:
1. Flushes pfctl’s local fingerprint view.
2. Opens the fingerprint file with `pfctl_fopen()`.
3. Clears kernel fingerprints unless in no-action mode.
4. Reads each line with `fgetln()`.
5. Removes comments and leading/trailing whitespace.
6. Parses colon-separated fields:
   - window size
   - TTL
   - don’t-fragment flag
   - packet size
   - TCP options
   - OS class
   - OS version
   - OS subtype
   - OS description
7. Parses TCP option signatures with `get_tcpopts()`.
8. Converts modifiers into `PF_OSFP_*` flags.
9. Adds the IPv4 fingerprint.
10. Also adds an IPv6-adjusted fingerprint by setting `PF_OSFP_INET6`, forcing DF, and adjusting packet size by the IPv6/IPv4 header size difference.

The parser accepts modifiers such as:
- `*`: don’t care
- `%`: modulus
- `S`: MSS multiple
- `T`: MTU multiple

## Kernel Operations

- `pfctl_clear_fingerprints()` calls `DIOCOSFPFLUSH`.
- `add_fingerprint()` calls `DIOCOSFPADD` unless in no-action mode.
- `pfctl_load_fingerprints()` repeatedly calls `DIOCOSFPGET` until `EBUSY` signals completion, importing each fingerprint locally.

There is also a `FAKE_PF_KERNEL` path where `pf_osfp_add()` is called directly instead of ioctl.

## Local Fingerprint Model

`pfctl_flush_my_fingerprints()` recursively frees the local class/version/subtype lists and resets counts.

`fingerprint_name_entry()` finds or creates a name in a list. Existing entries are moved to the front. Empty or null names return `NULL`, allowing version/subtype to be optional.

`import_fingerprint()` imports kernel-provided packed IDs and names into the local hierarchy while preserving maximum assigned numeric IDs.

`add_fingerprint()` assigns numeric IDs for class/version/subtype names, expands version/subtype ranges, packs them into `fp_os.fp_os`, increments the count, and loads the signature.

The range expansion macro accepts compact ranges like `1-4` or `2.2-2.6` and recursively creates one fingerprint per expanded value with `PF_OSFP_EXPANDED`.

The class name `nomatch` is reserved and rejected.

## Lookup By Name

`pfctl_get_fingerprint(name)` resolves rule syntax into a packed `pf_osfp_t`:
- `"unknown"` maps to `PF_OSFP_UNKNOWN`.
- A bare class name maps to class plus wildcard version/subtype.
- Otherwise it parses `class version subtype`.
- It supports fuzzy matching for version/subtype strings joined by `.`, space, tab, or `-`.

After packing, it unpacks again to detect overflow of class/version/subtype bit fields. If packing would collide with `PF_OSFP_ANY` or overflow, it returns `PF_OSFP_NOMATCH`.

## Lookup By ID

`pfctl_lookup_fingerprint(fp, buf, len)` converts a packed fingerprint ID back to text:
- `PF_OSFP_UNKNOWN` becomes `unknown`.
- `PF_OSFP_ANY` becomes `any`.
- Known class/version/subtype IDs are rebuilt as text.
- Missing or invalid IDs become `nomatch`.

The formatting preserves common version/subtype separators, using `.` when the version contains a dot and subtype begins with a digit.

## Listing And Sorting

`pfctl_show_fingerprints()`:
- In `-s all` mode, prints a section title and total fingerprint count.
- Otherwise prints a class/version/subtype table.

`sort_name_list()` recursively sorts each name list case-insensitively. The implementation is intentionally simple and slow, but fingerprint lists are small enough for that to be acceptable.

`print_name_list()` recursively prints the hierarchy with tab-separated prefixes.

## Parsing Helpers

`get_field()` returns the next colon-separated field from a line, trimming trailing whitespace.

`get_str()` copies the next field into allocated memory and enforces a minimum length.

`get_int()` parses integer fields with optional modifiers and max bounds, producing field-specific diagnostics with file and line number.

`get_tcpopts()` parses compact TCP option syntax:
- `N`: NOP
- `S`: SACK
- `T` or `T0`: timestamp, optionally zero timestamp
- `M`: MSS, with optional `*` or `%`
- `W`: window scale, with optional `*` or `%`

It packs options into `pf_tcpopts_t` using `PF_OSFP_TCPOPT_BITS` and returns MSS/window-scale values plus modifier flags.

`print_ioctl()` reconstructs a textual representation of a `pf_osfp_ioctl`, mainly for debug output.

## Role In This Group

`pfctl_osfp.c` is a specialized parser/loader for PF passive OS detection signatures. It complements the main rule loader by making OS fingerprint names available to rules and by synchronizing the userland name hierarchy with kernel fingerprint IDs.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_osfp.c -->