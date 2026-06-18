# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_3_0_sh_mask.h lines 2340-4718

## Scope

This chunk covers the middle of the generated AMD MMHUB 2.3 register shift/mask header. The range starts inside the `DAGB0_WR_TLB_CREDIT` field definitions, completes a large tail of the `mmhub_dagbdec`/`DAGB0_*` register block, then enters `addressBlock: mmhub_mmea_mmeadec0` and defines most of the `MMEA0_*` memory/E/A decoder register fields through the beginning of `MMEA0_LATENCY_SAMPLING`.

The file is declarative hardware ABI data. It contains no C functions, structs, executable branches, storage, or in-header persistence. Its public surface is the generated set of `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros used by AMDGPU code to compose and decode 32-bit MMIO register values.

Because this is a chunk of a larger generated file, the final per-file research pass should reconcile it with earlier lines for the beginning of `DAGB0_WR_TLB_CREDIT` and with later lines for the rest of `MMEA0_LATENCY_SAMPLING`, performance counters, error status, DSM/error-injection, clock-gating, and any later MMEA instances.

## Purpose

`mmhub_2_3_0_sh_mask.h` supplies bit-accurate field layout for the MMHUB 2.3 hardware block. The sibling `mmhub_2_3_0_offset.h` provides register addresses, `mmhub_2_3_0_default.h` provides reset/default values, and this header provides the masks and shifts that let code update a single field without hard-coding bit positions.

In this chunk, the `DAGB0_*` definitions describe write-side credits, outstanding/pending indications, snoop override controls, virtual-channel remapping, clock-gating disables, FIFO status, and performance-counter controls for the DAGB decoder. The `MMEA0_*` definitions describe the first MMEA decoder instance: DRAM and IO client grouping, group-to-virtual-channel mapping, request accumulation, CAM/page-burst and priority policy, address normalization and DRAM address decoding, channel/bank/chip-select hashing, harvested address ranges, SDP arbitration/credits/reservations, request controls, miscellaneous link/priority behavior, and latency-sampler filters.

Although this repository path sits under a Ceph client source import, this file is Linux AMDGPU DRM hardware register interface data. It is not Ceph filesystem logic.

## Important Macro Families

The macro convention is the API:

- `REGISTER__FIELD__SHIFT` is the least-significant bit position for a field.
- `REGISTER__FIELD_MASK` is the already-positioned 32-bit mask for that field.
- Consumers use these directly or through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`.

### DAGB0 write credits, status, and counters

The start of the chunk finishes `DAGB0_WR_TLB_CREDIT`, with six 5-bit TLB credit fields (`TLB0` through `TLB5`). It then defines write data and misc credit controls:

- `DAGB0_WR_DATA_CREDIT` packs deadlock-VC, large-burst, middle-burst, and small-burst credit budgets into byte-sized fields.
- `DAGB0_WR_MISC_CREDIT` covers atomic credits, deadlock VC number, OSD credits, and OSD deadlock credits.
- `DAGB0_WR_OSD_CREDIT_CNTL1/2` expose per-VC, IO, GMI, and pool OSD credits plus credit margin and legacy behavior.
- `DAGB0_WR_DATA_FIFO_CREDIT_CNTL1/2` and `DAGB0_WR_ATOMIC_FIFO_CREDIT_CNTL1` define per-VC FIFO credits, pool credits, VC mode, fixed-equation bits, and per-VC maximum packet lengths.

The pending/status block includes `DAGB0_WRCLI_ASK_PENDING`, `GO_PENDING`, `GBLSEND_PENDING`, `TLB_PENDING`, `OARB_PENDING`, `OSD_PENDING`, `DBUS_ASK_PENDING`, and `DBUS_GO_PENDING`, each exposing a full-width `BUSY` mask. `DAGB0_WRCLI_GPU_SNOOP_OVERRIDE` and `_VALUE` are full-width enable/value fields for snoop override policy.

`DAGB0_DAGB_DLY`, `DAGB0_CNTL_MISC`, and `DAGB0_CNTL_MISC2` cover delay/client/position selection, EA VC0-VC7 remapping, bandwidth initialization/gap cycles, urgency boost/halt, clock-gating disable bits for write/read request/return and TLB paths, EA busy disable bits, byte-swap control, parity check enable, and read-return FIFO credit fields.

