<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_dev_api.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_dev_api.h

## Purpose

Defines the PVRDMA guest-host device ABI: supported versions, PCI resource IDs, MMIO registers, shared region layout, capabilities, command opcodes, command payloads, event queue elements, and response payloads.

## Important APIs, Types, And Functions

Key version constants are `PVRDMA_ROCEV1_VERSION`, `PVRDMA_ROCEV2_VERSION`, `PVRDMA_PPN64_VERSION`, `PVRDMA_QPHANDLE_VERSION`, and `PVRDMA_VERSION`. Page-directory macros define a two-level directory with up to `PVRDMA_PAGE_DIR_MAX_PAGES`. `struct pvrdma_device_shared_region` carries driver version, guest OS info, command/response DMA addresses, async/CQ ring page directories, UAR PFN, and device capabilities. Command structs cover query port/pkey, create/destroy user context, PD, MR, CQ, SRQ, QP, and GID bindings.

## Control Flow

Probe allocates and fills the shared region, writes its physical address to registers, and the device fills capabilities. Verbs code populates command structs and expects matching response ack values. Event interrupt handlers consume `pvrdma_eqe` and `pvrdma_cqne` records from shared rings.

## State And Persistence Behavior

This file defines the memory layout of persistent shared state between guest driver and paravirtual device. The shared region and command slots live for the PCI device lifetime. Command structs are transient but ABI-stable within version gates.

## Dependencies And Integration Points

Includes Linux types and `pvrdma_verbs.h`. All PVRDMA implementation files depend on these definitions, and the hypervisor/device backend must implement the same ABI.

## Risks And Edge Cases

Packed shared-region layout, version gates, and response struct sizes are ABI-sensitive. Any incompatible field reorder or enum renumbering breaks host/guest communication. `PVRDMA_SUPPORTED()` currently accepts RoCE v1 or v2 modes only; future iWARP/IB modes would need explicit expansion.

## Test Signals

ABI tests should assert struct sizes/offsets, command union sizes, version-gated UAR PFN behavior, QP handle v2 response behavior, supported/unsupported device mode detection, and command response ack matching.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_dev_api.h -->
