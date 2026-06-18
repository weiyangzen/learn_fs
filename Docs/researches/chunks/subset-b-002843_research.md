# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 4724-7102

## Scope

This chunk covers the middle of the generated AMDGPU MMHUB 9.4.1 shift/mask header. The range starts inside the `mmhub_dagb_dagbdec2` address block, completing the later `DAGB2_WR_*` write-side virtual-channel, credit, status, snoop, misc, FIFO, counter, and reserve definitions. It then covers the complete visible `mmhub_dagb_dagbdec3` block for `DAGB3`, and ends just after the first shift definition of `DAGB4_RD_GMI_CNTL` in the next `mmhub_dagb_dagbdec4` block.

The source is hardware register metadata, not executable driver logic. It defines preprocessor constants named as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. The matching register offsets are in `mmhub_9_4_1_offset.h`; consumers pair those offsets with the masks here through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15_OFFSET`, and `WREG32_SOC15_OFFSET`.

Although the repository path is under `sources/distributed-fs/ceph-client`, this chunk belongs to Linux DRM AMDGPU register programming. It has no Ceph client, distributed filesystem, networking, or storage-protocol behavior.

## Purpose

The purpose of this chunk is to provide the bit-level ABI for programming and decoding MMHUB 9.4.1 DAGB decoder instances. DAGB blocks arbitrate and meter memory-hub traffic by client and virtual channel. The fields in this range describe virtual-channel routing, TLB-credit checking, urgency thresholds, max/min bandwidth controls, outstanding-operation limits, output and per-client burst/timer tuning, clock-gating overrides, read/write credit pools, pending-status bitmaps, write-client GPU snoop overrides, FIFO/credit status, and DAGB performance counters.

The exact values are important because each register is a packed 32-bit MMIO word. Driver code can use symbolic names instead of literal bit positions, but the correctness of every later read/modify/write depends on these masks matching the hardware register database for MMHUB 9.4.1.

## Important APIs, Types, And Macro Families

There are no functions, structs, enums, variables, or callable APIs in this range. The exported interface is the macro namespace.

The `DAGB2_WR_*` opening slice completes the write-side controls for DAGB instance 2. It starts at the tail of `DAGB2_WR_VC1_CNTL`, then defines `DAGB2_WR_VC2_CNTL` through `DAGB2_WR_VC7_CNTL`. Each virtual-channel control register uses the same packed fields: storage credit, EA credit, maximum bandwidth enable/value, minimum bandwidth enable/value, OSD limiter enable, and maximum OSD. The same DAGB2 tail also defines write-side miscellaneous pool credits (`STOR_POOL_CREDIT`, `EA_POOL_CREDIT`, `IO_EA_CREDIT`, legacy mode bits, `UTCL2_CID`, and read-return FIFO credits), six TLB credit lanes, data burst credits, atomic/DLOCK/OSD miscellaneous credits, write-pipeline pending status bitmaps, full-width GPU snoop override enable/value bitmaps, delay selection, misc control fields, FIFO empty/full status, read/write credit-full status, performance counter registers, result-control fields, and `DAGB2_RESERVE0` through `DAGB2_RESERVE13`.

The `DAGB3_RDCLI0` through `DAGB3_RDCLI15` group defines the repeated per-read-client arbitration layout for DAGB instance 3. Each client register exposes `VIRT_CHAN`, `CHECK_TLB_CREDIT`, `URG_HIGH`, `URG_LOW`, `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `OSD_LIMITER_ENABLE`, and `MAX_OSD`. The matching `DAGB3_WRCLI0` through `DAGB3_WRCLI15` group repeats that layout for write clients.

`DAGB3_RD_CNTL` and `DAGB3_WR_CNTL` define aggregate read/write policy: SCLK frequency encoding, client and virtual-channel max-bandwidth windows, IO-level override, IO-level value, IO-level-compliant VC selection, and shared VC count. `DAGB3_RD_GMI_CNTL` and `DAGB3_WR_GMI_CNTL` define EA credit, level, max burst, and lazy-timer fields for GMI traffic.