The chunk also defines status and performance-counter registers:

- `DAGB0_FIFO_EMPTY`, `DAGB0_FIFO_FULL`, `DAGB0_WR_CREDITS_FULL`, and `DAGB0_RD_CREDITS_FULL` expose packed fullness/emptiness state.
- `DAGB0_PERFCOUNTER_LO/HI` provide counter data and compare value bits.
- `DAGB0_PERFCOUNTER0_CFG`, `1_CFG`, `2_CFG`, and `DAGB0_PERFCOUNTER_RSLT_CNTL` provide event select ranges, mode, enable, clear, counter select, start/stop triggers, enable-any, clear-all, and stop-on-saturate.
- `DAGB0_RESERVE0` through `DAGB0_RESERVE9` are full-width reserved fields.

### MMEA0 DRAM grouping, arbitration, and priority

The `mmhub_mmea_mmeadec0` block begins at line 2627. It first defines DRAM client and priority plumbing:

- `MMEA0_DRAM_RD_CLI2GRP_MAP0/1` and `MMEA0_DRAM_WR_CLI2GRP_MAP0/1` map client IDs `CID0` through `CID31` into 2-bit request groups for read and write traffic.
- `MMEA0_DRAM_RD_GRP2VC_MAP` and `MMEA0_DRAM_WR_GRP2VC_MAP` map four request groups to virtual channels.
- `MMEA0_DRAM_RD_LAZY` and `MMEA0_DRAM_WR_LAZY` encode per-group delay plus request accumulation threshold, timeout, and idle maximum.
- `MMEA0_DRAM_RD_CAM_CNTL` and `MMEA0_DRAM_WR_CAM_CNTL` define CAM allocation mode and per-group allocation fields.
- `MMEA0_DRAM_PAGE_BURST` defines read/write page-hit burst limits.
- `MMEA0_DRAM_RD_PRI_AGE`, `WR_PRI_AGE`, `RD_PRI_QUEUING`, `WR_PRI_QUEUING`, `RD_PRI_FIXED`, `WR_PRI_FIXED`, `RD_PRI_URGENCY`, and `WR_PRI_URGENCY` provide age, queueing, fixed priority, urgency coefficient, and urgency mode fields for the four DRAM request groups.
- `MMEA0_DRAM_RD_PRI_QUANT_PRI1/2/3` and `MMEA0_DRAM_WR_PRI_QUANT_PRI1/2/3` define per-group quantum thresholds.

These fields are QoS and forward-progress controls. They determine how MMEA0 classifies MMHUB clients, assigns them to virtual channels, accumulates requests, arbitrates across groups, and switches priority modes.

### MMEA0 address normalization and DRAM decoding

The address block defines how incoming addresses are normalized and decoded into DRAM topology:

- `MMEA0_ADDRNORM_BASE_ADDR0/1`, `LIMIT_ADDR0/1`, and `OFFSET_ADDR1` describe two address ranges with valid bits, legacy MMIO-hole enable, interleave channel/die/socket parameters, address select, base/limit address, destination fabric ID, and high-address offset behavior.
- `MMEA0_ADDRNORMDRAM_HOLE_CNTL` and `MMEA0_ADDRNORMDRAM_NP2_CHANNEL_CFG` describe DRAM hole validity/offset and non-power-of-two channel space sizing.
- `MMEA0_ADDRDEC_BANK_CFG` and `MMEA0_ADDRDEC_MISC_CFG` define bank, bank-group, pseudo-channel, bank swap, row/column/bank remap, stack, 3DS, and chip-select sizing/stacking fields.
- `MMEA0_ADDRDECDRAM_ADDR_HASH_BANK0` through `BANK5`, `PC`, `PC2`, `CS0`, and `CS1` define hash masks for bank, pseudo-channel, and chip-select selection.
- `MMEA0_ADDRDECDRAM_HARVEST_ENABLE`, `HARVNA_ADDR_START0/END0`, and `HARVNA_ADDR_START1/END1` describe harvested or non-addressable address-range enable and boundaries.

The chunk then defines repeated `ADDRDEC0` and `ADDRDEC1` chip-select programming:

