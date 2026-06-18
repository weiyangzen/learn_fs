# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h lines 5019-7499

## Purpose

This chunk is generated AMD GC 11.5.0 register-offset metadata. It does not implement executable control flow; it provides C preprocessor symbols that map Graphics/Compute (GC) hardware register names to SOC15 register offsets and companion `*_BASE_IDX` values. Kernel driver code can then use symbolic names such as `regGRBM_GFX_CNTL`, `regCP_MES_CNTL`, or `regGL2C_CTRL` through SOC15 helpers instead of hard-coded offsets.

The assigned range starts at the tail of `gc_pfvf_grbmdec` with `regGRBM_GFX_CNTL` and `regGRBM_NOWHERE`, then covers complete blocks for PA/SQ/CP/DIDT/SPI/TCP/GDS/UTCL1/PMM/CAC/GFXU/CP RS64/cache decoders, and ends mid-`gc_perfddec` at `regTCP_PERFCOUNTER1_LO`. The next line outside the chunk supplies `regTCP_PERFCOUNTER1_LO_BASE_IDX`, so merge/reconciliation should treat the final register pair as split across chunks.

## Register Map Content

The chunk contains 1,203 non-`BASE_IDX` register symbols and 1,202 visible `*_BASE_IDX` companions, plus 13 intentional offset aliases. Every visible base index is `1`, which means these GC registers belong to the second base-address table slot used by SOC15 address computation.

Covered address blocks:

| Lines | Address block | Base address | Visible register range | Count |
| --- | --- | ---: | --- | ---: |
| 5019-5022 | `gc_pfvf_grbmdec` tail | `0x2a400` | `regGRBM_GFX_CNTL`..`regGRBM_NOWHERE` | 2 |
| 5025-5096 | `gc_pfvf_padec` | `0x2a500` | `regPA_SC_VRS_SURFACE_CNTL`..`regPA_SC_BINNER_OUTPUT_TIMEOUT_COUNTER` | 34 |
| 5097-5120 | `gc_pfvf_sqdec` | `0x2a780` | `regSQ_RUNTIME_CONFIG`..`regSQ_SHADER_TMA_HI` | 10 |
| 5121-5128 | `gc_pfonly_cpdec` | `0x2e000` | `regCP_DEBUG_2`..`regCP_FETCHER_SOURCE` | 2 |
| 5129-5138 | `gc_pfonly_cpphqddec` | `0x2e080` | `regCP_HPD_MES_ROQ_OFFSETS`..`regCP_HPD_STATUS0` | 3 |
| 5139-5170 | `gc_pfonly_didtdec` | `0x2e400` | DIDT EDC and indirect-index/data registers | 14 |
| 5171-5192 | `gc_pfonly_spidec` | `0x2e500` | SPI debug, arbitration, feature, and context-save status | 9 |
| 5193-5204 | `gc_pfonly_tcpdec` | `0x2e680` | TCP invalidate/status/control | 4 |
| 5205-5212 | `gc_pfonly_gdsdec` | `0x2e6c0` | GDS enhancement and OA CGPG restore | 2 |
| 5213-5230 | `gc_pfonly_utcl1dec` | `0x2e600` | UTCL1 and GCRD credit/target controls | 7 |
| 5231-5242 | `gc_pfonly_pmmdec` | `0x2e640` | GCR general/target/cmd/spare controls | 4 |
| 5243-5542 | `gc_pfonly_gccacdec` | `0x2eb40` | GC/SE CAC controls, weights, and indirect registers | 148 |
| 5543-5610 | `gc_pfonly2_spidec` | `0x2f000` | per-CU SPI resource reserve and enable registers | 32 |
| 5611-6206 | `gc_gfxudec` | `0x30000` | CP EOP/fence/stats/scratch/atomic/GDS/SPI user registers | 296 |
| 6207-7084 | `gc_cprs64dec` | `0x32000` | MES and GFX RS64 program/control/debug/aperture registers | 437 |
| 7085-7112 | `gc_gl1dec` | `0x33400` | GL1/GL1C arbitration, burst, status, and UTCL0 controls | 12 |
| 7113-7132 | `gc_chdec` | `0x33600` | CH/CHC arbitration, burst, delay, and status controls | 8 |
| 7133-7194 | `gc_gl2dec` | `0x33800` | GL2C/GL2A cache controls, address matching, flush/reset, counters | 29 |
| 7195-7206 | `gc_gl1hdec` | `0x33900` | GL1H arbitration and burst/status registers | 4 |
| 7207-7499 | `gc_perfddec` partial | `0x34000` | performance-counter registers from CPG through TCP | 146 visible |

Important symbol families include `GRBM`, `PA_SC`, `SQ`, `CP`, `DIDT`, `SPI`, `TCP`, `GDS`, `UTCL1`, `GCR`, `GC_CAC`, `SE_CAC`, `GL1`, `CH`, `GL2`, and many `*_PERFCOUNTER*` registers. The largest parts are the command processor/MES/RS64 families (`CP_*`) and the graphics performance counter block.

## APIs, Types, and Integration Points

There are no functions, structs, enums, or runtime APIs in this range. The public interface is the set of macros:

