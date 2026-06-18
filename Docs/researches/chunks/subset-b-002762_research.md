# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 9436-11789

## Scope And Purpose

This chunk is a generated AMD MMHUB 1.7 register shift/mask header slice. It contains C preprocessor constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>__SHIFT` value and a matching `<REGISTER>__<FIELD>_MASK` value. There are no functions, structs, enums, global storage objects, or executable control-flow paths in this range.

The line range starts in the tail of `DAGB5_RD_ADDR_DAGB_MAX_BURST0` with only the `CLIENT6` and `CLIENT7` masks present in this chunk, then covers the rest of the `DAGB5` read/write data-arbitration register field vocabulary. It then enters `addressBlock: mmhub_ea_mmeadec0` and covers the beginning of `MMEA0` DRAM/GMI client grouping, priority, CAM, lazy-timer, page-burst, and address-normalization field definitions. The range ends at the `MMEA0_ADDRNORMGMI_HOLE_CNTL` register comment; that register's field definitions continue in the next chunk.

The purpose of the chunk is to provide symbolic bit layouts for MMHUB data-arbitration and memory/EA address-decoder registers used by the AMDGPU MMHUB 1.7 support code. Consumers combine these macros with register offsets from `mmhub/mmhub_1_7_offset.h` and register access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, and raw `RREG32`/`WREG32` paths.

## Macro Interface

The exported interface is entirely macro based:

- `<REG>__<FIELD>__SHIFT` gives the right shift count for a field.
- `<REG>__<FIELD>_MASK` gives the bit mask in the 32-bit register word.
- Packed client, virtual-channel, group, and threshold registers use repeated low-nibble or byte lanes, such as `0x0000000f`, `0x000000f0`, or `0x000000ff`.
- Full-width status/counter fields and reserve registers use broad masks where appropriate; this chunk mainly uses packed control/status fields rather than whole-register data ports.

Typical consumers either use local AMDGPU helpers that expand through the mask/shift naming convention or perform explicit read-modify-write packing:

```c
field = (value & REG__FIELD_MASK) >> REG__FIELD__SHIFT;
value = (value & ~REG__FIELD_MASK) |
        ((new_field << REG__FIELD__SHIFT) & REG__FIELD_MASK);