`DAGB3_RD_ADDR_DAGB`, `DAGB3_WR_ADDR_DAGB`, and `DAGB3_WR_DATA_DAGB` describe core DAGB enable and identity controls: enable lanes, jump-ahead enable, self-init disable, and `WHOAMI`. The read and write address/output/data burst and lazy-timer families use 4-bit lanes. Output DAGB registers pack virtual channels 0-7 into one word, while address/data DAGB max-burst and lazy-timer registers split clients 0-7 and 8-15 into `...0` and `...1` words.

Clock and light-sleep control is represented by `DAGB3_RD_CGTT_CLK_CTRL`, `DAGB3_WR_CGTT_CLK_CTRL`, `DAGB3_L1TLB_RD_CGTT_CLK_CTRL`, `DAGB3_L1TLB_WR_CGTT_CLK_CTRL`, `DAGB3_ATCVM_RD_CGTT_CLK_CTRL`, and `DAGB3_ATCVM_WR_CGTT_CLK_CTRL`. These registers share `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_STALL_OVERRIDE`, and several `LS_OVERRIDE*` fields for write/read/return/register paths.

`DAGB3_RD_VC0_CNTL` through `DAGB3_RD_VC7_CNTL` and `DAGB3_WR_VC0_CNTL` through `DAGB3_WR_VC7_CNTL` define virtual-channel credit, bandwidth, and outstanding-depth policy. They share the storage credit, EA credit, max/min bandwidth enable/value, OSD limiter, and max OSD field layout also seen in the DAGB2 tail.

Credit and status registers include `DAGB3_RD_CNTL_MISC`, `DAGB3_RD_TLB_CREDIT`, `DAGB3_WR_CNTL_MISC`, `DAGB3_WR_TLB_CREDIT`, `DAGB3_WR_DATA_CREDIT`, and `DAGB3_WR_MISC_CREDIT`. These fields control or report pool credits, UTCL2 IDs, TLB lanes, burst credits, DLOCK VC credits, atomic credits, and OSD credits.

Pending-status groups include `DAGB3_RDCLI_ASK_PENDING`, `DAGB3_RDCLI_GO_PENDING`, `DAGB3_RDCLI_GBLSEND_PENDING`, `DAGB3_RDCLI_TLB_PENDING`, `DAGB3_RDCLI_OARB_PENDING`, `DAGB3_RDCLI_OSD_PENDING`, and the corresponding `DAGB3_WRCLI_*_PENDING` write-side registers. The write side additionally has `DAGB3_WRCLI_DBUS_ASK_PENDING` and `DAGB3_WRCLI_DBUS_GO_PENDING`. These expose full-width `BUSY` bitmaps.

`DAGB3_WRCLI_GPU_SNOOP_OVERRIDE` and `DAGB3_WRCLI_GPU_SNOOP_OVERRIDE_VALUE` expose full-width per-write-client enable/value masks. The concrete C integration in `drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c` programs this register family: `mmhub_v9_4_init_snoop_override_regs()` computes the spacing between `mmDAGB1_WRCLI_GPU_SNOOP_OVERRIDE` and `mmDAGB0_WRCLI_GPU_SNOOP_OVERRIDE`, iterates the DAGB instances assigned to each MMHUB, and sets bit 15 in both the override and override-value registers for the SDMA client.

`DAGB3_DAGB_DLY`, `DAGB3_CNTL_MISC`, and `DAGB3_CNTL_MISC2` contain cross-cutting controls such as delay selection, bandwidth-init cycle/gap timing, busy override, swap control, read-return FIFO performance control, and tap-chain clock-gating disable fields. `DAGB3_FIFO_EMPTY`, `DAGB3_FIFO_FULL`, `DAGB3_WR_CREDITS_FULL`, and `DAGB3_RD_CREDITS_FULL` expose FIFO and credit fullness/emptiness status bitmaps.

`DAGB3_PERFCOUNTER_LO`, `DAGB3_PERFCOUNTER_HI`, `DAGB3_PERFCOUNTER0_CFG`, `DAGB3_PERFCOUNTER1_CFG`, `DAGB3_PERFCOUNTER2_CFG`, and `DAGB3_PERFCOUNTER_RSLT_CNTL` define the DAGB3 performance counter block. The fields cover low/high counter words, compare value, event-select start/end, counter mode, enable, clear, result counter select, start/stop triggers, enable-any, clear-all, and stop-on-saturate.

