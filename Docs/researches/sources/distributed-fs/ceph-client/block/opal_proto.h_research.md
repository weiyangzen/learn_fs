<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/opal_proto.h -->
# sources/distributed-fs/ceph-client/block/opal_proto.h

## Purpose
`opal_proto.h` defines constants, token IDs, UIDs, method IDs, packet headers, and Discovery 0 feature descriptor structs for TCG Opal self-encrypting drive support. It is a protocol description header consumed by the Opal implementation, primarily `sed-opal.c`.

## Important APIs, Types, and Functions
There are no functions. Important definitions include:
- Security protocol IDs `TCG_SECP_00..02`, generic session numbers, discovery COMID, and TPer/locking feature masks.
- Atom encoding masks and token bytes for tiny/short/medium/long/empty atoms.
- `enum opal_uid`, `enum opal_method`, `enum opal_token`, `enum opal_lockingstate`, `enum opal_parameter`, and `enum opal_revertlsp`.
- Packet structures: `opal_compacket`, `opal_packet`, `opal_data_subpacket`, `opal_header`, `opal_stack_reset`, and `opal_stack_reset_response`.
- Discovery feature descriptors: `d0_header`, `d0_tper_features`, `d0_locking_features`, `d0_geometry_features`, `d0_enterprise_ssc`, `d0_opal_v100`, `d0_single_user_mode`, `d0_datastore_table`, `d0_opal_v200`, and `d0_features`.

## Control Flow
This header does not execute code. Its layout controls how the Opal command layer builds and parses SECURITY PROTOCOL IN/OUT payloads, indexes static UID/method arrays, interprets method status and token streams, and walks variable-length Discovery 0 feature descriptors.

## State and Persistence Behavior
The header itself has no mutable state. The protocol entities it describes affect persistent drive security state such as locking ranges, MBR shadowing, user/admin PINs, generated keys, revert behavior, and datastore tables. Endianness annotations (`__be*`) are part of the state contract for on-wire parsing.

## Dependencies and Integration Points
It depends on `<linux/types.h>` and Linux endian integer typedefs. The main integration is with TCG Opal SED management and block crypto/security ioctl flows that eventually send Opal commands to storage devices.

## Risks and Edge Cases
Struct layout and endian annotations are ABI-critical for device interoperability. Optional fields and bit-packed descriptors require exact offsets. Enum indices must match companion UID/method arrays; inserting values can break lookups. Atom masks and response token IDs are protocol-sensitive and difficult to test without real or emulated Opal devices.

## Test Signals
Useful checks include compile-time layout assertions in consumers, Opal discovery parsing tests against captured device payloads, security protocol command tests on real SEDs, endianness tests on big-endian builds, and regression tests for UID/method array index consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/opal_proto.h -->
