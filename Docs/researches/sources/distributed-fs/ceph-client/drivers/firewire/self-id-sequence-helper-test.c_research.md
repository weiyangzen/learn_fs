# sources/distributed-fs/ceph-client/drivers/firewire/self-id-sequence-helper-test.c

## Purpose
Provides KUnit coverage for FireWire self-ID sequence helper routines defined through `phy-packet-definitions.h`. It verifies sequence enumeration, malformed sequence detection, port-capacity calculation, port-status extraction, and port-status rewriting.

## APIs, Types, And Functions
The tests exercise `struct self_id_sequence_enumerator`, `self_id_sequence_enumerator_next()`, `self_id_sequence_get_port_capacity()`, `self_id_sequence_get_port_status()`, and `self_id_sequence_set_port_status()`. The expected status values use `enum phy_packet_self_id_port_status` values for child, parent, not-connected, and none.

## Control Flow
`test_self_id_sequence_enumerator_valid()` feeds a mixed sequence of primary and extended self-ID quadlets and verifies that each call advances the cursor and remaining quadlet count correctly, ending with `-ENODATA`. `test_self_id_sequence_enumerator_invalid()` checks that an incomplete extended sequence yields `-EPROTO`. `test_self_id_sequence_get_port_status()` reads 28 possible port slots, including one out-of-range slot, mirrors them into mutable quadlets with `self_id_sequence_set_port_status()`, and asserts that the reconstructed quadlets match the expected encoded sequence.

## State, Persistence, And Dependencies
State is local to KUnit stack/static arrays. There is no persistence or external device dependency. The file depends on KUnit and the FireWire PHY packet helper header.

## Integration Points
The test suite is registered as `self-id-sequence-helper` with `kunit_test_suite()`, so it participates in the FireWire KUnit configuration and kernel test runner.

## Risks And Test Signals
The tests protect bit-field layout and iterator edge cases used by topology/self-ID parsing. Gaps include broader malformed sequences and randomized port layouts. A passing KUnit suite is the direct test signal.