The end of the `DAGB3` block defines `DAGB3_RESERVE0` through `DAGB3_RESERVE13` as full-width reserved fields. This is a version-specific detail: similarly shaped regions in some neighboring MMHUB headers include fatal-error or indirect L1TLB control registers, but the visible MMHUB 9.4.1 range here ends the DAGB3 block with reserve registers.

The final lines begin `DAGB4_RDCLI0` through `DAGB4_RDCLI15`, `DAGB4_RD_CNTL`, and only the first shift of `DAGB4_RD_GMI_CNTL`. The complete DAGB4 read GMI masks and later DAGB4 read/write controls continue in the next chunk.

## Control Flow

This chunk has no runtime control flow. It does not call functions, branch, allocate memory, perform IO, acquire locks, or access hardware directly.

Runtime behavior appears in consuming AMDGPU code. A typical flow is: include the offset and shift/mask headers, read a 32-bit MMHUB register with a SOC15 helper, compose or decode fields with `REG_SET_FIELD` or `REG_GET_FIELD`, and write the result back with a SOC15 helper. `mmhub_v9_4.c` follows this pattern broadly for MMHUB VM/cache/TLB setup and directly uses the DAGB register spacing and write-client snoop override register family covered by this chunk.

The generated macros influence control flow only indirectly: a caller may branch based on decoded pending, FIFO, credit, or performance-counter status, or may choose different initialization paths depending on hardware instance and SR-IOV mode. Those decisions are not represented in this header.

## State And Persistence Behavior

The macros themselves have no state and persist nothing. They are compile-time constants.

The state described by the macros is MMIO-backed hardware state inside MMHUB. Configuration fields such as VC assignment, credit budgets, bandwidth windows, OSD limits, burst/lazy timers, clock-gating overrides, snoop override bits, and counter selection persist in hardware until reset, power gating, firmware programming, suspend/resume restore, or driver reprogramming changes them. Status fields such as pending bitmaps, FIFO empty/full, credit-full flags, and performance counter values are hardware-maintained and can change while traffic is active.

Several fields are command-like or sequencing-sensitive rather than durable policy: performance counter clear bits, clear-all, start/stop triggers, busy overrides, snoop override enable/value bitmaps, and any status registers with latched or side-effect semantics. This generated header does not encode access direction, write-one-to-clear rules, polling requirements, or reset ordering.

## Dependencies And Integration Points

