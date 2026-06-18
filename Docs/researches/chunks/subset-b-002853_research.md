# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 28444-30822

## Scope And Purpose

This chunk is a middle section of the generated AMDGPU MMHUB 9.4.1 register shift/mask header. It covers the tail of `mmhub_dagb_dagbdec5`, the complete `mmhub_dagb_dagbdec6` mask block, and the start of `mmhub_dagb_dagbdec7` through the shift definitions for `DAGB7_RDCLI9`. The range contains 2,181 `#define` entries: 1,092 shift constants and 1,089 mask constants.

The file is not executable code. It is a hardware register-field contract for MMHUB DAGB arbitration and status registers. Callers include it with the matching offset header and use macros such as `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` through AMDGPU helpers like `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15*`, and `WREG32_SOC15*`.

Within this chunk, the dominant purpose is to describe DAGB5 write-side completion controls, all DAGB6 read/write client arbitration controls, DAGB6 clock-gating, credit, pending, snoop override, FIFO, performance counter, and reserved registers, plus the beginning of DAGB7 read-client arbitration.

## Important APIs, Types, And Register Families

There are no local C functions, structs, enums, variables, or callable APIs in this chunk. The public interface is the macro namespace exported by `mmhub_9_4_1_sh_mask.h`.

Important covered register families include:

