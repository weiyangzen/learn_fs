# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_0_3_offset.h

## Purpose

`dpcs_2_0_3_offset.h` is a generated AMD display PHY control/status register offset header for the DPCS 2.0.3 register block used by the DCN 2.0.1 resource path. It defines symbolic MMIO register offsets and `_BASE_IDX` selectors for two transmitter instances, `DPCSTX0`/`RDPCSTX0` and `DPCSTX1`/`RDPCSTX1`. The direct `DPCSTX` block covers transmit-side clock, FIFO/control, CBUS, interrupt, and PLL update registers. The `RDPCSTX` block covers reduced/display PHY control, clocking, interrupt status, PLL update data, CR address/data access, scratch, and `RDPCSTX_PHY_CNTL0` through `RDPCSTX_PHY_CNTL14`.

The header carries no executable logic. Its purpose is to provide a stable hardware-address contract to the AMD display driver. `dcn201_resource.c` includes this file together with `dpcs_2_0_3_sh_mask.h`, then expands link encoder register tables from these macros.

## Important APIs, Types, and Macros

The public surface is entirely preprocessor definitions:

- `mmDPCSTX0_DPCSTX_TX_CLOCK_CNTL` through `mmDPCSTX0_DPCSTX_PLL_UPDATE_DATA`, and equivalent `DPCSTX1` names, map transmit control registers to offsets `0x2928` through `0x292d` for instance 0 and `0x2a00` through `0x2a05` for instance 1.
- `mmRDPCSTX0_RDPCSTX_CNTL` through `mmRDPCSTX0_RDPCSTX_PHY_CNTL14`, and equivalent `RDPCSTX1` names, map reduced PHY control/status registers to offsets `0x2930` through `0x294e` and `0x2a08` through `0x2a26`.
- Every register has a companion `..._BASE_IDX` macro set to `2`. Resource macros use this index with segment macros such as `BASE(mm..._BASE_IDX)` before adding the register offset.
- The include guard `_dpcs_2_0_3_OFFSET_HEADER` prevents duplicate macro definition inside a single translation unit.

There are no C functions, structs, enums, or inline helpers in this file. The effective API is the macro naming scheme expected by resource and link encoder headers.

## Control Flow

The control flow is compile-time macro expansion:

1. `dcn201_resource.c` includes `dpcs_2_0_3_offset.h` and `dpcs_2_0_3_sh_mask.h`.
2. Link encoder register lists expand names such as `RDPCSTX0_RDPCSTX_PHY_CNTL3` into `BASE(mmRDPCSTX0_RDPCSTX_PHY_CNTL3_BASE_IDX) + mmRDPCSTX0_RDPCSTX_PHY_CNTL3`.
3. The resulting numeric addresses populate `struct dcn10_link_enc_registers` arrays for two link encoder instances.
4. Runtime encoder code later uses those populated register structs through AMD display register helper paths, not through this header directly.

The file itself has no branches or runtime entry points. A bad macro value changes the compiled register table silently, which is why generated-header correctness is critical.

## State and Persistence Behavior

No software state is stored by this header. The defined offsets point at persistent hardware MMIO state in the display PHY and transmitter blocks. Registers named by this file can affect live link behavior, including PHY reset, lane enablement, FIFO state, clock gating, PLL programming, interrupt clearing/masking, and scratch/debug state. Persistence is hardware-defined: values may survive until reset, power-gate transitions, or explicit driver writes, depending on the register.

## Dependencies and Integration Points

This header depends on the AMD ASIC register generation convention:

- `mm...` prefixes are consumed by resource macros using token pasting.
- `_BASE_IDX` values must match the DCN base segment definitions included by the resource file.
- Field definitions from `dpcs_2_0_3_sh_mask.h` must correspond to these offsets.
- `dcn201_resource.c` is the direct integration point for DCN 2.0.1, where only two link encoder instances are created.
- `dcn20_link_encoder.h` provides many DPCS mask/shift list macros that expect `RDPCSTX0` field names.

Because all names are plain preprocessor macros, any consumer that includes multiple ASIC generations in one translation unit risks name collisions unless the build isolates generation-specific resource files.

## Risks and Edge Cases

- Offset and mask mismatches can compile cleanly but write the wrong hardware register or field.
- All `_BASE_IDX` values are `2`; if a future ASIC routes these blocks through a different segment, resource tables would target the wrong MMIO aperture.
- The 2.0.3 offset surface covers only two DPCS/RDPCS instances. Reusing it for a design with more transmitters would create missing macro failures or, worse, incorrect copy/paste substitutions.
- `dpcs_2_0_3_sh_mask.h` contains some debug field definitions for registers such as `DPCSTX0_DPCSTX_DEBUG_CONFIG`, but this offset header does not define matching `mmDPCSTX*_DPCSTX_DEBUG_CONFIG` offsets. That is safe only while no 2.0.3 register-list macro instantiates those debug registers.
- These register names encode hardware behavior but not access semantics. Clear-on-write, read-only status, and sequence requirements must be enforced in the higher-level link encoder code or hardware programming tables.

## Test Signals

Useful validation signals include:

- A build of the DCN 2.0.1 display resource path, especially `dcn201_resource.c`, to catch missing or renamed macros.
- Static comparison against AMD register XML/source-generation output for DPCS 2.0.3.
- Link encoder bring-up tests on matching hardware, including DP link training, lane enable/disable, PLL programming, hotplug, suspend/resume, and interrupt handling.
- Register readback traces confirming that addresses in the constructed `link_enc_regs` table resolve to the intended DPCS and RDPCS instance offsets.
