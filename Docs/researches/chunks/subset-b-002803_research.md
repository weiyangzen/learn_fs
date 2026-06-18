# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_1_sh_mask.h lines 1-2366

## Scope And Purpose

This chunk is the opening portion of the generated AMDGPU MMHUB 3.0.1 register shift/mask header. It starts with the AMD MIT-style license and include guard, then defines the first `mmhub_dagbdec` address-block field macros through the first two shift definitions for `DAGB0_SDP_PRIORITY_OVERRIDE`. The source file continues after this range, so this document covers only lines 1-2366.

The file is a hardware register contract, not executable logic. Its public surface is a large set of preprocessor constants named as `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`; callers combine those constants with AMDGPU register helpers to compose or decode 32-bit MMIO register values. In this chunk there are no C functions, structs, enums, storage objects, loops, branches, or direct register accesses.

Within the covered range, the dominant purpose is to describe DAGB0 read and write arbitration for MMHUB 3.0.1: per-client virtual-channel selection, TLB-credit checks, urgency thresholds, bandwidth throttling, outstanding request limits, address/data DAGB burst and lazy timers, clock-gating controls, pending/status bitmaps, FIFO/credit status, and DAGB performance counters.

## Important APIs, Types, And Register Families

There are no callable APIs or local types. The API is the macro namespace consumed by code that includes `mmhub_3_0_1_sh_mask.h`, typically through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15*`, and `RREG32_SOC15*`.

Important register families in this chunk include:

- `DAGB0_RDCLI0` through `DAGB0_RDCLI29`: per-read-client control registers. Each has the same field layout: `VIRT_CHAN`, `CHECK_TLB_CREDIT`, `URG_HIGH`, `URG_LOW`, `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `OSD_LIMITER_ENABLE`, and `MAX_OSD`.
- `DAGB0_WRCLI0` through `DAGB0_WRCLI29`: matching per-write-client controls with the same virtual-channel, TLB-credit, urgency, bandwidth, and outstanding-request limiter fields.
- `DAGB0_RD_CNTL` and `DAGB0_WR_CNTL`: shared read/write arbitration controls for client max-bandwidth window, virtual-channel max-bandwidth window, shared VC count, and round-robin enable.
- `DAGB0_RD_IO_CNTL`, `DAGB0_RD_GMI_CNTL`, `DAGB0_WR_IO_CNTL`, and `DAGB0_WR_GMI_CNTL`: priority override controls with two override slots and a common priority field for IO and GMI traffic.
- `DAGB0_RD_ADDR_DAGB`, `DAGB0_WR_ADDR_DAGB`, and `DAGB0_WR_DATA_DAGB`: DAGB enable, jump-ahead, self-init-disable, `WHOAMI`, and write-address jump-mode fields.
- `DAGB0_*_CGTT_CLK_CTRL` and `DAGB0_L1TLB_*_CGTT_CLK_CTRL`: clock and light-sleep timing fields such as `ON_DELAY`, `OFF_HYSTERESIS`, `LS_ASSERT_HYSTERESIS`, `LS_DISABLE`, and `BUSY_OVERRIDE`.
- `DAGB0_RD_ADDR_DAGB_MAX_BURST[0-3]`, `DAGB0_RD_ADDR_DAGB_LAZY_TIMER[0-3]`, `DAGB0_WR_ADDR_DAGB_MAX_BURST[0-3]`, `DAGB0_WR_ADDR_DAGB_LAZY_TIMER[0-3]`, `DAGB0_WR_DATA_DAGB_MAX_BURST[0-3]`, and `DAGB0_WR_DATA_DAGB_LAZY_TIMER[0-3]`: packed four-bit fields for clients 0-31.
- `DAGB0_RD_VC0_CNTL` through `DAGB0_RD_VC5_CNTL` and `DAGB0_WR_VC0_CNTL` through `DAGB0_WR_VC5_CNTL`: per-virtual-channel storage credit, max/min bandwidth, OSD limiter, and max outstanding fields.
- `DAGB0_RD_IO_VC_CNTL`, `DAGB0_RD_GMI_VC_CNTL`, `DAGB0_WR_IO_VC_CNTL`, and `DAGB0_WR_GMI_VC_CNTL`: IO/GMI virtual-channel bandwidth and OSD controls.
- `DAGB0_RD_CNTL_MISC`, `DAGB0_WR_CNTL_MISC`, `DAGB0_RD_TLB_CREDIT`, `DAGB0_WR_TLB_CREDIT`, `DAGB0_WR_DATA_CREDIT`, `DAGB0_WR_MISC_CREDIT`, `DAGB0_WR_DATA_FIFO_CREDIT_CNTL1`, and `DAGB0_WR_ATOMIC_FIFO_CREDIT_CNTL1`: storage-pool, UTCL2 VCI, TLB, data, DLOCK, OSD, atomic, FIFO, and per-VC credit packing.
- `DAGB0_RDCLI_*_PENDING`, `DAGB0_WRCLI_*_PENDING`, and `DAGB0_WRCLI_DBUS_*_PENDING`: full-width `BUSY` status bitmaps for ask/go/global-send/TLB/output-arbiter/DF/OSD and data-bus pending states.
- `DAGB0_WRCLI_GPU_SNOOP_OVERRIDE` and `DAGB0_WRCLI_GPU_SNOOP_OVERRIDE_VALUE`: full-width per-client enable/value bitmaps for GPU snoop override behavior.
- `DAGB0_DAGB_DLY`, `DAGB0_CNTL_MISC`, and `DAGB0_CNTL_MISC2`: delay selection, bandwidth-init cycle, busy overrides, swap control, parity-check enablement, RDATA/WDATA parity response behavior, RDRET FIFO performance, and tap-chain fine-grain clock-gating disable bits.
- `DAGB0_FIFO_EMPTY`, `DAGB0_FIFO_FULL`, `DAGB0_RD_CREDITS_FULL`, and `DAGB0_WR_CREDITS_FULL`: FIFO and credit fullness/emptiness status fields.
- `DAGB0_PERFCOUNTER_LO`, `DAGB0_PERFCOUNTER_HI`, `DAGB0_PERFCOUNTER0_CFG` through `DAGB0_PERFCOUNTER2_CFG`, and `DAGB0_PERFCOUNTER_RSLT_CNTL`: performance counter low/high words, compare value, event-select range, mode, enable, clear, start/stop triggers, enable-any, clear-all, and stop-on-saturate controls.
- `DAGB0_L1TLB_REG_RW` and `DAGB0_RESERVE1` through `DAGB0_RESERVE4`: L1TLB register read/write control and full-width reserved placeholders.
- `DAGB0_SDP_RD_BW_CNTL` and the start of `DAGB0_SDP_PRIORITY_OVERRIDE`: SDP read bandwidth controls and the first two priority-override shift fields. The masks and remaining fields for `DAGB0_SDP_PRIORITY_OVERRIDE` are outside this chunk.