- `BASE_ADDR_CS0..CS3` and `BASE_ADDR_SECCS0..SECCS3` give base address fields for primary and secondary chip selects.
- `ADDR_MASK_*`, `ADDR_CFG_*`, `ADDR_SEL_*`, `ADDR_SEL2_*`, `COL_SEL_LO_*`, `COL_SEL_HI_*`, and `RM_SEL_*` define address masks, config bits, row/column/bank/bank-group/chip-select address bit selection, remap, and column bit selection for paired chip selects (`CS01`, `CS23`, `SECCS01`, `SECCS23`) and later single-chip-select variants (`CS1`, `CS3`, `SECCS1`, `SECCS3`).
- `MMEA0_ADDRNORMDRAM_GLOBAL_CNTL`, `MMEA0_ADDRDECDRAM_GECC_HARV_ADJ0..5`, and `MMEA0_ADDRNORMDRAM_MASKING` complete this chunk's address-normalization side with global control, GECC harvest adjustment masks, and DRAM masking.

This is among the riskiest material in the chunk: a wrong mask or shift can misroute physical memory accesses, disturb interleave behavior, or break harvested-memory/topology handling.

### MMEA0 IO grouping and priority

The IO section mirrors the DRAM grouping model for non-DRAM traffic:

- `MMEA0_IO_RD_CLI2GRP_MAP0/1` and `MMEA0_IO_WR_CLI2GRP_MAP0/1` map client IDs to read/write IO groups.
- `MMEA0_IO_RD_COMBINE_FLUSH` and `MMEA0_IO_WR_COMBINE_FLUSH` control group flush timers and enable bits for request combining.
- `MMEA0_IO_GROUP_BURST` sets read/write group burst limits.
- `MMEA0_IO_RD_PRI_AGE`, `WR_PRI_AGE`, `RD_PRI_QUEUING`, `WR_PRI_QUEUING`, `RD_PRI_FIXED`, `WR_PRI_FIXED`, `RD_PRI_URGENCY`, and `WR_PRI_URGENCY` define the same age/queue/fixed/urgency policy fields for IO traffic.
- `MMEA0_IO_RD_PRI_URGENCY_MASKING` and `MMEA0_IO_WR_PRI_URGENCY_MASKING` provide one-bit urgency masks for client IDs `CID0` through `CID31`.
- `MMEA0_IO_RD_PRI_QUANT_PRI1/2/3` and `MMEA0_IO_WR_PRI_QUANT_PRI1/2/3` provide per-group quantum threshold fields.

The IO urgency-masking registers are full, densely packed 32-bit client masks. Callers must preserve all unrelated clients when changing one client bit.

### MMEA0 SDP arbitration, credits, request control, and sampling

The tail of this chunk defines shared data path controls:

- `MMEA0_SDP_ARB_DRAM` controls DRAM read/write burst limit cycles/data, early switch-to-read/write on priority or reservation, end-of-burst-on-expire, and decoupled read/write bank state.
- `MMEA0_SDP_ARB_FINAL` controls final DRAM/GMI/IO burst limits, burst multiplier, read-only flags for VC0-VC7, error-event and halt-request on error, GMI burst stretch, and DRAM/GMI read/write throttles.
- `MMEA0_SDP_DRAM_PRIORITY` and `MMEA0_SDP_IO_PRIORITY` define read/write priority values for groups 0-3.
- `MMEA0_SDP_CREDITS` defines tag, write-response, and read-response credits.
- `MMEA0_SDP_TAG_RESERVE0/1`, `MMEA0_SDP_VCC_RESERVE0/1`, and `MMEA0_SDP_VCD_RESERVE0/1` define per-VC tag and credit reservations plus distribute-pool flags.
- `MMEA0_SDP_REQ_CNTL` defines read/write/atomic pass-password overrides, DRAM/GMI chain override, inner-domain mode, and request block levels for reads, writes, and atomics.
- `MMEA0_MISC` controls relative priority modes in DRAM/GMI/IO arbiters, early write-return enable per VC, early SDP original-data behavior, link-manager dynamic/halt/reconnect/idle parameters, and chip-select switching preferences.
- `MMEA0_LATENCY_SAMPLING` begins at the chunk tail, defining sampler0/sampler1 filters for DRAM, GMI, IO, read, write, atomic-return, atomic-no-return, and virtual-channel selection. The final `SAMPLER1_VC_MASK` appears just after this chunk and must be merged from the next range.

