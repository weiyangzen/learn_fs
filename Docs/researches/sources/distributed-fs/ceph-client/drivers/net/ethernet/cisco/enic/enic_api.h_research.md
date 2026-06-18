<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_api.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_api.h

## Purpose

`enic_api.h` declares the exported ENIC devcmd proxy API.

## Important APIs, Types, and Functions

It declares `enic_api_devcmd_proxy_by_index`, taking a netdev, VF index, devcmd enum, two command arguments, and a wait value.

## Control Flow

No executable flow exists in the header. It provides the prototype used by external or internal callers of the API implemented in `enic_api.c`.

## State and Persistence Behavior

The header stores no state. Call effects depend on the underlying devcmd issued by the implementation.

## Dependencies and Integration Points

It includes netdevice, `vnic_dev.h`, and `vnic_devcmd.h`, exposing ENIC's firmware command vocabulary to users of this API.

## Risks and Edge Cases

The prototype exposes raw devcmd arguments, so ABI users must understand firmware command semantics and locking expectations. Header/API drift would break module builds.

## Test Signals

Compile external users against this header and exercise command proxy success, failure, and reset-concurrency behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_api.h -->
