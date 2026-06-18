# sources/distributed-fs/ceph-client/net/sched/act_simple.c

## Purpose

`act_simple.c` is a small example tc action. It stores a user string, logs that string with the packet count whenever the action runs, and returns the configured tc control action.

## Important APIs, types, and functions

`tcf_simp_init()` parses `TCA_DEF_PARMS` and required `TCA_DEF_DATA`, allocates or replaces a `tcf_defact`, and validates the control action. `alloc_defdata()` allocates the fixed `SIMP_MAX_DATA` string buffer. `reset_policy()` updates existing actions. `tcf_simp_act()` updates lastuse and basic stats under `tcf_lock`, logs `simple: <data>_<packets>`, and returns `tcf_action`. `tcf_simp_dump()` serializes params, string, and timing.

## Control flow

Create requires a data string and action parameters. Existing actions require replace mode and rewrite the stored policy string under lock. Runtime is intentionally simple: lock, update stats, print, unlock, return.

## State and persistence

State is the common tc action plus a heap-allocated `tcfd_defdata` string of up to 32 bytes. Cleanup frees that string. Unlike many other actions in this group, it does not use RCU parameter replacement.

## Dependencies and integration points

It uses tc action IDR/per-net registration, netlink string parsing, kernel logging, and standard control-action handling. It serves mostly as an example and diagnostic action rather than a performance-focused datapath primitive.

## Risks and edge cases

The hot path takes a spinlock and emits `pr_info()` per packet, so it is unsuitable for high-rate production traffic. Missing data is rejected. Tests should be careful not to depend on unbounded kernel log availability.

## Test signals

Create, replace, dump, and delete the action; confirm the log includes the configured string and monotonically increasing packet count; verify missing `TCA_DEF_DATA` fails and configured control actions are returned.
