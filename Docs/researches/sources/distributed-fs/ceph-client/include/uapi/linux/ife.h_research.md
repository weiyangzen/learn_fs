
# sources/distributed-fs/ceph-client/include/uapi/linux/ife.h

## Purpose

`ife.h` defines the UAPI metadata IDs for Intermediate Functional Block Encapsulation metadata. The complete 19-line file was read.

## Important APIs, Types, and Functions

It defines `IFE_METAHDRLEN`, enum metadata IDs `IFE_META_SKBMARK`, `IFE_META_HASHID`, `IFE_META_PRIO`, `IFE_META_QMAP`, `IFE_META_TCINDEX`, and `IFE_META_MAX`.

## Control Flow

No code flow exists. Traffic-control IFE code uses these IDs to encode and decode skb metadata carried with encapsulated packets.

## State and Persistence Behavior

No state is stored here. IFE metadata values come from skb fields and tc action configuration at packet-processing time.

## Dependencies and Integration Points

The header has no includes and integrates with Linux traffic control actions and classifiers that manipulate skb mark/hash/priority/queue mapping/tc index metadata.

## Risks and Edge Cases

Metadata ID renumbering would break tc/user-space decoders. Runtime override of max metadata by module option means consumers should not assume every ID is always accepted.

## Test Signals

tc IFE tests should encode/decode each metadata type, verify max-ID handling, and check behavior when module options restrict supported metadata.
