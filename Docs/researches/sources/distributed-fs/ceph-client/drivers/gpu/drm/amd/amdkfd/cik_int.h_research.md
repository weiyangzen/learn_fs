# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cik_int.h

## Purpose
`cik_int.h` defines the CIK interrupt-ring entry layout and source IDs used by AMDKFD CIK interrupt processing.

## Important APIs, Types, And Functions
The main type is `struct cik_ih_ring_entry`, containing `source_id`, `data`, `ring_id`, and `reserved` dwords. Defined source IDs include CP end-of-pipe, CP bad opcode, SDMA trap, SQ interrupt message, GFX page invalid fault, and GFX memory protection fault.

## Control Flow
There is no direct control flow. `cik_event_interrupt.c` casts raw IH ring-entry dwords to this structure, decodes `source_id`, and extracts VMID/PASID from `ring_id`.

## State And Persistence
The header owns no state. It describes the binary interrupt payload format persisted in the GPU IH ring until software consumes it.

## Dependencies And Integration Points
It includes `<linux/types.h>` for fixed-width integer types and is consumed by CIK interrupt/event code. Its constants must match CIK hardware firmware interrupt source encodings.

## Risks
Structure layout and source IDs are ABI-like hardware contracts. Any packing, field order, or constant mistake causes interrupts to be misclassified. Because users cast from raw `uint32_t *`, alignment and size assumptions must remain four dwords.

## Test Signals
Compile coverage plus runtime interrupt tests are needed. Expected signals include correct event delivery for all listed sources, correct VMID/PASID extraction from `ring_id`, and no bad-opcode or VM fault misclassification.
