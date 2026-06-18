<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/adreno-smmu-priv.h -->
# sources/distributed-fs/ceph-client/include/linux/adreno-smmu-priv.h

## Purpose
`adreno-smmu-priv.h` defines the private coordination interface between the Adreno GPU driver and the Adreno-specific ARM SMMU integration.

## Important APIs, types, and functions
`struct adreno_smmu_fault_info` carries fault address, TTBR0, context ID, fault status, syndrome registers, and CBFRSYNRA. `struct adreno_smmu_priv` contains an opaque cookie plus callbacks to get TTBR1 config, set/disable TTBR0 config, fetch fault info, control stall-on-fault, resume translation, and optional PRR bit/address configuration.

## Control flow
When the GPU driver attaches a domain, the SMMU side provides this callback table. GPU context-switch and fault paths call into it to update translation context, inspect faults, stall/resume translation, and configure partially resident region features.

## State and persistence behavior
The cookie points to SMMU-owned state. Callback effects persist in SMMU context-bank registers and GPU translation behavior until changed again.

## Dependencies and integration points
It depends on `io-pgtable` configuration types and physical addresses. Integration is intentionally private to DRM/MSM Adreno GPU and the Adreno SMMU driver.

## Risks and test signals
Risks include callback NULL handling, stale cookie lifetime, register state races during GPU faults/context switches, and PRR optional callbacks being assumed present. Test signals include GPU page fault diagnostics, context-switch stress, stall/resume tests, and attach/detach lifetime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/adreno-smmu-priv.h -->