## Control Flow

There is no direct control flow in this header. The only behavior is indirect: compiled driver code includes this generated macro table, reads or writes an MMIO register from the offset header, and uses a mask/shift pair to isolate a field.

Typical runtime flow in consumers is:

1. Read a 32-bit MMHUB register with a helper such as `RREG32_SOC15`.
2. Update one or more fields using `REG_SET_FIELD` or direct mask operations.
3. Write the result back with `WREG32_SOC15`, or decode status with `REG_GET_FIELD` or direct masks.
4. Poll status, collect counters, or rely on hardware behavior after the register programming takes effect.

One concrete integration in this tree is `drivers/gpu/drm/amd/amdgpu/mmhub_v2_3.c`: `mmhub_v2_3_update_medium_grain_clock_gating()` reads `mmDAGB0_CNTL_MISC2` and clears or sets `DAGB0_CNTL_MISC2__DISABLE_WRREQ_CG_MASK`, `DISABLE_WRRET_CG_MASK`, `DISABLE_RDREQ_CG_MASK`, `DISABLE_RDRET_CG_MASK`, `DISABLE_TLBWR_CG_MASK`, and `DISABLE_TLBRD_CG_MASK` depending on `AMD_CG_SUPPORT_MC_MGCG`. `mmhub_v2_3_get_clockgating()` reads the same masks to report whether medium-grain memory-controller clock gating is active.

## State And Persistence Behavior

The header itself has no state. The hardware registers described by these macros are persistent device state until reset, suspend/resume reprogramming, driver reinitialization, or another MMIO write changes them.

Important state classes represented in this chunk include:

- DAGB credit state: write TLB/data/misc/OSD/FIFO/atomic credit limits, pool credits, maximum packet length, and credit-full indications.
- DAGB diagnostic and status state: pending busy vectors, FIFO empty/full bits, performance-counter selection/mode/enable/clear state, and current counter low/high words.
- DAGB power/clock and parity state: clock-gating disable bits, EA busy disable bits, parity check enable, and read-return FIFO credit policy.
- MMEA0 QoS state: client-to-group maps, group-to-virtual-channel maps, lazy accumulation, CAM allocation, burst limits, age/queue/fixed/urgency coefficients, urgency masking, quantum thresholds, and SDP priority values.
- MMEA0 address-routing state: base/limit/offset windows, fabric destination, interleave topology, DRAM holes, non-power-of-two channel sizing, bank/chip-select/pseudo-channel hashing, harvest enable/ranges, chip-select masks/configuration, and GECC harvest adjustment.
- MMEA0 SDP state: burst arbitration, read-only virtual-channel flags, error/halt on error policy, throttles, tag/response credits, per-VC reservations, request blocking levels, chain overrides, and link-manager thresholds.
- MMEA0 observability state: latency-sampling filter selection for traffic class, operation type, atomic type, and virtual channel.

Several fields have side effects or control liveness rather than merely storing configuration. Counter `CLEAR`/`CLEAR_ALL`, request block levels, halt-on-error, throttles, clock-gating disable bits, snoop override, and parity/check/error policy fields should be treated as active hardware controls.

## Dependencies And Integration Points

Direct dependencies:

- `mmhub_2_3_0_offset.h` supplies matching register address macros such as `mmDAGB0_CNTL_MISC2`; this `_sh_mask.h` file only supplies field layout.
- `mmhub_2_3_0_default.h` supplies reset/default values for this generation.
- AMDGPU register helpers and SOC15 MMIO helpers consume the generated mask/shift names.

