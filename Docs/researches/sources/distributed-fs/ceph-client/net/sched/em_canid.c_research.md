
# sources/distributed-fs/ceph-client/net/sched/em_canid.c

## Purpose

`em_canid.c` implements an extended match for CAN frames. It lets ematch-capable classifiers test the CAN identifier in an skb against a list of `struct can_filter` rules, optimized for standard 11-bit CAN identifiers and preserving full rule data for dumps and extended identifiers.

## Important APIs, Types, and Functions

`struct canid_match` stores a bitmap for all SFF IDs, counts for total/SFF/EFF rules, and a flexible raw rule array. `em_canid_change()` validates and compiles the user rule array. `em_canid_match()` reads the CAN id from `struct can_frame` data, uses the bitmap for SFF frames, and linearly scans EFF rules. `em_canid_dump()` emits raw rules. `em_canid_destroy()` frees compiled state. The module registers `TCF_EM_CANID`.

## Control Flow

Change rejects empty, misaligned, or more than 500 rules, allocates state plus raw rule storage, copies EFF rules first for a compact match loop, then copies SFF rules and expands each SFF mask into the bitmap. Match first ensures the skb has a full CAN frame. EFF frames compare against the EFF rule prefix; SFF frames mask to 11 bits and test one bitmap bit. Dump returns the original rule array order as stored in `rules_raw`.

## State and Persistence Behavior

Compiled state is per ematch instance and owned by `m->data`. The SFF bitmap is derived state; raw rules are persisted for EFF matching and netlink dump. There is no global state other than module registration.

## Dependencies and Integration Points

It depends on CAN frame layout from `<linux/can.h>`, ematch core registration, skb pull helpers, and netlink raw ematch payload handling. It is usable only where an ematch tree is attached by another classifier.

## Risks and Edge Cases

The code assumes CAN ID is at `skb->data` after ensuring `CAN_MTU`. SFF expansion can be expensive for broad masks but is bounded by 2048 IDs and 500 rules. Filters matching the same numeric id as SFF and EFF require separate rules due to SFF/EFF separation.

## Test Signals

Use SFF exact, SFF masked, all-SFF, EFF exact/masked, mixed rule, over-limit, misaligned length, dump, and inverted ematch tree tests.