```

The header does not constrain values before shifting and does not encode whether a field is read-only, write-one-to-clear, pulse, latched status, or persistent configuration. Those semantics are owned by the hardware register documentation and the driver code that sequences MMIO access.

## Register Families Covered

### DAGB5 Read-Side Arbitration And Credits

The opening `DAGB5_RD_*` section covers read-side behavior for the fifth DAGB instance. It includes:

- `DAGB5_RD_ADDR_DAGB_MAX_BURST*` and `DAGB5_RD_ADDR_DAGB_LAZY_TIMER*`: per-client burst and lazy-delay controls. The `0` register is partial in this chunk; client 0-5 definitions are in the previous chunk while client 6-7 masks and the complete lazy timer are here. The `1` register covers clients 8-15.
- `DAGB5_RD_VC0_CNTL` through `DAGB5_RD_VC7_CNTL`: per-virtual-channel storage and EA credits, max/min bandwidth enable and values, OSD limiter enable, and max outstanding controls.
- `DAGB5_RD_CNTL_MISC`, `DAGB5_RD_TLB_CREDIT`, `DAGB5_RD_RDRET_CREDIT_CNTL`, and `DAGB5_RD_RDRET_CREDIT_CNTL2`: pool, TLB, read-return, IO, GMI, and VC credit accounting.
- `DAGB5_RDCLI_*_PENDING`: busy/status bits for ask, go, global-send, TLB, OARB, and OSD read-client paths.

These fields form the bit-level contract for read request arbitration, outstanding credit limits, and status polling in the MMHUB DAGB.

### DAGB5 Write-Side Client, DAGB, Credit, And Clock Controls

The write-side `DAGB5_WR*` section is the largest part of the DAGB block in this range:

- `DAGB5_WRCLI0` through `DAGB5_WRCLI15` define each write client's virtual-channel assignment, TLB-credit checking, high/low urgency thresholds, max/min bandwidth controls, and OSD limiter/max-outstanding fields.
- `DAGB5_WR_CNTL` exposes SCLK frequency/window fields, IO-level override, shared-VC selection, and fixed-jump behavior.
- `DAGB5_WR_GMI_CNTL`, `DAGB5_WR_ADDR_DAGB`, `DAGB5_WR_DATA_DAGB`, and the output/address/data `MAX_BURST` and `LAZY_TIMER` registers tune write request routing and batching across output VCs, address clients, and data clients.
- `DAGB5_WR_CGTT_CLK_CTRL`, `DAGB5_L1TLB_WR_CGTT_CLK_CTRL`, and `DAGB5_ATCVM_WR_CGTT_CLK_CTRL` define clock-gating/light-sleep style delay and override bits for write, L1 TLB write, and ATC/VM write subpaths.
- `DAGB5_WR_TLB_CREDIT`, `DAGB5_WR_DATA_CREDIT`, `DAGB5_WR_MISC_CREDIT`, `DAGB5_WR_OSD_CREDIT_CNTL1/2`, and `DAGB5_WR_ATOMIC_FIFO_CREDIT_CNTL1` define write-side TLB, data-burst, OSD, atomic FIFO, pool, IO, GMI, deadlock-VC, and legacy credit controls.
- `DAGB5_WRCLI_GPU_SNOOP_OVERRIDE`, `DAGB5_WRCLI_GPU_SNOOP_OVERRIDE_VALUE`, and the `DAGB5_WRCLI_*_PENDING`/`DBUS_*_PENDING` status bits expose write-client snoop and pending-state behavior.

These constants are relevant to bandwidth shaping, request batching, clock gating, GPU snoop control, and hang diagnosis for MMHUB write traffic.

### DAGB5 Diagnostics, Fatal Error, And Performance Counters

The diagnostic tail of the DAGB block includes:

- `DAGB5_DAGB_DLY`, `DAGB5_CNTL_MISC`, and `DAGB5_CNTL_MISC2`: delay injection, VC remap, bandwidth timing windows, urgency boost/halt, clock-gating disables, busy-disable controls, swap controls, HDP CID, and read-return FIFO/deadlock-credit fields.
- `DAGB5_FATAL_ERROR_CNTL`, `DAGB5_FATAL_ERROR_CLEAR`, and `DAGB5_FATAL_ERROR_STATUS0` through `STATUS3`: fatal-error filter selection, clear bit, validity, client ID, address low/high, tag, VF/VFID, space/IO/size/FED attributes, and operation/snoop/nack/ordering/memlog/EOP status fields.
- `DAGB5_FIFO_EMPTY`, `DAGB5_FIFO_FULL`, `DAGB5_WR_CREDITS_FULL`, and `DAGB5_RD_CREDITS_FULL`: one-bit status fields for FIFO and credit fullness/emptiness.
- `DAGB5_PERFCOUNTER_LO`, `DAGB5_PERFCOUNTER_HI`, `DAGB5_PERFCOUNTER0_CFG` through `2_CFG`, and `DAGB5_PERFCOUNTER_RSLT_CNTL`: event selection, end event, mode, enable, clear, counter low/high, compare value, start/stop triggers, clear-all, enable-any, and stop-on-saturate controls.
- `DAGB5_L1TLB_REG_RW` and `DAGB5_RESERVE1` through `RESERVE4`: L1 TLB register read/write control, VMID exception interrupt control, parity/read-return checking controls, and reserve fields.

These fields are primarily consumed by debug, RAS-like diagnosis, performance counter setup, and low-level bring-up validation. Mis-decoding fatal error fields can lead to incorrect fault attribution even if the underlying hardware error is real.

### MMEA0 DRAM And GMI Grouping, Arbitration, And Priority

After `addressBlock: mmhub_ea_mmeadec0`, the chunk defines the beginning of the MMEA0 address/arbiter register vocabulary for DRAM and GMI paths:

- `MMEA0_DRAM_RD_CLI2GRP_MAP0/1`, `MMEA0_DRAM_WR_CLI2GRP_MAP0/1`, `MMEA0_GMI_RD_CLI2GRP_MAP0/1`, and `MMEA0_GMI_WR_CLI2GRP_MAP0/1`: map client IDs 0-31 into four arbitration groups. Each client field is two bits.
- `*_GRP2VC_MAP`: map groups 0-3 to virtual channels.
- `*_LAZY`: per-group delay plus request accumulation threshold, timeout, and idle-max fields.
- `*_CAM_CNTL`: per-group CAM depth, per-group reorder limit, and refill-chain controls. GMI variants also include `PAGEBASED_CHAINING`.
- `*_PAGE_BURST`: read/write low/high page burst limits.
- `*_PRI_AGE`, `*_PRI_QUEUING`, `*_PRI_FIXED`, `*_PRI_URGENCY`, and `*_PRI_QUANT_PRI1/2/3`: per-group coefficients, urgency modes, and threshold levels used by the DRAM and GMI arbitration priority model.
- `MMEA0_GMI_RD_PRI_URGENCY_MASKING` and `MMEA0_GMI_WR_PRI_URGENCY_MASKING`: per-CID urgency masking for client IDs 0-31 on GMI read and write paths.

This section expresses how MMHUB EA traffic is grouped and prioritized before it reaches DRAM or GMI fabric paths. It is not a software scheduler by itself; it defines the bitfields used to program hardware arbitration policy.

### MMEA0 Address Normalization

The last complete block in this chunk begins the `MMEA0_ADDRNORM*` address-normalization registers:

- `MMEA0_ADDRNORM_BASE_ADDR0` through `BASE_ADDR3` and `MMEA0_ADDRNORM_MEGABASE_ADDR0/1`: range valid, legacy MMIO hole enable, interleave channel/die/socket counts, interleave address select, and base-address fields.
- `MMEA0_ADDRNORM_LIMIT_ADDR0` through `LIMIT_ADDR3` and `MMEA0_ADDRNORM_MEGALIMIT_ADDR0/1`: destination fabric ID and limit-address fields.
- `MMEA0_ADDRNORM_OFFSET_ADDR1` and `OFFSET_ADDR3`: high-address offset enable and high-address offset fields.
- `MMEA0_ADDRNORMDRAM_HOLE_CNTL`: DRAM hole valid and hole offset fields.
- `MMEA0_ADDRNORMGMI_HOLE_CNTL`: only the register comment appears at the final line in this chunk; its field definitions are outside this line range.

These fields are part of the hardware address-routing contract. Incorrect packing can route memory transactions to the wrong fabric destination, mishandle interleaving, or misrepresent MMIO/DRAM holes.

## Control Flow And State Behavior

There is no local control flow in this header. Runtime behavior appears only when other code includes it and performs MMIO reads or writes.

The state represented by these macros is hardware state:

- DAGB read/write arbitration and credit fields persist in MMHUB registers until reset or reprogramming by initialization, power-management, clock-gating, debug, or recovery code.
- Pending, FIFO, full, fatal-error, and performance-counter fields are observed hardware state. Some fields are latched status or command/clear bits, but this header does not document those write semantics.
- MMEA0 grouping, VC mapping, priority coefficients, CAM controls, and address-normalization fields persist as programmed hardware policy for DRAM/GMI routing and arbitration.
- Performance counters have explicit enable/clear/start/stop control fields and low/high result fields. The masks allow programming and reading counters, but counter lifetime and sampling rules are implemented by the hardware and consuming driver paths.

The primary control-flow integration point is `amdgpu/mmhub_v1_7.c`, which includes `mmhub/mmhub_1_7_offset.h` and this shift/mask header. That file initializes MMHUB VM/GART apertures, TLB/cache registers, snoop overrides, VMID settings, invalidation, fault handling, clock gating, and RAS query/reset paths. This exact chunk is not a function body, but its `DAGB5_*` and `MMEA0_*` definitions are part of the same register namespace used by that implementation and by `SOC15_REG_FIELD`/`REG_GET_FIELD` style access.

## Dependencies And Integration Points

- Companion offsets live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_offset.h`; this source tree does not have a `mmhub_1_7_d.h` companion for this generated header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c` directly includes this header and registers `mmhub_v1_7_funcs` and `mmhub_v1_7_ras` for the MMHUB 1.7 block.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c` selects `mmhub_v1_7_funcs` and `mmhub_v1_7_ras` for matching ASIC paths, tying this register vocabulary into GMC/GART setup and VM management.
- Register access is through SOC15 MMIO helpers (`RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `RREG32`, `WREG32`) and field helpers that rely on the exact generated naming convention.
- RAS integration in `mmhub_v1_7.c` uses `SOC15_REG_FIELD` definitions for MMEA EDC/error status fields elsewhere in the same header. The MMEA priority/address-normalization fields in this chunk are adjacent to those RAS-visible MMEA blocks and share the same register address space.
- Debug and validation tools can use the DAGB fatal-error, FIFO, credit, pending, and performance-counter field definitions to decode MMHUB hangs, traffic stalls, or bandwidth anomalies.

## Risks And Edge Cases

- The chunk boundaries split registers. `DAGB5_RD_ADDR_DAGB_MAX_BURST0` begins before line 9436, so this chunk only contains the tail masks for clients 6 and 7. `MMEA0_ADDRNORMGMI_HOLE_CNTL` begins at line 11789 but its fields are in the next chunk. Merge/reconciliation must not treat either partial register as complete based only on this file.
- Hardware contract drift is the main risk. A stale mask or shift can program the wrong client, VC, credit, urgency coefficient, fabric ID, base/limit address, or clear/status bit.
- Many fields are packed repeated lanes. Off-by-one client numbering or using a client 0-15 register where a client 16-31 register is required can silently modify the wrong arbitration group or priority mask.
- Address-normalization masks are high impact. Misprogramming `ADDR_RNG_VAL`, interleave fields, fabric destination IDs, base/limit addresses, hole controls, or high-address offsets can cause bad routing, memory holes, failed access to VRAM/system memory, or device hangs.
- Credit and OSD limiter fields can throttle or deadlock traffic if programmed outside valid hardware ranges. The header provides masks but does not validate maximum legal values or ordering between pool, VC, IO, GMI, TLB, and data credits.
- Clock-gating/light-sleep override fields can alter power behavior and timing. Incorrect read-modify-write code may disable intended gating or force hardware subblocks on/off unexpectedly.
- Fatal-error and clear/status fields require semantic care. The presence of masks for `CLEAR`, `VALID`, `FED`, `NACK`, and operation/status fields does not define whether writes are pulse, level, clear-on-write, or read-only.
- Similar `DAGB*` and `MMEA*` names exist across MMHUB generations. Consumers must use the MMHUB 1.7 offset and mask headers together; mixing with MMHUB 1.0, 1.8, 9.4, or 9.3.0 masks can compile but produce wrong register programming.

## Test And Validation Signals

There are no direct unit tests for these generated macro definitions. Useful validation signals are integration-level and hardware/static consistency checks:

- Build coverage for AMDGPU files that include `mmhub_1_7_sh_mask.h`, especially `amdgpu/mmhub_v1_7.c` and the `gmc_v9_0.c` paths that select MMHUB 1.7 functions.
- Static generated-header checks: every complete field should have both a `__SHIFT` and `_MASK`, single-bit masks should match the shift, contiguous multi-bit masks should collapse to dense low-bit fields after shifting, and repeated client/group lanes should follow the expected 2-bit, 4-bit, or 8-bit stride.
- Register namespace consistency against `mmhub_1_7_offset.h`: `regDAGB5_*`/`mmDAGB5_*` and `regMMEA0_*` offsets should exist for mask families used by driver code or diagnostic tooling.
- MMHUB bring-up smoke tests should initialize GART, VMID, cache/TLB, invalidation, fault, and clock-gating paths without invalid MMIO access warnings or hangs.
- Hardware validation can program DAGB performance counters, use result-control start/stop/clear fields, and verify low/high counters move and clear as expected.
- Stress tests that generate MMHUB traffic should avoid persistent `DAGB5_*_PENDING`, FIFO full, credit full, or fatal-error status after normal operation.
- RAS and hang diagnostics should correctly decode fatal error address, CID, VF/VFID, operation, NACK, and FED fields when errors are injected or observed on supported hardware.
- Address-normalization validation should check that DRAM/GMI ranges, interleaving, fabric IDs, holes, and high-address offsets match firmware/BIOS expectations and do not break VRAM/system-memory access.

## Chunk Notes For Merge Lane

This is one source-tree-aligned chunk of `mmhub_1_7_sh_mask.h`, not a final whole-file report. In whole-file reconciliation, combine it with neighboring chunks for the complete `DAGB5_RD_ADDR_DAGB_MAX_BURST0` and `MMEA0_ADDRNORMGMI_HOLE_CNTL` definitions. The main contribution of this range is late `DAGB5` read/write arbitration, DAGB5 diagnostics/perf/fatal-error masks, and the beginning of `MMEA0` DRAM/GMI arbitration plus address-normalization masks.
