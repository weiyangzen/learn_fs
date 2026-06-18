# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_11_0_6_offset.h

## Purpose

`smuio_11_0_6_offset.h` is the SMUIO 11.0.6 generated register-offset header for the small ROM access subset used by AMDGPU. It maps symbolic `mm*` register names to offsets within the `smuio_smuio_SmuSmuioDec` address block, whose base address is documented as `0x5a000`.

## Important APIs, Types, and Macros

The header exports macro constants only:

- `mmCGTT_ROM_CLK_CTRL0` at offset `0x00e4`, base index `0`.
- `mmROM_INDEX` at offset `0x00e5`, base index `0`.
- `mmROM_DATA` at offset `0x00e6`, base index `0`.

There are no functions, types, or variables. These macros are passed to SOC15 helpers that combine IP block, instance, base index, and offset into an MMIO address.

## Control Flow

No control flow is implemented here. In `amdgpu/smuio_v11_0_6.c`, the macros drive this runtime sequence:

- `smuio_v11_0_6_get_rom_index_offset()` returns `SOC15_REG_OFFSET(SMUIO, 0, mmROM_INDEX)`.
- `smuio_v11_0_6_get_rom_data_offset()` returns `SOC15_REG_OFFSET(SMUIO, 0, mmROM_DATA)`.
- `smuio_v11_0_6_update_rom_clock_gating()` reads `mmCGTT_ROM_CLK_CTRL0`, updates the soft override bits supplied by the matching mask header, and writes the register only if the value changes.
- `smuio_v11_0_6_get_clock_gating_state()` reads `mmCGTT_ROM_CLK_CTRL0` and reports ROM MGCG support when override bit 0 is not set.

## State and Persistence Behavior

The header has no state. It names hardware registers whose state is persistent only in the device:

- `mmCGTT_ROM_CLK_CTRL0` controls/reflects ROM clock-gating timing and soft override state.
- `mmROM_INDEX` and `mmROM_DATA` form a hardware register pair for indexed ROM access.

Driver writes to `mmCGTT_ROM_CLK_CTRL0` survive until device reset, firmware action, or another driver path changes the register. ROM index/data usage is transient during VBIOS or ROM reads.

## Dependencies

The file depends on include guard `_smuio_11_0_6_OFFSET_HEADER` and the generated naming convention expected by AMDGPU SOC15 access macros. It must be paired with `smuio_11_0_6_sh_mask.h` for field-level operations. The runtime consumer depends on `amdgpu_device`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `AMD_IS_APU`, and `AMD_CG_SUPPORT_ROM_MGCG`.

## Integration Points

Direct include:

- `drivers/gpu/drm/amd/amdgpu/smuio_v11_0_6.c`

Functional integration:

- Registers are exposed through `const struct amdgpu_smuio_funcs smuio_v11_0_6_funcs`, which lets the wider AMDGPU device code locate ROM index/data registers and control ROM memory clock gating for this SMUIO IP revision.

## Risks and Edge Cases

- A wrong base index or offset makes SOC15 MMIO access hit a different register. For ROM access this can break VBIOS reads; for `CGTT_ROM_CLK_CTRL0` it can alter unrelated hardware state.
- `smuio_v11_0_6.c` intentionally skips ROM clock-gating control on APUs because the register is unavailable there. Reusing the offset macros without the same guard can fault or read undefined data on APU configurations.
- This 11.0.6 subset is narrower than the 11.0.0 and 13.0.2 maps. Code should not assume other SMUIO registers are available from this header.

## Test Signals

- Build coverage for `smuio_v11_0_6.c` validates the three exported offset names and matching mask names.
- Runtime VBIOS ROM reads validate `mmROM_INDEX`/`mmROM_DATA`.
- Clock-gating enable/disable tests validate the `mmCGTT_ROM_CLK_CTRL0` address and APU skip path.
- Comparing `SOC15_REG_OFFSET(SMUIO, 0, mm*)` output against hardware register documentation or known-good traces is the primary regression check for generated offsets.
