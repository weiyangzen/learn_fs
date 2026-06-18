# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_guc_g2g_test.c

## Purpose

`xe_guc_g2g_test.c` is a live KUnit suite for GuC-to-GuC (G2G) communication across GTs. It verifies message routing, payload integrity, sequence ordering, default driver CTB allocation, and alternate CTB placement in host or tile-local memory.

## Important APIs, Types, and Functions

- Payload and routing helpers: `struct g2g_test_payload`, `slot_index_from_gts`, `g2g_test_send`, and exported `xe_guc_g2g_test_notification`.
- Test loop: `g2g_test_in_order`, `g2g_wait_for_complete`, `g2g_run_test`, and `g2g_clean_array`.
- CTB lifecycle: `g2g_ct_stop`, `g2g_ctb_size`, `g2g_alloc_default`, `g2g_alloc_host`, `g2g_alloc_tile`, `g2g_distribute`, `g2g_free`, `g2g_stop`, and `g2g_reinit`.
- Flat CTB indexing/registering: `g2g_slot_flat`, `g2g_register_flat`, and `g2g_start`.
- Test entry points: `xe_live_guc_g2g_kunit_default` and `xe_live_guc_g2g_kunit_allmem`.

## Control Flow

The notification handler validates async G2H notification length, payload length, source/destination tile/device IDs, finds the transmitting GT, computes a slot index, checks the sequence number, updates the per-pair sequence array, and decrements an outstanding-message counter.

The main test allocates a `gt_count * gt_count` sequence array, sends increasing sequence numbers from every GT to every other GT, waits for each prior sequence before queueing the next message on the same route, waits for all notifications, and finally checks that identity slots remain zero and all cross-GT slots reached the final sequence. The all-memory test stops/recreates CTBs, runs the same traffic through default, host-backed, and per-tile local-memory CTB placements, then restores the original default CTBs through a KUnit cleanup action.

## State and Persistence Behavior

The test mutates live GuC G2G CTB registration state, `guc->g2g.bo` ownership/reference state, GGTT mappings, device `g2g_test_array`, and atomic outstanding notification counts. Runtime PM references and CTB recreation are registered as cleanup actions to restore the device.

## Dependencies and Integration Points

It depends on live Xe devices, GuC CT send APIs, GuC G2G registration/deregistration actions, managed BO pin/map, GGTT addresses, runtime PM, GuC firmware build type, and the production `xe_guc_g2g_wanted` policy. It only runs when there are at least two GTs and the firmware exposes the test interface.

## Risks and Edge Cases

- The notification handler cannot use aborting KUnit assertions because it runs asynchronously from the G2H notification path; failures must be logged and returned.
- The all-memory test deliberately recreates CTBs and can leave G2G communication broken if cleanup fails.
- Sequence waiting uses polling and bounded sleeps; overloaded systems or firmware latency can cause false timeouts.
- The flat slot-index math is duplicated from driver logic to force coverage of alternate placement schemes; drift between test and driver is both a risk and a signal that tests must be updated.

## Test Signals

Passing default tests show production G2G CTBs can route messages between GTs. Passing all-memory tests show host and local-memory CTB placements are reachable from all participating GuCs. Failures in payload IDs, sequence numbers, outstanding count, registration, or CTB cleanup are strong regressions in G2G transport.
