# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi10_ip_offset.h

## Purpose

`navi10_ip_offset.h` is a generated AMDGPU ASIC address-map header for Navi 10/DCN 2.0 class hardware. It does not implement behavior; it publishes immutable base offsets for hardware IP blocks so display and SOC15 register-access code can translate block-relative register offsets into concrete MMIO addresses.

The file is guarded by `_navi10_ip_offset_HEADER`, defines `MAX_INSTANCE` as 6 and `MAX_SEGMENT` as 6, then provides both structured `IP_BASE` tables and flattened `*_BASE__INSTn_SEGm` macros. The source is data-only but high impact because these constants decide which hardware block a register read or write reaches.

## Important APIs, Types, And Data

The public C data model is:

- `struct IP_BASE_INSTANCE`, containing `unsigned int segment[MAX_SEGMENT]`.
- `struct IP_BASE`, containing `struct IP_BASE_INSTANCE instance[MAX_INSTANCE]`, marked `__maybe_unused` so generated constants can be included by multiple consumers without warnings.

The static `IP_BASE` tables describe Navi 10 block bases for `ATHUB_BASE`, `CLK_BASE`, `DF_BASE`, `DCN_BASE`, `FUSE_BASE`, `GC_BASE`, `HDP_BASE`, `MMHUB_BASE`, `MP0_BASE`, `MP1_BASE`, `NBIO_BASE`, `OSSSYS_BASE`, `RSMU_BASE`, `SMUIO_BASE`, `THM_BASE`, `UMC_BASE`, and `VCN_BASE`. The data is mostly instance 0 with zero-filled unused instances. Notable populated segment groups include `CLK_BASE` with six segment offsets, `DCN_BASE` with four display offsets, `GC_BASE` with two graphics/SDMA-facing offsets, `NBIO_BASE` with four NBIO segments, `SMUIO_BASE` with two segments, and `VCN_BASE` with two codec segments.

Every table is mirrored by macro constants like `DCN_BASE__INST0_SEG0`, `CLK_BASE__INST0_SEG5`, or `VCN_BASE__INST0_SEG1`. These macros are useful for register list initializers or preprocessor-style access patterns where the structured table is not used directly.

## Control Flow

There is no runtime control flow in this header. The effective flow is inclusion-time:

1. A Navi 10 display component includes the header.
2. Code chooses an IP table or flattened macro for the relevant hardware block.
3. Register access helpers combine a base segment with a block-local register offset.
4. The resulting MMIO address is read, written, polled, or added to a register list.

Direct includes in this tree include DCN 2.0 resource, GPIO, IRQ, and clock manager code: `display/dc/resource/dcn20/dcn20_resource.c`, `display/dc/gpio/dcn20/hw_factory_dcn20.c`, `display/dc/irq/dcn20/irq_service_dcn20.c`, and `display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`.

## State And Persistence Behavior

The header stores immutable compile-time data. It owns no runtime state, no locks, no allocation, and no persistence path. The stateful effect occurs in consumers: once these constants are compiled into the driver, display and power-management code use them to access persistent hardware registers until reset, suspend/resume reinitialization, or module unload.

Because the constants become part of the kernel image, a wrong base address persists as a driver-hardware ABI error for every Navi 10 device using that code path.

## Dependencies

The file depends on kernel/compiler definitions for `__maybe_unused` and on AMDGPU/SOC15 register access conventions that interpret IP block bases and segment indices. It is intended to be included with generation-specific register offset and mask headers under `include/asic_reg/`, plus display code that knows the Navi 10/DCN 2.0 hardware layout.

It shares generic names such as `struct IP_BASE` and `ATHUB_BASE` with other ASIC offset headers. Consumers normally include one ASIC offset header per translation unit to avoid symbol/name collisions.

## Integration Points

Primary integration is with the DCN 2.0 display stack: resource construction, GPIO factory setup, IRQ service registration, and clock manager SMU/register access. The `DCN_BASE`, `CLK_BASE`, `MP0_BASE`, `MP1_BASE`, `SMUIO_BASE`, `THM_BASE`, and `VCN_BASE` entries are especially relevant to display bring-up, clock/thermal programming, and multimedia/display block access.

The header also aligns with sibling ASIC offset headers such as `navi12_ip_offset.h`, `navi14_ip_offset.h`, and `renoir_ip_offset.h`. Shared display code assumes the table/macro naming scheme is stable while each ASIC-specific file supplies the correct address map.

## Risks

The main risk is silent MMIO misaddressing. A single incorrect populated segment can make a valid register macro access the wrong hardware aperture, causing display bring-up failures, clock programming errors, interrupt issues, or hard-to-debug hangs while polling status bits.

Zero-filled entries are ambiguous unless the caller knows the hardware map. Zero can mean an absent instance/segment, but some blocks legitimately start near low offsets. Code must rely on the known table shape rather than scanning for nonzero values without context.

The generic symbol names create compile-time collision risk if more than one `*_ip_offset.h` file is included into the same C file. Changes to `MAX_INSTANCE` or `MAX_SEGMENT` are also risky because consumers and generated macro sets assume the exact instance/segment cardinality.

## Test Signals

Strong signals are successful build coverage of all DCN 2.0 consumers, followed by hardware probe on Navi 10 with display enabled. Runtime validation should include DCN resource creation, display modeset, GPIO/DDC detection, IRQ delivery, clock manager initialization, suspend/resume, and register dumps that confirm known DCN, CLK, SMUIO, THM, VCN, and NBIO addresses resolve as expected.

Failures commonly surface as MMIO read/write faults, timeouts while polling display or SMU registers, missing hotplug/IRQ events, bad clock reporting, or display modeset failures.