The immediate companion dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_offset.h`. In that file, examples from this range include `mmDAGB2_WR_VC2_CNTL` at `0x014f`, `mmDAGB3_RDCLI0` at `0x0180`, `mmDAGB3_WRCLI0` at `0x01ac`, `mmDAGB3_WR_VC0_CNTL` at `0x01cd`, `mmDAGB4_RDCLI0` at `0x0200`, and `mmDAGB4_RD_GMI_CNTL` at `0x0211`, all using base index 1. The masks here are meaningful only when paired with those offsets and the correct SOC15 MMHUB instance.

The main C integration point in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, which includes `mmhub_9_4_1_offset.h`, `mmhub_9_4_1_sh_mask.h`, and `mmhub_9_4_1_default.h`. That file initializes MMHUB apertures, VM page-table bases, L1/L2 cache and TLB controls, VMID contexts, invalidation, protection fault handling, and DAGB snoop overrides for the two MMHUB instances. The specific DAGB code sets SDMA snoop override bit 15 across DAGB instances 0-4 in hub 0 and 5-7 in hub 1 by using the repeated DAGB register offset spacing.

Additional dependencies are the AMDGPU SOC15 register access layer, common register-field helpers, the generated `mmhub_9_4_1_default.h` defaults for reset/default values, and the underlying AMD register database that generated this header. Cross-generation similarity with headers such as `mmhub_1_8_0_sh_mask.h` is useful for review, but client counts, reserved regions, base indices, offsets, and field layouts must remain version-specific.

## Risks And Edge Cases

The largest risk is hardware ABI drift. A single wrong shift or mask can silently write unrelated bits in a packed MMHUB register, causing bad traffic routing, throttling, credit starvation, hangs, false pending status, incorrect power behavior, or misleading performance data.

The repeated client, VC, and DAGB-instance families are easy to review incorrectly. `RDCLI0..15`, `WRCLI0..15`, VC0..VC7 controls, burst/timer lanes, and pending masks look highly regular, so an isolated generator error in one index can evade visual inspection.

Read-side and write-side blocks are similar but not identical. Write-side blocks include data DAGB controls, data credits, miscellaneous atomic/DLOCK/OSD credits, DBUS pending status, and GPU snoop override fields. Callers must not substitute read macros for write registers or assume every read-side field has a write-side twin.

Several masks are full-width `0xFFFFFFFFL` values. Code and diagnostics should treat them as 32-bit register fields and avoid signed-format or host-width assumptions that obscure the intended bitmap semantics.

Status and control registers share the same macro style. Pending, FIFO, credit-full, performance counter result, and reserve fields should not be treated as ordinary writable policy. The header does not mark read-only, write-only, reserved, sticky, or self-clearing fields.

Clock-gating and light-sleep override fields can affect power and reset sequencing. Misprogramming `SOFT_STALL_OVERRIDE` or `LS_OVERRIDE*` bits can force a block active, hide true busy state, or interfere with low-power entry.

Snoop override fields are integration-sensitive. `mmhub_v9_4_init_snoop_override_regs()` relies on DAGB register spacing and SDMA client bit 15. A mismatch between offset spacing, hub instance mapping, or bitmap width can set the wrong client override.

The chunk boundary matters. It starts after part of `DAGB2_WR_VC1_CNTL` and ends before `DAGB4_RD_GMI_CNTL` is complete, so the final per-file report must merge adjacent chunks before making complete statements about DAGB2 and DAGB4.

## Test Signals

There are no unit tests for this macro-only chunk. Useful validation is build-time, static, and hardware-observation based:

- Compile AMDGPU code that includes `mmhub_9_4_1_sh_mask.h`, especially `mmhub_v9_4.c`, to catch missing or renamed register-field macros.
- Mechanically compare the header against the authoritative MMHUB 9.4.1 register database and verify that every `_MASK` is contiguous, aligned with its matching `__SHIFT`, and non-overlapping within a register.
- Cross-check this chunk with `mmhub_9_4_1_offset.h` so each covered register family has the expected `mmDAGB*` offset and base index.
- Inspect generated defaults in `mmhub_9_4_1_default.h` for covered counter/status/control registers, especially performance counter defaults and reserved register defaults.
- On MMHUB 9.4.1 hardware or simulator, run VM/GART initialization, memory traffic, SDMA traffic, compute, display, and reset/suspend/resume paths while checking for MMHUB faults, hangs, unexpected throttling, or broken snoop behavior.
- Read back `DAGB*_WRCLI_GPU_SNOOP_OVERRIDE` and `DAGB*_WRCLI_GPU_SNOOP_OVERRIDE_VALUE` after `mmhub_v9_4_init_snoop_override_regs()` and verify that SDMA client bit 15 is set in the intended DAGB instances for each hub.
- Exercise debug/performance paths that program `DAGB3_PERFCOUNTER*_CFG`, select results through `DAGB3_PERFCOUNTER_RSLT_CNTL`, read low/high counter words, and validate clear, trigger, and stop-on-saturate behavior.
- Under high traffic, sample pending, FIFO, and credit-full registers to confirm decoded bitmaps are plausible for active clients and do not show stuck busy/credit exhaustion after traffic drains.

## Chunk Notes For Merge Lane

This is a middle chunk of `mmhub_9_4_1_sh_mask.h`. It completes the visible tail of DAGB2 write controls, covers DAGB3 from read-client arbitration through reserved registers, and starts DAGB4 read controls through the first `DAGB4_RD_GMI_CNTL` shift. The merge lane should reconcile this with the previous chunk for complete DAGB2 coverage and with the next chunk for complete DAGB4 coverage before producing the final per-file research document.
