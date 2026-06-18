# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 24772-27122

## Scope

This chunk is a generated AMD GC 9.0 shift/mask register-header segment. It contains C preprocessor constants only: hardware register fields are represented as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros for composing and decoding 32-bit GPU register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected range begins at the tail of `CGTS_CU8_LDS_SQ_CTRL_REG`, after the corresponding register marker and shift definitions in the previous chunk, then covers the rest of the compute-unit clock/test/status override definitions for CU8 through CU15 and all TCPI controls for CU0 through CU15. It then defines a broad set of GC clock-gating/throttle controls, crosses `gc_ea_pwrdec`, `gc_utcl2_vmsharedhvdec`, and starts `gc_hypdec`. The final line is only the `CP_ME_RAM_WADDR__ME_RAM_WADDR__SHIFT` macro; the matching mask and following CP microcode/RAM fields are in the next chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM graphics-core hardware metadata and is unrelated to Ceph filesystem behavior.

## Purpose

`gc_9_0_sh_mask.h` supplies bit layouts for GC 9.0 graphics-core registers. Driver code pairs these constants with register-address symbols from `gc_9_0_offset.h` and uses AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, and SOC15 register accessors to avoid hard-coded bit positions.

This chunk is mainly concerned with power, clock, virtualization, and CP firmware access surfaces:

- Per-CU `CGTS_*` controls for shader processor, LDS/SQ, texture address/SQC, texture data/TCPF, and TCPI subblocks. These fields expose subblock status bits plus override, busy override, light-sleep override, and SIMD-busy override controls.
- Per-block `CGTT_*` and related `*_CGTT_*` clock-throttling/clock-gating controls for SPI, primitive/geometry front-end blocks, scan converter, shader, shader export, texture/data/address/cache blocks, DB/CB/backend blocks, CP/CPF/CPC/RLC, RMI, TCPF, GCEA, and UTCL2.
- RLC resource-management validity state through `RLC_GFX_RM_CNTL`.
- SR-IOV / virtualization and IOMMU-visible memory window controls in `gc_utcl2_vmsharedhvdec`, including per-VF framebuffer size/offset pairs, MARC base/relocation/length windows, IOMMU enable/performance bits, PCIe ATS enable fields, and UTCL2 clock-gating controls.
- The beginning of CP hypervisor/microcode access definitions for PFP and ME firmware/RAM windows, including PFP ucode address/data and ME ucode/read/write address fields.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field's raw 32-bit mask.
- Matching register addresses are in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h`.
- Consumers normally use these macros through AMDGPU register helpers rather than directly shifting by hand.

Notable macro groups in this range include:

- `CGTS_CU8_LDS_SQ_CTRL_REG` tail plus `CGTS_CU8_*` through `CGTS_CU15_*`: per-compute-unit CGTS controls for `SP00`, `SP01`, `LDS`, `SQ`, `TA`, `SQC`, `SP10`, `SP11`, `TD`, and `TCPF`. Repeated fields include 7-bit state slices and override bits at low and high halfword positions.
- `CGTS_CU0_TCPI_CTRL_REG` through `CGTS_CU15_TCPI_CTRL_REG`: per-CU TCPI state and override fields, with the same `TCPI`, `TCPI_OVERRIDE`, `TCPI_BUSY_OVERRIDE`, `TCPI_LS_OVERRIDE`, and `TCPI_SIMDBUSY_OVERRIDE` layout.
- `CGTT_SPI_CLK_CTRL`, `CGTT_PC_CLK_CTRL`, `CGTT_BCI_CLK_CTRL`, `CGTT_VGT_CLK_CTRL`, `CGTT_IA_CLK_CTRL`, `CGTT_WD_CLK_CTRL`, `CGTT_PA_CLK_CTRL`, `CGTT_SC_CLK_CTRL0/1`, `CGTT_SQ_CLK_CTRL`, and `CGTT_SQG_CLK_CTRL`: graphics front-end and shader clock-gating controls with on-delay/off-hysteresis, debug/perf enables, group/core overrides, register overrides, and soft-stall override bits.
- `SQ_ALU_CLK_CTRL`, `SQ_TEX_CLK_CTRL`, `SQ_LDS_CLK_CTRL`, `SQ_POWER_THROTTLE`, and `SQ_POWER_THROTTLE2`: shader subblock clock and power throttle fields.
- `CGTT_SX_CLK_CTRL0` through `CGTT_SX_CLK_CTRL4`: shader-export clock-gating controls for export/position/index banks, blend queues, request paths, and related subblock overrides.
- `TD_CGTT_CTRL`, `TA_CGTT_CTRL`, `CGTT_TCPI_CLK_CTRL`, `CGTT_TCI_CLK_CTRL`, `CGTT_GDS_CLK_CTRL`, `DB_CGTT_CLK_CTRL_0`, `CB_CGTT_SCLK_CTRL`, `TCC_CGTT_SCLK_CTRL`, `TCA_CGTT_SCLK_CTRL`, `RMI_CGTT_SCLK_CTRL`, and `CGTT_TCPF_CLK_CTRL`: texture, global data share, depth/color backend, cache, memory-interface, and texture-cache frontend clock controls.
- `CGTT_CP_CLK_CTRL`, `CGTT_CPF_CLK_CTRL`, `CGTT_CPC_CLK_CTRL`, and `CGTT_RLC_CLK_CTRL`: command processor, command processor front-end, compute processor, and RLC clock gating/soft-stall overrides.
- `GCEA_CGTT_CLK_CTRL`: graphics/EA power-decoder clock-gating control with return/register override fields.
- `MC_VM_FB_SIZE_OFFSET_VF0` through `MC_VM_FB_SIZE_OFFSET_VF15`: per-virtual-function framebuffer size and offset fields, each split into 16-bit `VF_FB_SIZE` and `VF_FB_OFFSET`.
- `VM_IOMMU_MMIO_CNTRL_1`, `MC_VM_MARC_BASE_*`, `MC_VM_MARC_RELOC_*`, `MC_VM_MARC_LEN_*`, `VM_IOMMU_CONTROL_REGISTER`, `VM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER`, and `VM_PCIE_ATS_CNTL*`: IOMMU/MARC/ATS controls for memory aperture remapping and PCIe address translation services. Low MARC address/length fields use bit-12 alignment, high fields use 20-bit masks, and relocation low fields also include enable/read-only bits.
- `UTCL2_CGTT_CLK_CTRL`: UTCL2 clock-gating delay, soft override, MGLS override, and soft-stall override fields.
- `CP_HYP_PFP_UCODE_ADDR`, `CP_PFP_UCODE_ADDR`, `CP_HYP_PFP_UCODE_DATA`, `CP_PFP_UCODE_DATA`, `CP_HYP_ME_UCODE_ADDR`, `CP_ME_RAM_RADDR`, and the partial `CP_ME_RAM_WADDR`: CP microcode and ME RAM address/data window fields. In `gfx_v9_0.c`, the ME firmware loading path writes `mmCP_ME_RAM_WADDR`, streams data through `mmCP_ME_RAM_DATA`, then writes the ME firmware version back to `mmCP_ME_RAM_WADDR`.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Detect/select a GC 9.0 ASIC path and include the matching generated register headers.
2. Choose a register address from `gc_9_0_offset.h`.
3. Compose or decode a register value with these shift/mask definitions, commonly through `REG_SET_FIELD` or `REG_GET_FIELD`.
4. Access the register through MMIO, RLC-safe accessors, SOC15 helpers, firmware loading paths, SR-IOV virtualization setup, power-management code, or diagnostic register dumps.

For CGTS and CGTT families, initialization, golden-register, power-management, debug, and recovery code can read status or program clock-gating/override policy. This header does not encode the hardware sequencing needed to safely change clock-gating bits, clear stalls, or sample transient busy state.

For VM/IOMMU/MARC/ATS registers, virtualization and memory-management code configures per-VF apertures, remap windows, IOMMU enablement, performance optimizations, and PCIe ATS behavior. The header only defines bit positions; it does not validate VF ownership, aperture bounds, PCIe/IOMMU capability state, or ordering relative to TLB/cache invalidations.

For CP hypervisor and microcode windows, firmware-loading code writes address selectors and then streams data through paired data registers. Indexed RAM/ucode windows require strict sequencing and size bounds in the consumer. The partial `CP_ME_RAM_WADDR` definition at the chunk end must be merged with the following chunk before describing the complete CP RAM window family.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware register fields whose values live in the GPU until reset, power-gating loss, firmware reinitialization, driver reprogramming, or virtualization teardown.

CGTS fields can expose or force per-CU subblock state for SP, LDS, SQ, TA, SQC, TD, TCPF, and TCPI. Status-style bits may change while waves and memory operations run; override bits persist until cleared or reset and can intentionally hold blocks out of normal clock/light-sleep behavior.

CGTT fields persist as graphics-core clock-gating and throttle policy. `ON_DELAY` and `OFF_HYSTERESIS` tune gating latency; `SOFT_STALL_OVERRIDE*`, `SOFT_OVERRIDE*`, `REG_OVERRIDE`, `CORE*_OVERRIDE`, `MGLS_OVERRIDE`, debug/perf enables, and all-clock-on fields can materially change power, performance, and hang behavior. Some fields are reserved or spare and should be preserved during read-modify-write unless a hardware sequence explicitly defines them.

The VM/IOMMU/MARC/ATS fields persist as virtualization and address-translation state. Per-VF framebuffer offset/size fields define guest-visible framebuffer apertures. MARC base, relocation, enable, read-only, and length fields define remap windows. ATS and IOMMU bits control whether transactions can use address translation services. Misconfigured values can survive long enough to affect multiple queues, VFs, or DMA streams until reset or reconfiguration.

CP PFP/ME ucode address/data and ME RAM address fields are persistent selector/data windows during firmware upload and inspection. Their contents and selected indices interact with CP firmware state; address selector writes are not just passive values when paired with following data writes.

## Dependencies And Integration Points

The primary dependency is the matching generated offset header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h`, which defines addresses such as `mmCGTS_CU8_TA_SQC_CTRL_REG`, `mmCGTT_SPI_CLK_CTRL`, `mmMC_VM_FB_SIZE_OFFSET_VF*`, `mmMC_VM_MARC_*`, `mmVM_PCIE_ATS_CNTL*`, `mmCP_HYP_PFP_UCODE_ADDR`, and `mmCP_ME_RAM_WADDR`.