- `regNAME` gives the register offset used by SOC15 register access machinery.
- `regNAME_BASE_IDX` gives the base-address-table index paired with that offset.

The file is included directly by `drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c`. The same naming convention is used across AMDGPU GC headers by `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_ENTRY_STR`, and golden-register table macros in neighboring GC/GFX/MES code. In this source tree, similar register names are accessed in version-specific files such as `gfx_v11_0.c`, `gfx_v12_0.c`, `mes_v12_0.c`, and `mes_v12_1.c`; for GC 11.5.0, this header supplies the authoritative offsets for code that includes the `gc_11_5_0` register set.

Several symbols deliberately alias the same offset to preserve hardware/manual naming variants:

- `regCP_HPD_MES_ROQ_OFFSETS` and `regCP_HPD_ROQ_OFFSETS` at `0x1821`.
- `regSCRATCH_REG_ATOMIC` and `regSCRATCH_REG_CMPSWAP_ATOMIC` at `0x2048`.
- `regCP_APPEND_DATA` and `regCP_APPEND_DATA_LO` at `0x205a`.
- `regCP_APPEND_LAST_CS_FENCE` and `regCP_APPEND_LAST_CS_FENCE_LO` at `0x205b`.
- `regCP_APPEND_LAST_PS_FENCE` and `regCP_APPEND_LAST_PS_FENCE_LO` at `0x205c`.
- CP/ME atomic preop aliases from `0x205d` through `0x2062`.
- MES interrupt-vector aliases `regCP_MES_INTR_ROUTINE_START`/`regCP_MES_MTVEC_LO` and `_HI`/`MTVEC_HI` at `0x2801` and `0x2802`.

## Control Flow and State

The header has no branches, loops, locking, allocation, or I/O by itself. Control flow appears only in consumers that compile these constants into register reads and writes. State is entirely hardware-resident: writes through consumers can affect GPU scheduler/MES state, command-processor fences and atomics, cache control/flush behavior, CAC/power accounting, performance counters, scratch registers, and debug/trap settings.

The macros are compile-time constants and are not persisted by software. Persistence and reset behavior depend on the underlying GC hardware block. Many registers in the chunk are volatile operational registers, including counters, status registers, indirect-index/data windows, fence addresses, scratch slots, cache-control registers, and MES/RS64 program/aperture registers. Values may be reset by GPU reset, power-gating, clock-gating, firmware initialization, or mode switches outside this header.

## Dependencies

The chunk depends on the AMD ASIC register-generation contract: register symbols, offsets, address-block comments, and base-index companions must match the GC 11.5.0 hardware specification and the SOC15 base-address table used by AMDGPU. It is paired conceptually with sibling generated headers such as `gc_11_5_0_sh_mask.h`, which provide field masks and shifts for many of these registers.

Consumer dependencies are the AMDGPU register-access helpers and include ordering. A consumer must include the correct ASIC offset header for the active IP version; using a GC 11.5.0 offset against a different hardware generation can silently target the wrong MMIO address.

## Risks

- Offset drift is high impact: a single incorrect constant can make `RREG32_SOC15`/`WREG32_SOC15` read or write the wrong hardware register.
- The chunk boundary splits `regTCP_PERFCOUNTER1_LO` from its `BASE_IDX`, so partial analysis or generated diffs must not treat that symbol as missing a companion in the full file.
- Aliased offsets are expected; deduplication tooling must preserve all names because consumers may use either the generic or block-specific spelling.
- PF/VF and PF-only block names matter for virtualization/security. Exposing or writing PF-only registers in the wrong execution context could break SR-IOV assumptions.
- Indirect register pairs such as `DIDT_IND_INDEX`/`DIDT_IND_DATA`, `GC_CAC_IND_INDEX`/`GC_CAC_IND_DATA`, and `SE_CAC_IND_INDEX`/`SE_CAC_IND_DATA` require ordered consumer access and appropriate serialization; the header only names the windows.
- Counter low/high pairs and 64-bit address/data pairs require consumer-side ordering to avoid torn reads or partially programmed addresses.
- Generated headers are easy to review superficially; validation should rely on generator inputs, hardware tables, and compile-time/use-site tests rather than manual spot checks only.

## Test and Validation Signals

- Build coverage: compile AMDGPU code paths that include `gc/gc_11_5_0_offset.h`, especially `gfxhub_v11_5_0.c`.
- Static checks: verify every `reg*` symbol in the full header has the expected `*_BASE_IDX` companion and that all base indices match the SOC15 base-address table for GC 11.5.0. The apparent missing companion at this chunk end is resolved at line 7500.
- Register-table checks: compare address-block base comments and offset ranges against the vendor register database used to generate the file.
- Runtime smoke: on matching GC 11.5.0 hardware, confirm safe reads of status/version/counter registers through debugfs or driver diagnostic paths and confirm no invalid-register faults during bring-up.
- Functional signals: MES initialization, ring scheduling, GPU reset/recovery, cache invalidation, performance-counter collection, and SR-IOV/PF-VF paths should continue to work because this chunk names registers used by those paths.