Observed integration in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v2_3.c` includes `mmhub/mmhub_2_3_0_sh_mask.h`, `mmhub_2_3_0_offset.h`, and `mmhub_2_3_0_default.h`.
- The concrete in-chunk use in `mmhub_v2_3.c` is `DAGB0_CNTL_MISC2` clock-gating mask handling for medium-grain memory-controller clock gating and clock-gating status reporting.
- Other fields in this chunk are ABI surface for generated-register consumers, hardware bring-up, debug/perf tooling, RAS/error-policy flows, and firmware or table-driven programming paths even when there is no local textual reference to each macro in this tree snapshot.

Cross-generation integration matters. Similar `DAGB0_*` and `MMEA0_*` macros exist in other MMHUB generated headers, but bit positions and available fields differ by ASIC generation. Consumers must include the matching `mmhub_2_3_0_*` files for MMHUB 2.3 hardware rather than substituting a nearby generation.

## Risks And Edge Cases

Bitfield drift is the primary risk. These constants are generated from hardware register specifications; if a shift or mask is wrong, driver code may silently program the wrong bits in a 32-bit MMIO register.

Packed fields are common and fragile:

- Client-to-group maps pack sixteen 2-bit client fields into one word.
- Urgency masking packs one bit for each of 32 clients.
- Priority, quantum, credit, reservation, and VC-map registers pack multiple independent policy fields into one register.
- Address-decoder registers pack topology selectors, masks, and chip-select controls where a single incorrect field can affect a large address range.

Status, command, and configuration fields share the same naming convention. For example, `BUSY`, `EMPTY`, `FULL`, and counter-value fields are observed status, while `CLEAR`, `CLEAR_ALL`, request-block, throttle, halt-on-error, snoop-override, and clock-gating-disable fields actively change hardware behavior. Code review should verify access direction and side effects against the register specification, not just the macro name.

Power and clock-gating fields are liveness-sensitive. `DAGB0_CNTL_MISC2` clock-gating disables are used by `mmhub_v2_3.c`; accidentally setting or clearing the wrong bit can leave request/return/TLB clock domains ungated, gated at the wrong time, or misreported in clock-gating status.

Address normalization and DRAM decode fields are correctness-sensitive. Misprogramming `MMEA0_ADDRNORM_*`, `ADDRDEC_*`, hash, harvest, or chip-select selection fields can route memory accesses incorrectly, break interleave assumptions, expose harvested regions, or cause data corruption/hangs.

The chunk ends inside `MMEA0_LATENCY_SAMPLING`, so this document must not be treated as a complete description of all MMEA0 observability/performance/error controls. Later chunks continue the register family.

## Test And Validation Signals

Useful validation is mostly build, register-generation, and hardware behavior coverage:

- Build AMDGPU code that includes `mmhub/mmhub_2_3_0_sh_mask.h`; this catches missing, renamed, or syntactically invalid macro definitions.
- Exercise `mmhub_v2_3_set_clockgating()` and `mmhub_v2_3_get_clockgating()` with `AMD_CG_SUPPORT_MC_MGCG` and confirm `DAGB0_CNTL_MISC2` read/modify/write only changes the intended clock-gating disable bits.
- Compare this header against the authoritative AMD MMHUB 2.3 register database, especially `DAGB0_CNTL_MISC2`, packed DAGB credit controls, `MMEA0_ADDRNORM_*`, `MMEA0_ADDRDEC*`, hash/harvest fields, IO urgency masks, and SDP request/credit registers.
- Use representative `REG_SET_FIELD`/`REG_GET_FIELD` checks for packed fields such as `MMEA0_DRAM_RD_CLI2GRP_MAP0__CID15_GROUP`, `MMEA0_IO_RD_PRI_URGENCY_MASKING__CID31`, `MMEA0_SDP_ARB_FINAL__GMI_WR_THROTTLE`, and `DAGB0_WR_DATA_FIFO_CREDIT_CNTL1__FIX2`.
- On hardware or simulator, read back MMHUB 2.3 registers after initialization and clock-gating transitions to verify default values, intended field updates, and preservation of unrelated fields.
- Run GPU reset, suspend/resume, and power-management tests because hardware register state in this chunk is reset/reprogrammed across those flows.
- Run memory stress and MMHUB client traffic tests that exercise DRAM and IO read/write clients; failures may show as hangs, timeout recovery, protection faults, degraded bandwidth, or unfair client service if group/VC/priority/credit fields are wrong.
- Use performance-counter and latency-sampling smoke tests where available to confirm DAGB counter enable/clear/select behavior and MMEA0 sampler filters select expected traffic classes and virtual channels.
