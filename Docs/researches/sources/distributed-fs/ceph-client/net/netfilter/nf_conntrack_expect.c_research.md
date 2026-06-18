# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_expect.c

## Purpose
`nf_conntrack_expect.c` manages conntrack expectations: temporary or permanent rules created by helpers to classify future related connections, such as FTP data channels or Amanda streams.

## Important APIs, Types, And Functions
Global state includes `nf_ct_expect_hash`, `nf_ct_expect_hsize`, `nf_ct_expect_max`, expectation slab cache, and siphash seed. Exported APIs include `nf_ct_expect_alloc()`, `nf_ct_expect_init()`, `nf_ct_expect_related_report()`, `nf_ct_expect_find_get()`, `nf_ct_find_expectation()`, `nf_ct_remove_expect()`, `nf_ct_remove_expectations()`, `nf_ct_unexpect_related()`, `nf_ct_unlink_expect_report()`, `nf_ct_expect_iterate_destroy()`, and `nf_ct_expect_iterate_net()`.

## Control Flow
Helpers allocate an expectation, initialize tuple/mask/net/zone/helper metadata, and submit it through `nf_ct_expect_related_report()`. Under `nf_conntrack_expect_lock`, the code checks for identical expectations, mask clashes, per-helper class limits, and global table limit. Successful insertion adds a timer reference, links into the master's expectation list and global hash, increments counts, and emits an event. Packet lookup calls `nf_ct_find_expectation()`, verifies the expectation is active, the master is confirmed and alive, gets a master reference, and either returns a permanent expectation or unlinks a one-shot expectation.

## State And Persistence
Expectations are in-memory, refcounted, RCU-freed objects. They are stored both in the global expectation hash and the master conntrack helper list. Timers expire non-permanent expectations. Per-net `expect_count` tracks global pressure.

## Dependencies And Integration Points
This file is used by conntrack helpers, conntrack core allocation for related flows, event cache reporting, procfs display, zones, net namespace proc setup, and the shared `nf_conntrack_expect_lock`.

## Risks
Expectation masks can be broad, so clash detection is critical. Master lifetime is subtle because unfulfilled expectations do not hold a master reference until matched. Timer deletion controls safe unlink. Permanent expectations are not one-shot and must be used carefully. Procfs iteration is RCU-based and netns-filtered.

## Test Signals
Test helper max_expected eviction, global table full, identical replacement, mask clash rejection, timeout expiry, permanent expectations, userspace/inactive flags in proc output, net namespace filtering, expected connection creation inheriting mark/secmark/master/helper, and cleanup when a master dies.
