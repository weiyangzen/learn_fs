# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi12_ip_offset.h

## Purpose

`navi12_ip_offset.h` is a generated AMDGPU IP base-offset table for Navi 12 hardware. It gives the driver a compile-time map from hardware IP block, instance, and segment to MMIO base addresses. Like the other `*_ip_offset.h` files, it contains no executable logic; its purpose is to make register offset composition deterministic for ASIC-specific display and SOC15 code.

The file uses `_navi12_ip_offset_HEADER`, `MAX_INSTANCE` 7, and `MAX_SEGMENT` 5. The larger instance count and different segment count distinguish it from Navi 10 and reflect Navi 12's generated address map.

## Important APIs, Types, And Data

The exported types are the same generated pair used by sibling files:

- `struct IP_BASE_INSTANCE { unsigned int segment[MAX_SEGMENT]; }`
- `struct IP_BASE { struct IP_BASE_INSTANCE instance[MAX_INSTANCE]; } __maybe_unused`

The static base tables cover `ATHUB_BASE`, `CLK_BASE`, `DF_BASE`, `DIO_BASE`, `DMU_BASE`, `DPCS_BASE`, `FUSE_BASE`, `GC_BASE`, `HDA_BASE`, `HDP_BASE`, `MMHUB_BASE`, `MP0_BASE`, `MP1_BASE`, `NBIF0_BASE`, `OSSSYS_BASE`, `PCIE0_BASE`, `SDMA_BASE`, `SMUIO_BASE`, `THM_BASE`, `UMC_BASE`, `USB0_BASE`, and `UVD0_BASE`.

The flattened macro API follows `BLOCK_BASE__INSTn_SEGm`. Navi 12 has several nontrivial mappings: `CLK_BASE` has populated offsets across instances 0 through 5, `MP0_BASE` and `MP1_BASE` use distinct firmware/management apertures, `NBIF0_BASE` and `PCIE0_BASE` are separate tables, `SDMA_BASE` has populated values for instance 0 and instance 1, and `UMC_BASE` has four populated memory-controller instances. Display-related `DMU_BASE` and `DPCS_BASE` share the same populated segment list.

## Control Flow

There are no functions, branches, callbacks, or initialization routines in this file. Consumers include the header and use the constants during register-address calculation. The operational flow is:

1. ASIC-specific code selects the Navi 12 address-map header.
2. Register helper macros or register-list initializers reference `*_BASE` tables or `*_BASE__INSTn_SEGm` macros.
3. The selected segment base is added to a register-local offset.
4. The computed MMIO address is used for hardware programming, polling, or diagnostics.

Unlike `navi10_ip_offset.h` and `renoir_ip_offset.h`, a direct include of `navi12_ip_offset.h` was not found under `drivers/gpu/drm/amd` in this snapshot. That suggests it is either retained as generated ASIC data for conditional/out-of-tree users, included through build variants not present in the searched files, or available for future/partial Navi 12 enablement.

## State And Persistence Behavior

The file contributes immutable constants compiled into any consumer. It has no mutable software state and no persistence. The hardware state affected by consumers is persistent MMIO state: display, clock, PCIe/NBIF, firmware-management, SDMA, UVD, USB/HDA, and memory-controller registers remain programmed until reset, power gating, suspend/resume, or driver teardown.

If a consumer starts using this header, the constants become part of the runtime hardware ABI for Navi 12.

## Dependencies

The only syntactic dependency is the kernel's `__maybe_unused` annotation. Practical dependencies are AMDGPU SOC15/MMIO register helper conventions, matching register offset/mask headers for the hardware blocks being addressed, and ASIC selection logic that ensures this Navi 12 map is not used on a different GPU.

The file shares global names such as `CLK_BASE`, `GC_BASE`, and `struct IP_BASE` with other ASIC headers, so it should not be mixed with sibling `*_ip_offset.h` headers in one translation unit.

## Integration Points

Potential integration points are Navi-family display resource code, GPIO/IRQ setup, SMU/clock code, SDMA and memory-controller setup, and register dump tooling. The table contents line up with the broader AMDGPU generated-register scheme: `NBIF0_BASE`/`PCIE0_BASE` for bus registers, `DMU_BASE`/`DPCS_BASE`/`DIO_BASE` for display, `MP0_BASE`/`MP1_BASE` for management processors, and `UVD0_BASE`/`SDMA_BASE` for media and DMA engines.

The lack of direct in-tree includes is itself an integration signal: changes here may not be compile-tested unless a specific Navi 12 path includes it or broader generated-header validation is run.

## Risks

Address-map errors can compile cleanly and fail only on hardware. Incorrect `MP0_BASE` or `MP1_BASE` values can break firmware mailbox or SMU interactions; bad `PCIE0_BASE` or `NBIF0_BASE` values can corrupt bus configuration; wrong `DMU_BASE`/`DPCS_BASE` values can break display timing or link programming; incorrect `UMC_BASE` instances can affect memory-controller diagnostics or RAS flows.

Because no direct consumer was found, drift risk is higher: the file may not receive normal compile or boot coverage. The generated table must remain synchronized with hardware documentation and with any code that eventually selects it.

## Test Signals

Best signals are a build target that includes this header, static checks for duplicate `struct IP_BASE` inclusion conflicts, and Navi 12 hardware smoke tests. Runtime signals should include successful GPU probe, register readback sanity for each populated block, display modeset, clock/SMU initialization, SDMA ring tests, UVD/media ring tests, PCIe/NBIF diagnostics, suspend/resume, and memory-controller/RAS readouts where applicable.

For a currently unused header, a useful guard is generated-data comparison against the authoritative register database plus a compile-only consumer that verifies the table and macro names remain valid.
