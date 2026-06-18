# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/sienna_cichlid_ip_offset.h

## Purpose

`sienna_cichlid_ip_offset.h` is a generated-style AMDGPU/DC register-base map for the Sienna Cichlid ASIC family. It gives consumers two equivalent ways to reach hardware block base addresses:

- typed static tables, `static const struct IP_BASE <BLOCK>_BASE`, indexed as instance then segment;
- preprocessor constants named `<BLOCK>_BASE__INST<n>_SEG<m>`, usable inside register-list macros.

The file is not executable logic. Its job is to make register address construction deterministic for display, DMUB, GPIO, IRQ, clock manager, and related DCN 3.0 code that combines a block base with generated register offsets such as `mm...` and `..._BASE_IDX`.

## Important APIs, Types, And Constants

- `MAX_INSTANCE` is `7`; every `IP_BASE` table contains seven instance rows.
- `MAX_SEGMENT` is `5`; every instance row contains five segment slots.
- `struct IP_BASE_INSTANCE` wraps `unsigned int segment[MAX_SEGMENT]`.
- `struct IP_BASE` wraps `struct IP_BASE_INSTANCE instance[MAX_INSTANCE]` and is annotated `__maybe_unused`, which is useful because inclusion sites often consume only macro constants.
- Static block tables are provided for `ATHUB`, `CLK`, `DF`, `DIO`, `DCN`, `DPCS`, `FUSE`, `GC`, `HDA`, `HDP`, `MMHUB`, `MP0`, `MP1`, `NBIO`, `OSSSYS`, `PCIE0`, `SDMA0`, `SDMA1`, `SMUIO`, `THM`, `UMC`, `USB0`, and `VCN`.
- The macro matrix covers the same block names for all seven instances and five segments, yielding 805 `<BLOCK>_BASE__INST<n>_SEG<m>` definitions.

Notable populated ranges include multi-segment DCN/DPCS display bases, five-segment MP0/MP1/NBIO/PCIE0 bases, seven UMC instance rows, seven CLK instance rows, and two populated VCN instance rows. Zero values are meaningful sentinels for absent instances or absent segment slots, not dynamically discovered data.

## Control Flow And Data Flow

There is no function-level control flow. At compile time, include sites expand `BASE_INNER(seg)` or similar macros into constants such as `DCN_BASE__INST0_SEG4`; then generated register macros add generated register offsets:

- `BASE(mmREG_BASE_IDX) + mmREG` in DCN display code;
- static register tables, for example clock-manager register initializers, storing absolute SOC15-style register offsets;
- GPIO translation switch cases matching the same computed offsets.

Where the static `IP_BASE` tables are used, consumers can assign `adev->reg_offset[<HWIP>][instance]` to the address of a table instance, then later index `[base_idx]` while constructing register accesses. This repo shows that pattern in neighboring ASIC offset headers and AMGPU register-init paths, while Sienna Cichlid include sites in this checkout are primarily DC display and DMUB files that include the header directly and use the macro constants.

## State And Persistence Behavior

The file stores immutable compile-time constants only. It does not allocate memory, mutate driver state, persist device state, or read hardware. Its values become part of compiled driver code and indirectly influence runtime register access addresses. The only "state" is the static read-only data emitted into each translation unit that references the tables or macros.

## Dependencies

- Depends on a kernel build environment that defines `__maybe_unused`; the header itself does not include the defining header.
- Must match generated block register headers such as `dcn/dcn_3_0_0_offset.h`, `dpcs/dpcs_3_0_0_offset.h`, `mmhub/mmhub_2_0_0_offset.h`, and `nbio/nbio_7_4_offset.h`, because their `_BASE_IDX` values select segment indexes from this file.
- Included by DCN/DMUB Sienna Cichlid paths including `display/dmub/src/dmub_dcn30.c`, `display/dmub/src/dmub_dcn303.c`, `display/dc/irq/dcn30/irq_service_dcn30.c`, `display/dc/irq/dcn303/irq_service_dcn303.c`, `display/dc/gpio/dcn30/hw_translate_dcn30.c`, `display/dc/gpio/dcn30/hw_factory_dcn30.c`, `display/dc/resource/dcn30/dcn30_resource.c`, `display/dc/resource/dcn303/dcn303_resource.c`, and `display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`.
- Conceptually depends on AMDGPU hardware-IP identifiers from `soc15_hw_ip.h` when table-based offsets are attached to `adev->reg_offset[HWIP][instance]`.

## Integration Points

The main integration point is address construction for register reads/writes in AMD display and graphics code. For example, DCN code defines `BASE_INNER(seg) DCN_BASE__INST0_SEG ## seg`, then defines `REG(reg_name)` as `BASE(mm ## reg_name ## _BASE_IDX) + mm ## reg_name`. This makes the generated register offset headers hardware-family-specific without changing each register user.

The static tables align with `struct amdgpu_device::reg_offset[MAX_HWIP][HWIP_MAX_INSTANCE]`, whose entries are later consumed by SOC15 register helpers in `amdgpu/soc15_common.h`. The exact block names must therefore stay consistent with HWIP names and register base-index macros.

## Risks And Edge Cases

- Wrong segment values cause silent register misaddressing: reads and writes compile and run but target the wrong MMIO location.
- The `MAX_SEGMENT` width must be compatible with every `_BASE_IDX` used by included generated register headers. A new base index above 4 would become an out-of-bounds table access in table consumers or an undefined macro in macro consumers.
- Zero is overloaded as a valid base for some hardware ranges and as "not present" for most unused instance/segment cells. Consumers cannot infer presence from nonzero alone unless the relevant block's address map makes zero impossible.
- The struct names `IP_BASE_INSTANCE` and `IP_BASE` are generic and repeated by other generated offset headers. Include ordering must avoid including two incompatible generated offset headers with the same guard-disabled type names in one translation unit.
- Since the static tables live in a header, any non-`static` conversion would create multiple-definition link errors. Keeping them `static const` is required for header inclusion.

## Test Signals

- Build coverage from all DCN/DMUB translation units that include this header is the first signal: missing macros, bad type definitions, or conflicting generated headers fail compilation.
- Runtime display smoke tests are important: modeset, HPD, GPIO, clock manager, IRQ, and DMUB initialization paths exercise the computed register addresses.
- Register access tracing or debugfs reads can validate that DCN, DPCS, MMHUB, NBIO, and SMUIO addresses match Sienna Cichlid hardware documentation.
- Regression signals include blank display, hotplug failure, interrupt storms or missing vblank/pageflip interrupts, SMU/clock-manager failures, and GPU hangs during display bring-up.