## Control Flow And State Behavior

This chunk has no runtime control flow. Its constants are substituted by the C preprocessor into other AMDGPU code that reads, modifies, writes, or logs MMHUB registers.

The runtime state represented here lives in MMHUB hardware registers. Read/write client and VC fields configure traffic routing and quality-of-service policy: virtual-channel choice, bandwidth windows, min/max bandwidth enforcement, urgency thresholds, TLB-credit accounting, outstanding request limits, and address/data burst or lazy behavior. Pending, FIFO, credit-full, and performance-counter fields expose hardware status or counter state. Counter control fields such as `ENABLE`, `CLEAR`, `CLEAR_ALL`, triggers, and stop-on-saturate are stateful hardware controls.

Persistence is entirely hardware-local. Values remain until reset, power-gating, firmware programming, or driver reprogramming changes them. This header does not cache register values, serialize access, validate field access direction, or protect callers from writing status-only or reserved fields.

## Dependencies And Integration Points

The immediate companion file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_1_offset.h`. It maps the same `mmhub_dagbdec` register names to offsets at base address `0x68000`, with `regDAGB0_RDCLI0` at `0x0000`, `regDAGB0_WRCLI0` at `0x003f`, `regDAGB0_WR_DATA_DAGB` at `0x006b`, `regDAGB0_PERFCOUNTER_LO` at `0x0096`, `regDAGB0_SDP_RD_BW_CNTL` at `0x00a1`, and `regDAGB0_SDP_PRIORITY_OVERRIDE` at `0x00a2`.

The principal source integration point in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_1.c`, which includes both `mmhub_3_0_1_offset.h` and `mmhub_3_0_1_sh_mask.h`. That implementation primarily uses later MMVM fields from the same header for VM/GART setup, invalidation, and protection-fault decoding, but the include provides the complete MMHUB 3.0.1 register-field namespace for any DAGB, VM, fault, and debug code compiled in that translation unit.

