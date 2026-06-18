# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cyan_skillfish_reg_init.c

## Purpose
`cyan_skillfish_reg_init.c` initializes AMDGPU register base offset tables for Cyan Skillfish, a Navi-family APU configuration using static IP offset tables. Its single function, `cyan_skillfish_reg_base_init()`, maps each hardware IP block enum to the corresponding generated base-address table used by register access macros.

## Important APIs, Types, and Functions
The file exports `int cyan_skillfish_reg_base_init(struct amdgpu_device *adev)`, declared in `nv.h`. It includes `amdgpu.h`, `nv.h`, SOC15 common/IP headers, and `cyan_skillfish_ip_offset.h`, which defines symbols such as `GC_BASE`, `HDP_BASE`, `MMHUB_BASE`, and other per-IP base arrays.

The function sets `adev->gfx.xcc_mask = 1`, then loops `i` from `0` to `MAX_INSTANCE - 1` and fills `adev->reg_offset[HWIP][i]` for GC, HDP, MMHUB, ATHUB, NBIO, MP0, MP1, VCN, DF, DCE, OSSSYS, SDMA0, SDMA1, SMUIO, THM, and CLK. SDMA0 and SDMA1 intentionally point at `GC_BASE.instance[i]`, and VCN maps to `UVD0_BASE`. It returns `0` unconditionally.

## Control Flow and Integration
Control flow is linear: initialize the graphics XCC mask, populate all relevant hardware-IP offset pointers for each instance, and return success. The function is called from the discovery/Navi initialization path for Cyan Skillfish; `amdgpu_discovery.c` invokes it for this ASIC path when static/discovery register base setup is needed. After this function runs, SOC15 register macros can resolve logical IP/register accesses through `adev->reg_offset`.

## State and Persistence Behavior
The function mutates only in-memory driver state on `struct amdgpu_device`: `adev->gfx.xcc_mask` and `adev->reg_offset`. There is no persistent storage and no allocation. The offset pointers remain valid as long as the generated static base tables remain linked into the driver image and the `amdgpu_device` instance is alive. The function is idempotent for the same device because it overwrites the same fields with the same static addresses.

## Dependencies
The critical dependency is `cyan_skillfish_ip_offset.h`, whose generated structures must match `MAX_INSTANCE` and the hardware IP enum layout. It also depends on the SOC15 register access model, `amdgpu_device.reg_offset`, and the caller selecting this function only for Cyan Skillfish-compatible hardware.

## Risks
Wrong IP-to-base mapping causes register reads/writes to target the wrong MMIO ranges, which can break initialization broadly. The comment notes hardware has more IP blocks than the driver initializes; future code accessing an uninitialized IP block would fail or use null offsets. The cast to `uint32_t *` assumes generated base structures are layout-compatible with the register offset table. An incorrect `xcc_mask` would misrepresent graphics complex topology.

## Test Signals
Signals include successful device discovery/probe on Cyan Skillfish, correct MMIO access through SOC15 macros, no null `reg_offset` use for initialized IPs, and successful initialization of GC, SDMA, VCN, display, SMU/thermal/clock, and memory hub paths. Regression checks should compare generated IP offset headers with this mapping whenever Cyan Skillfish tables are regenerated.