- `DAGB5_WR_ADDR_DAGB_MAX_BURST1`, `DAGB5_WR_ADDR_DAGB_LAZY_TIMER1`, `DAGB5_WR_DATA_DAGB`, `DAGB5_WR_DATA_DAGB_MAX_BURST[0-1]`, and `DAGB5_WR_DATA_DAGB_LAZY_TIMER[0-1]`: tail of DAGB5 write-address/write-data DAGB burst and lazy-timer programming. The max-burst and lazy-timer registers pack 4-bit client fields for clients 0-15 across low/high words.
- `DAGB5_WR_VC0_CNTL` through `DAGB5_WR_VC7_CNTL`: per-write-virtual-channel storage and EA credits, max/min bandwidth enable and values, OSD limiter enable, and max outstanding fields.
- `DAGB5_WR_CNTL_MISC`, `DAGB5_WR_TLB_CREDIT`, `DAGB5_WR_DATA_CREDIT`, and `DAGB5_WR_MISC_CREDIT`: write-side storage pool, EA pool, IO/EA, UTCL2 CID, RDRET FIFO, TLB, burst, atomic, DLOCK, and OSD credit packing.
- `DAGB5_WRCLI_*_PENDING`, `DAGB5_WRCLI_DBUS_*_PENDING`, `DAGB5_WRCLI_GPU_SNOOP_OVERRIDE`, and `DAGB5_WRCLI_GPU_SNOOP_OVERRIDE_VALUE`: full-width busy/status and snoop override bitmaps for write clients.
- `DAGB5_DAGB_DLY`, `DAGB5_CNTL_MISC`, `DAGB5_CNTL_MISC2`, FIFO/credit-full status, `DAGB5_PERFCOUNTER_*`, and `DAGB5_RESERVE0` through `DAGB5_RESERVE13`: delay selection, EA virtual-channel remap, bandwidth timing, urgent boost/halt, clock-gating disable bits, status fields, performance counters, and full-width reserved placeholders.
- `DAGB6_RDCLI0` through `DAGB6_RDCLI15` and `DAGB6_WRCLI0` through `DAGB6_WRCLI15`: per-client read/write controls. Each client uses the repeated layout `VIRT_CHAN`, `CHECK_TLB_CREDIT`, `URG_HIGH`, `URG_LOW`, `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `OSD_LIMITER_ENABLE`, and `MAX_OSD`.
- `DAGB6_RD_CNTL` and `DAGB6_WR_CNTL`: shared read/write arbitration controls for `SCLK_FREQ`, client and VC bandwidth windows, IO-level override and compliance fields, and shared VC count.
- `DAGB6_RD_GMI_CNTL` and `DAGB6_WR_GMI_CNTL`: GMI path credit, level, max-burst, and lazy-timer fields.
- `DAGB6_RD_ADDR_DAGB`, `DAGB6_WR_ADDR_DAGB`, and `DAGB6_WR_DATA_DAGB`: DAGB enable, jump-ahead enable, self-init disable, and `WHOAMI` fields for read address, write address, and write data paths.
- `DAGB6_RD_OUTPUT_DAGB_MAX_BURST`, `DAGB6_RD_OUTPUT_DAGB_LAZY_TIMER`, `DAGB6_WR_OUTPUT_DAGB_MAX_BURST`, and `DAGB6_WR_OUTPUT_DAGB_LAZY_TIMER`: 4-bit packed controls for output virtual channels 0-7.
- `DAGB6_RD_CGTT_CLK_CTRL`, `DAGB6_L1TLB_RD_CGTT_CLK_CTRL`, `DAGB6_ATCVM_RD_CGTT_CLK_CTRL`, `DAGB6_WR_CGTT_CLK_CTRL`, `DAGB6_L1TLB_WR_CGTT_CLK_CTRL`, and `DAGB6_ATCVM_WR_CGTT_CLK_CTRL`: clock/light-sleep controls with on-delay, off-hysteresis, soft-stall override, and light-sleep override bits for normal, L1TLB, and ATCVM read/write paths.
- `DAGB6_RD_ADDR_DAGB_MAX_BURST[0-1]`, `DAGB6_RD_ADDR_DAGB_LAZY_TIMER[0-1]`, `DAGB6_WR_ADDR_DAGB_MAX_BURST[0-1]`, `DAGB6_WR_ADDR_DAGB_LAZY_TIMER[0-1]`, `DAGB6_WR_DATA_DAGB_MAX_BURST[0-1]`, and `DAGB6_WR_DATA_DAGB_LAZY_TIMER[0-1]`: packed 4-bit per-client controls for clients 0-15.
- `DAGB6_RD_VC0_CNTL` through `DAGB6_RD_VC7_CNTL` and `DAGB6_WR_VC0_CNTL` through `DAGB6_WR_VC7_CNTL`: per-VC credit, bandwidth, OSD limiter, and max outstanding request controls.
- `DAGB6_RD_CNTL_MISC`, `DAGB6_WR_CNTL_MISC`, `DAGB6_RD_TLB_CREDIT`, `DAGB6_WR_TLB_CREDIT`, `DAGB6_WR_DATA_CREDIT`, and `DAGB6_WR_MISC_CREDIT`: pool and per-resource credit registers. TLB credits use packed 5-bit fields for TLB0-TLB5; data and misc credits use larger packed byte or sub-byte fields.
- `DAGB6_RDCLI_*_PENDING`, `DAGB6_WRCLI_*_PENDING`, and `DAGB6_WRCLI_DBUS_*_PENDING`: full-width `BUSY` bitmaps for ask, go, global-send, TLB, output-arbiter, OSD, and data-bus pending states.
- `DAGB6_WRCLI_GPU_SNOOP_OVERRIDE` and `DAGB6_WRCLI_GPU_SNOOP_OVERRIDE_VALUE`: full-width write-client snoop override enable/value bitmaps.
- `DAGB6_DAGB_DLY`, `DAGB6_CNTL_MISC`, and `DAGB6_CNTL_MISC2`: delay injection selection, EA VC remapping, bandwidth initialization/gap timing, urgent boost/halt, clock-gating disable flags, EA request busy suppression flags, swap control, RDRET FIFO performance, and DLOCK credit fields.
- `DAGB6_FIFO_EMPTY`, `DAGB6_FIFO_FULL`, `DAGB6_WR_CREDITS_FULL`, and `DAGB6_RD_CREDITS_FULL`: status bitfields for FIFO and credit conditions.
- `DAGB6_PERFCOUNTER_LO`, `DAGB6_PERFCOUNTER_HI`, `DAGB6_PERFCOUNTER0_CFG` through `DAGB6_PERFCOUNTER2_CFG`, and `DAGB6_PERFCOUNTER_RSLT_CNTL`: low/high counter words, compare value, event select ranges, modes, enable/clear bits, start/stop triggers, enable-any, clear-all, and stop-on-saturate controls.
- `DAGB6_RESERVE0` through `DAGB6_RESERVE13`: generated full-width reserved register field masks.
- `DAGB7_RDCLI0` through the shift-only portion of `DAGB7_RDCLI9`: beginning of DAGB7 read-client controls with the same field layout as DAGB6 read clients. The `DAGB7_RDCLI9` masks are just outside this chunk, so the merge lane should treat that register as split.

## Control Flow And State Behavior

This chunk has no runtime control flow. All behavior occurs when other AMDGPU code expands these constants into register read/modify/write or decode operations.

The state represented by these macros lives in MMHUB hardware registers. Configuration fields affect DAGB routing and quality of service: virtual-channel selection, TLB-credit checks, urgency thresholds, max/min bandwidth limiting, outstanding request limiting, burst sizing, lazy timers, GMI crediting, and data/address DAGB enablement. Clock control and `CNTL_MISC2` fields affect power and clock-gating behavior. Snoop override bitmaps affect how write clients participate in GPU snooping. Pending/FIFO/credit fields expose live hardware status, and performance counter fields control or report hardware counters.

Persistence is hardware-local. Register values remain until reset, power-gating, firmware initialization, or driver programming changes them. This header does not cache values, serialize access, distinguish read-only status from writable controls, or validate legal field values.

## Dependencies And Integration Points

The immediate companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_offset.h`. Its matching `mmhub_dagb_dagbdec6` block gives base address `0x74200`, `mmDAGB6_RDCLI0` at `0x3080`, `mmDAGB6_WRCLI0` at `0x30ac`, `mmDAGB6_WR_DATA_DAGB` at `0x30c8`, `mmDAGB6_CNTL_MISC2` at `0x30e7`, and `mmDAGB6_PERFCOUNTER_LO` at `0x30ec`. The same offset file starts `mmhub_dagb_dagbdec7` at base address `0x74400`, with `mmDAGB7_RDCLI0` at `0x3100` and `mmDAGB7_RDCLI9` at `0x3109`.

`sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_default.h` supplies default values for the same register names, including `mmDAGB6_RDCLI0_DEFAULT`, `mmDAGB6_WRCLI0_DEFAULT`, `mmDAGB6_CNTL_MISC_DEFAULT`, `mmDAGB6_CNTL_MISC2_DEFAULT`, and the DAGB6 performance counter defaults. Those defaults are useful for reset-state comparison and for checking whether runtime programming diverges from generated expectations.

The principal source consumer is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c`, which includes the 9.4.1 offset, shift/mask, and default headers. That implementation mostly uses VM, aperture, protection fault, and RAS fields from the same header family, but it also depends on the DAGB register layout:

- `mmhub_v9_4_init_system_aperture_regs()` iterates DAGB instances and writes `mmDAGB0_WRCLI_GPU_SNOOP_OVERRIDE` and `mmDAGB0_WRCLI_GPU_SNOOP_OVERRIDE_VALUE` with a stride computed from `mmDAGB1_WRCLI_GPU_SNOOP_OVERRIDE - mmDAGB0_WRCLI_GPU_SNOOP_OVERRIDE`. The comments state DAGB instances 0-4 are in hub0 and 5-7 are in hub1, so the DAGB5-DAGB7 macros in this chunk are part of that instance family.
- `mmhub_v9_4_update_medium_grain_clock_gating()` computes a DAGB stride from `mmDAGB1_CNTL_MISC2 - mmDAGB0_CNTL_MISC2` and toggles `DAGB0_CNTL_MISC2__DISABLE_WRREQ_CG_MASK`, `DISABLE_WRRET_CG_MASK`, `DISABLE_RDREQ_CG_MASK`, `DISABLE_RDRET_CG_MASK`, `DISABLE_TLBWR_CG_MASK`, and `DISABLE_TLBRD_CG_MASK` across DAGB instances. The masks are named for DAGB0 but share the same layout as the DAGB5 and DAGB6 `CNTL_MISC2` masks in this chunk.

Although this repository path is under a Ceph client source import, this header is Linux AMDGPU DRM hardware-interface data. It has no Ceph filesystem semantics.

## Risks And Edge Cases

- These macros are a hardware ABI. A wrong shift or mask can silently program the wrong MMIO field while still compiling, affecting MMHUB arbitration, memory traffic fairness, snooping, clock gating, or diagnostics.
- The chunk is highly repetitive. DAGB6 read/write client macros repeat 16 times each, VC controls repeat 8 times for read and write, and burst/lazy timers repeat packed client lanes. Generator drift in one client or VC can be hard to notice by visual review.
- Packed fields require read-modify-write discipline. Client burst/lazy timers use 4-bit lanes, TLB credits use 5-bit lanes, VC controls pack several unrelated controls into one word, and status registers often use full-width or near-full-width bitmaps.
- Full-width masks such as `0xFFFFFFFFL` should be handled as 32-bit register masks. Signed promotion or wrong diagnostic formatting can make register dumps misleading on some build targets.
- Status and control registers use the same macro style. Pending, FIFO, credit-full, performance-counter result, and reserved fields may be read-only or side-effectful according to the hardware specification; this header does not encode access permissions.
- `DAGB*_CNTL_MISC2` and `*_CGTT_CLK_CTRL` fields are not passive metadata. Incorrect writes can disable clock gating, force/suppress busy behavior, or change light-sleep override behavior.
- `WRCLI_GPU_SNOOP_OVERRIDE` and `WRCLI_GPU_SNOOP_OVERRIDE_VALUE` are full-client bitmaps. A bad bit position or instance stride can affect an unrelated write client or DAGB instance.
- The chunk boundary splits context in both directions: it starts after the first `DAGB5_WR_ADDR_DAGB_LAZY_TIMER0` definitions and ends before the `DAGB7_RDCLI9` masks. The final per-file merge should reconcile adjacent chunks before making whole-register claims for those boundary registers.

## Test And Validation Signals

There are no direct unit tests for this macro-only range. Useful validation signals are compile-time, generated-data, and hardware-observation based:

- Build AMDGPU code that includes `mmhub_9_4_1_sh_mask.h`, especially `amdgpu/mmhub_v9_4.c`, to catch missing or renamed register-field macros.
- Run static consistency checks over this chunk: each `__SHIFT` should have the expected paired `_MASK`, masks should be contiguous for multi-bit fields, single-bit masks should match their shifts, and fields inside one register should not overlap.
- Cross-check covered register groups with `mmhub_9_4_1_offset.h`: every complete `DAGB6_*` register group in this chunk should have a corresponding `mmDAGB6_*` offset/base-index entry, and the DAGB7 partial group should align with the offset block that starts at `mmDAGB7_RDCLI0`.
- Compare generated defaults in `mmhub_9_4_1_default.h` against reset-time hardware dumps for `DAGB6_RDCLI*`, `DAGB6_WRCLI*`, `DAGB6_CNTL_MISC*`, FIFO/credit status, and performance counter registers.
- On MMHUB 9.4.1 hardware or simulator, validate that clock-gating updates in `mmhub_v9_4_update_medium_grain_clock_gating()` affect all intended DAGB instances and preserve unrelated `CNTL_MISC2` bits.
- Exercise GPU snoop override programming in `mmhub_v9_4_init_system_aperture_regs()` and inspect `DAGB5` through `DAGB7` register dumps to confirm the computed instance stride selects the expected registers.
- For diagnostic/performance paths, verify counter enable, clear, select, trigger, high/low reads, and stop-on-saturate behavior without leaving clear bits or trigger state unexpectedly asserted.

## Chunk Notes For Merge Lane

This is chunk 13 of 19 for `mmhub_9_4_1_sh_mask.h`. It should be merged with chunk 12 for the beginning of the DAGB5 write-address lazy-timer register and with chunk 14 for the remainder of `DAGB7_RDCLI9` plus later DAGB7 registers. The complete per-file report should describe this as part of the generated MMHUB 9.4.1 register mask namespace rather than as standalone driver logic.