The file follows the AMDGPU generated-register convention shared with nearby MMHUB headers such as `mmhub_2_0_0_sh_mask.h`, `mmhub_3_0_2_sh_mask.h`, and `mmhub_9_4_1_sh_mask.h`. Cross-generation similarity is useful for review, but the `reg*` offsets, base indices, client counts, and exact masks are ASIC-specific; code should include the header matching the IP block being programmed.

Although this repository path is under a Ceph client source import, this file belongs to the Linux AMDGPU DRM hardware interface and has no Ceph filesystem behavior.

## Risks And Edge Cases

- These constants are a hardware ABI. A wrong shift or mask can silently program the wrong field, change request routing, alter bandwidth policy, lose TLB-credit accounting, or misread status while still compiling cleanly.
- The read-client and write-client blocks are highly repetitive. Copy/paste or generator drift can affect a single client while leaving neighboring macros correct, so spot checks should cover client 0, middle clients, and client 29.
- Many registers pack repeated fields tightly into one word. Client burst/lazy timers use 4-bit lanes, TLB credits use 5-bit lanes, bandwidth and OSD fields use larger packed ranges, and status registers may be full-width bitmaps. Read-modify-write callers must preserve unrelated bits.
- Full-width masks such as `0xFFFFFFFFL` should be treated as 32-bit register values. Signed promotion or wrong printf formats can make diagnostics misleading.
- Status and control fields share the same macro naming style. Pending, FIFO, credit, and counter result fields may be read-only or side-effectful depending on the hardware guide; the header does not encode access permissions.
- Clock, parity, busy override, snoop override, counter clear, and `L1TLB_REG_RW` fields are not passive metadata. Accidental writes can change power behavior, suppress or force busy state, clear diagnostics, or alter debug access.
- The chunk boundary splits `DAGB0_SDP_PRIORITY_OVERRIDE` after only `OVERRIDE0_PRIORITY__SHIFT` and `OVERRIDE0_CLIENT_ID__SHIFT`. Whole-file research must merge this with the following chunk before describing that register completely.

## Test And Validation Signals

There are no direct unit tests for this macro-only chunk. Useful validation is compile-time, static, and hardware-observation based:

- Build AMDGPU code paths that include `mmhub_3_0_1_sh_mask.h`, especially `mmhub_v3_0_1.c`, to catch missing or renamed macros.
- Run static mask/shift consistency checks: masks should be contiguous, single-bit masks should match their shift, packed fields should not overlap, and full-width masks should start at shift zero.
- Compare this chunk against `mmhub_3_0_1_offset.h` so every covered register-comment group has a corresponding `reg*` offset and base index.
- Compare generated values against the authoritative AMD register database for MMHUB 3.0.1, especially repeated `RDCLI`/`WRCLI` layouts, 30-client limits, VC count, FIFO/credit status widths, and performance-counter controls.
- On MMHUB 3.0.1 hardware or simulator, inspect MMHUB register dumps around VM/GART initialization, power transitions, and display or media client activity to confirm DAGB fields remain at expected firmware/driver-programmed values.
- For debug/performance paths, validate that counter enable/clear/select fields and high/low counter reads behave as expected and that clear bits do not persist unexpectedly.

## Chunk Notes For Merge Lane

This is the first chunk of `mmhub_3_0_1_sh_mask.h`. It covers the license, include guard, and the opening `mmhub_dagbdec` DAGB0 arbitration/QoS/status/performance-counter section through the start of `DAGB0_SDP_PRIORITY_OVERRIDE`. The final per-file report should reconcile this with the next chunk before making complete statements about SDP priority, later DAGB0 registers, MMVM, MMEA, ATC, or L2TLB fields.
