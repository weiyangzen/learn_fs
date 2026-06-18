# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/matcher.c

## Purpose
`matcher.c` implements HWS matcher and match-template lifecycle. A matcher owns match definers, action template processing, STE ranges, RTC objects, end flow-table anchors, collision matchers, priority-chain wiring, isolated matcher wiring, dynamic action-template attachment, and resize target setup. It is the table-level orchestration layer between PRM match/action templates and rule insertion.

## Important APIs, types, and functions
Public functions are `mlx5hws_matcher_create()`, `mlx5hws_matcher_destroy()`, `mlx5hws_match_template_create()`, `mlx5hws_match_template_destroy()`, `mlx5hws_matcher_attach_at()`, `mlx5hws_matcher_resize_set_target()`, `mlx5hws_matcher_resize_rule_move()`, and `mlx5hws_matcher_update_end_ft_isolated()`.

Core internal groups include attribute processing (`hws_matcher_process_attr()`, `hws_matcher_validate_insert_mode()`, `hws_matcher_check_attr_sz()`), template binding (`hws_matcher_bind_mt()`, `hws_matcher_bind_at()`), object allocation (`hws_matcher_create_end_ft()`, `hws_matcher_create_rtc()`), chain manipulation (`hws_matcher_connect()`, `hws_matcher_disconnect()` and isolated variants), collision matcher handling, and resize validation.

## Control flow
Creation allocates a matcher, copies attributes, validates insert/distribute/resource modes against device caps, converts rule-count sizing into hash-table dimensions when needed, sets resizable/isolated flags, copies match and action templates, and enters `hws_matcher_init()` under the context control lock. Initialization binds match templates by creating definers and RX/TX STE ranges, processes action templates into setters and calculates the maximum number of action STEs, creates an end flow table, creates RX and TX RTCs, connects the matcher into the table's priority list, and optionally creates a collision matcher for large hash tables.

For non-isolated tables, connection inserts the matcher by priority, points the new matcher's end FT to the next matcher or default miss table, points the previous FT or table start FT to the new matcher's RTCs, resets default miss refcounts, and updates connected miss tables when the first matcher changes. Isolated tables use a special chain where matcher end FTs point back to the complex matcher's end FT and the start FT or previous isolated end FT points at the current match RTCs. Destruction reverses the process under the control lock: destroy collision matcher, disconnect from the chain, destroy RTCs, destroy end FT, unbind STE ranges and definers, free template arrays, and free the matcher.

RTC creation configures hash, hash-split, or linear lookup modes based on insert and distribute mode. It sets match definer IDs, access/update index mode, PD, STE base, STC base, table type, reparse mode, miss FT, and mirrored TX RTC for FDB tables. Optimization by flow source can allocate zero-sized RX or TX resources.

Resize setup validates source and destination table type, resizable flags, insert mode, no existing resize, equal number of match templates, sufficient action STE capacity, and equivalent definers. It then records `src_matcher->resize_dst`. Rule moves are delegated to `mlx5hws_rule_move_hws_add()`.

## State and persistence behavior
Matchers persist in `tbl->matchers_list` and own firmware resources: STE ranges, RTCs, end FTs, and definer references. Collision matchers share copied template arrays with the parent but own their own resources. Runtime matcher state includes IP-version match flags and learned IP version constraints, resize destination pointer, and maximum action STE count. Match templates own copied PRM masks until destroyed.

## Dependencies and integration points
`matcher.c` depends on command helpers for RTC/STE allocation, table FT wiring helpers, definer initialization/comparison, action template processing and validation, context capabilities, action STE sizing, rule move helpers, and Linux list/mutex primitives. It is called by the public HWS API and by BWC wrappers used from `fs_hws.c`.

## Risks and edge cases
Flow-table chain rewiring is high risk: a failed connect/disconnect can leave miss paths or priority ordering wrong. Isolated matcher logic has multiple first/last/collision/rehash cases. RTC sizing must honor caps and avoid invalid zero-sized resources except for explicit flow-source optimization. Collision matcher sizing uses a fixed assured ratio and depth; wrong thresholds affect insertion success. Dynamic AT attachment grows arrays and mirrors the count into collision matchers, so array capacity and processed setters must remain consistent. Resize requires equivalent definers; skipping checks could move rules into incompatible hardware layout.

## Test signals
Test matcher create/destroy across hash, insert-by-index hash-split, and linear lookup modes; invalid cap combinations; priority insertion before/middle/after; default miss updates; isolated matcher first/last/collision cases; large-rule collision matcher creation; dynamic action-template attachment; resizable matcher creation and target setup; resize rejection for incompatible templates; and failure injection at definer, STE, end FT, RTC, and connect stages.