AMDGPU integration points include:

- GFX 9.0 initialization, golden-register programming, suspend/resume, GPU reset, and gfxoff/power-management code that needs GC clock-gating and soft-stall override definitions.
- Hang triage and register-dump code that decodes CGTS per-CU status or broad CGTT clock-gating state to determine whether shader, texture, backend, RLC, CP, or memory-interface blocks are stuck or forced on.
- RLC and command processor bring-up paths using `CGTT_RLC_CLK_CTRL`, `RLC_GFX_RM_CNTL`, and CP/CPF/CPC clock controls.
- CP firmware loading and inspection paths. `gfx_v9_0.c` directly writes `mmCP_ME_RAM_WADDR` during ME firmware upload; adjacent CP PFP/ME ucode fields in this chunk describe the indexed windows around that flow.
- SR-IOV and virtualization setup that configures per-VF framebuffer windows, MARC remapping, IOMMU enablement, and ATS enablement.
- GPUVM, IOMMU, PCIe ATS, and UTCL2-related code paths where translation policy and clock-gating behavior affect memory access correctness and performance.
- Common register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_RLC`, and RLC-shadowed or indexed register accessors.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but can program a different hardware bit, corrupt diagnostics, or change power/virtualization policy.
- This chunk starts and ends mid-register context. It begins with only three masks for `CGTS_CU8_LDS_SQ_CTRL_REG`, and it ends after only `CP_ME_RAM_WADDR__ME_RAM_WADDR__SHIFT`. Adjacent chunks are required for full register-family context.
- CGTS and CGTT families are highly repetitive. Copy/paste or generator errors can swap CU numbers, subblocks, group numbers, or override bits while still looking structurally plausible.
- Clock-gating and soft-stall overrides can hide idle/hang symptoms or create new hangs if set while a block is active. Full-register writes risk changing reserved/spare bits, debug enables, or performance overrides.
- `ON_DELAY` and `OFF_HYSTERESIS` fields are small delay controls, not arbitrary counters. Incorrect values can cause power regressions, clock chatter, or delayed wake behavior that only appears under workload stress.
- Per-VF framebuffer size/offset fields and MARC relocation windows are security-sensitive in SR-IOV contexts. Off-by-one VF indexing, wrong size units, or mispacked high/low address fields can expose memory across guests or block valid guest access.
- MARC low fields are aligned at bit 12 while high fields are only 20 bits. Ad hoc address packing can silently drop low address bits or overflow the intended aperture.
- `MARC_ENABLE` and `MARC_READONLY` bits share relocation-low registers with address bits; consumers must not overwrite control bits when updating relocation addresses.
- ATS/IOMMU enable bits depend on platform and PCIe/IOMMU capability state. Enabling ATC at the wrong time can cause translation faults or stale translations if invalidation sequencing is missing.
- CP microcode and ME RAM address/data windows require ordered indexed writes. A bad address mask or missing bounds check in a consumer can load firmware at the wrong RAM location or overwrite version/address selector state.

## Test Signals

Useful validation combines generated-data checks, build coverage, and hardware/runtime behavior:

- Build AMDGPU code paths that include `gc_9_0_sh_mask.h` and `gc_9_0_offset.h`; missing, renamed, or malformed macros should surface at compile time.
- Mechanically compare this line range against AMD's authoritative GC 9.0 register database. Complete fields should have matching `__SHIFT` and `_MASK` entries, masks should align with shifts, and repeated CU/VF families should remain structurally consistent.
- Cross-check every register family in this chunk against `gc_9_0_offset.h` for matching address symbols and base-index entries.
- Static sanity checks should verify repeated `CGTS_CU8` through `CGTS_CU15` layouts, `CGTS_CU0_TCPI` through `CGTS_CU15_TCPI`, per-block `CGTT_*` override bit positions, per-VF framebuffer size/offset pairs, four MARC base/reloc/length windows, and sixteen ATS VF enable registers.
- Runtime bring-up tests on GC 9.0 hardware should cover graphics initialization, golden-register programming, gfxoff/power transitions, suspend/resume, and GPU reset without stuck busy bits or unexpected clock-gating overrides.
- Power/performance tests should compare clock-gating behavior, wake latency, and idle power before and after any generated-register update that touches CGTT/CGTS fields.
- SR-IOV tests should validate VF framebuffer aperture isolation, MARC remapping, read-only behavior, ATS enablement, and guest memory access under reset and migration-like teardown/reinit paths.
- GPUVM/IOMMU stress tests should watch for translation faults, stale ATS entries, bad aperture boundaries, or UTCL2 clock-gating side effects.
- CP firmware-loading tests should verify PFP/ME firmware upload succeeds, CP rings start, firmware version writes/readbacks are sane, and no ME RAM window bounds or address-selector regressions occur.
- Hang/debug register-dump tests should decode CGTS/CGTT state during known workloads and compare against expected busy/idle/override states.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002625`. The previous chunk owns the beginning of `CGTS_CU8_LDS_SQ_CTRL_REG`, while this chunk starts at its final masks. The next chunk must complete `CP_ME_RAM_WADDR`, then continue the CP hypervisor/microcode address/data definitions. The final per-file research should merge these boundaries before presenting a whole-file view of `gc_9_0_sh_mask.h`.
