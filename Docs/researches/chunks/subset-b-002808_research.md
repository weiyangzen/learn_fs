# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_2_sh_mask.h lines 1-2377

## Scope

This chunk covers the opening 2,377 lines of the generated MMHUB 3.0.2 shift/mask header. The range starts with the license, include guard, and `mmhub_dagbdec` address block, then defines the `DAGB0` register field layout from `DAGB0_RDCLI0` through the first three mask definitions of `DAGB0_FATAL_ERROR_STATUS4`. The next lines after this chunk add the remaining `DAGB0_FATAL_ERROR_STATUS4` masks and continue into `DAGB0_SDP_CGTT_CLK_CTRL`, so this chunk intentionally ends in the middle of that final fatal-status register's mask set.

The covered content is entirely preprocessor data. It defines `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` constants for 32-bit MMIO register fields; it contains no functions, structs, enums, storage, or executable control flow.

## Purpose

The purpose of this header section is to encode the bit-level ABI for the MMHUB 3.0.2 DAGB0 datapath. MMHUB is the memory hub side of AMDGPU virtual memory and memory-traffic routing. The `DAGB0` register families in this chunk describe read/write client arbitration, virtual-channel assignment, bandwidth limits, TLB and return credits, clock-gating controls, pending/busy state, SDP routing and error handling, performance counters, and fatal-error capture fields.

The companion `mmhub_3_0_2_offset.h` header supplies the register addresses, for example `regDAGB0_RDCLI0`, `regDAGB0_WR_DATA_CREDIT`, `regDAGB0_SDP_ERR_STATUS`, and `regDAGB0_FATAL_ERROR_STATUS0..4`. This file supplies the field positions and masks consumed by AMDGPU helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`.

## Important Macro Families

### Read Client Control

`DAGB0_RDCLI0` through `DAGB0_RDCLI23` define the same per-client read-side layout. Each client has fields for:

- `VIRT_CHAN`, selecting the virtual channel.
- `CHECK_TLB_CREDIT`, gating requests on TLB credit availability.
- `URG_HIGH` and `URG_LOW`, encoding urgency thresholds or priorities.
- `MAX_BW_ENABLE` / `MAX_BW` and `MIN_BW_ENABLE` / `MIN_BW`, controlling bandwidth limiting or reservation.
- `OSD_LIMITER_ENABLE` and `MAX_OSD`, limiting outstanding demand.

`DAGB0_RD_CNTL` adds global read arbitration knobs such as client and VC max-bandwidth windows, shared-VC count, and round-robin enable. `DAGB0_RD_IO_CNTL` and `DAGB0_RD_GMI_CNTL` provide two priority override slots plus a common priority for IO and GMI classes. `DAGB0_RD_ADDR_DAGB` enables the read address DAGB path, jump-ahead behavior, self-init suppression, instance identity, and jump mode.

The read path also defines clock-gating controls (`DAGB0_RD_CGTT_CLK_CTRL`, `DAGB0_L1TLB_RD_CGTT_CLK_CTRL`), per-client maximum burst and lazy-timer nibbles grouped as clients 0-7, 8-15, and 16-23, virtual-channel controls `DAGB0_RD_VC0_CNTL` through `DAGB0_RD_VC5_CNTL`, and IO/GMI VC controls. `DAGB0_RD_CNTL_MISC`, `DAGB0_RD_TLB_CREDIT`, `DAGB0_RD_RDRET_CREDIT_CNTL`, and `DAGB0_RD_RDRET_CREDIT_CNTL2` describe storage pool, UTCL2 VCI, read-return compatibility mode, per-TLB credits, per-VC read-return credits, VC mode, equality-fix controls, and pool credit.

The read-side pending and override registers (`DAGB0_RDCLI_ASK_PENDING`, `GO_PENDING`, `GBLSEND_PENDING`, `TLB_PENDING`, `OARB_PENDING`, `ASK2ARB_PENDING`, `ASK2DF_PENDING`, `OSD_PENDING`, `ASK_OSD_PENDING`, `NOALLOC_OVERRIDE`, and `NOALLOC_OVERRIDE_VALUE`) expose full-width bitmaps. These fields are likely used for diagnostics, drain checks, or debug overrides because each register has a single `BUSY`, `ENABLE`, or `VALUE` field covering all 32 bits.

### Write Client Control

`DAGB0_WRCLI0` through `DAGB0_WRCLI23` mirror the read client format: virtual-channel selection, TLB-credit checking, urgency thresholds, max/min bandwidth policy, OSD limiting, and max outstanding demand.

`DAGB0_WR_CNTL` differs slightly from the read global control. It has client and VC max-bandwidth windows plus `VC_ROUNDROBIN_EN`, `UPDATE_FED`, and `UPDATE_NACK`, which are write-path policy/update controls. `DAGB0_WR_IO_CNTL` and `DAGB0_WR_GMI_CNTL` mirror the read-side IO/GMI priority override shape. `DAGB0_WR_ADDR_DAGB` controls the write address DAGB path, while `DAGB0_WR_DATA_DAGB` separately controls the write data path; both expose enable, jump-ahead, self-init, and identity fields, with the address path also carrying `JUMP_MODE`.

Write address and write data paths each have grouped maximum-burst and lazy-timer controls for clients 0-23. The write path also includes `DAGB0_WR_VC0_CNTL` through `DAGB0_WR_VC5_CNTL`, IO/GMI VC controls, `DAGB0_WR_CNTL_MISC`, `DAGB0_WR_TLB_CREDIT`, `DAGB0_WR_DATA_CREDIT`, `DAGB0_WR_MISC_CREDIT`, `DAGB0_WR_DATA_FIFO_CREDIT_CNTL1`, and `DAGB0_WR_ATOMIC_FIFO_CREDIT_CNTL1`. These registers describe storage and HDP client ID selection, per-TLB credits, burst-size data credits, atomic credits, deadlock VC selection, data FIFO credits, atomic FIFO credits, pool credits, VC mode, and fix bits.

Write pending and override registers include the read-side set plus write-specific DBUS pending state and GPU snoop overrides: `DAGB0_WRCLI_DBUS_ASK_PENDING`, `DAGB0_WRCLI_DBUS_GO_PENDING`, `DAGB0_WRCLI_GPU_SNOOP_OVERRIDE`, `DAGB0_WRCLI_GPU_SNOOP_OVERRIDE_VALUE`, `DAGB0_WRCLI_NOALLOC_OVERRIDE`, and `DAGB0_WRCLI_NOALLOC_OVERRIDE_VALUE`.

### DAGB Miscellaneous State and Performance Counters

`DAGB0_DAGB_DLY` exposes delay, client, and position fields. `DAGB0_CNTL_MISC` has a bandwidth initialization cycle field. `DAGB0_CNTL_MISC2` is a compact control and debug register with read/write busy overrides, TLB busy overrides, SDP busy override, swap control, parity check enable, read-data parity-to-NACK behavior, write-data parity-to-RAS behavior, read-return FIFO performance selection, and fine-grain clock-gating disable bits for read/write return tap chains.

`DAGB0_FIFO_EMPTY`, `DAGB0_FIFO_FULL`, `DAGB0_RD_CREDITS_FULL`, and `DAGB0_WR_CREDITS_FULL` expose packed status fields for FIFO and credit fullness. `DAGB0_PERFCOUNTER_LO` and `DAGB0_PERFCOUNTER_HI` hold the low counter bits, high counter bits, and a compare value. `DAGB0_PERFCOUNTER0_CFG`, `DAGB0_PERFCOUNTER1_CFG`, and `DAGB0_PERFCOUNTER2_CFG` define event selection, ending selection, performance mode, enable, and clear bits. `DAGB0_PERFCOUNTER_RSLT_CNTL` selects a counter result and provides start/stop triggers, enable-any, clear-all, and stop-on-saturate controls.

`DAGB0_L1TLB_REG_RW` exposes command bits for L1 TLB register write/read control plus a large reserved field. `DAGB0_RESERVE1` through `DAGB0_RESERVE4` are full-width reserved register fields.

### SDP Routing, Credits, Errors, and Fatal Capture

The SDP section begins with `DAGB0_SDP_RD_BW_CNTL`, which controls SDP read bandwidth maximum, minimum, and max-bandwidth window. `DAGB0_SDP_PRIORITY_OVERRIDE` supplies two override slots, each with priority, client ID, and enable bits for DRAM read/write, GMI read/write, and IO read/write traffic. `DAGB0_SDP_RD_PRIORITY` and `DAGB0_SDP_WR_PRIORITY` define common priorities for DRAM, GMI, and IO. `DAGB0_SDP_RD_CLI2SDP_VC_MAP` and `DAGB0_SDP_WR_CLI2SDP_VC_MAP` map DRAM/GMI/IO client classes onto SDP virtual channels.

`DAGB0_SDP_ENABLE` is a single enable bit. `DAGB0_SDP_CREDITS` defines read-response, write-response, and command credits. `DAGB0_SDP_TAG_RESERVE0/1`, `DAGB0_SDP_VCC_RESERVE0/1`, and `DAGB0_SDP_VCD_RESERVE0/1` reserve tags or credits per virtual channel and optionally distribute pool resources.

`DAGB0_SDP_ERR_STATUS` captures read/write response status, read data status, read data parity error, error-clear control, busy-on-error policy, FUE flag, ignored read-response fatal error disable, fatal interrupt enable, ignore-client-fatal interrupt policy, level interrupt mode, and busy-on-completion-fatal behavior. `DAGB0_SDP_REQ_CNTL` controls request pass-PW overrides, request-chain overrides for DRAM/GMI, inner-domain mode, and block levels for read/write/atomic requests.

`DAGB0_SDP_MISC_AON`, `DAGB0_SDP_MISC`, and `DAGB0_SDP_MISC2` include link-manager hysteresis/deassert behavior, early write-return enables for VC0-VC7, early SDP original data behavior, dynamic link-manager mode, halt/reconnect/idle thresholds, data FIFO margins, read-return swap mode, request blocking, request-blocked status, and read-response credit-release mode. `DAGB0_SDP_ARB_CNTL0` and `DAGB0_SDP_ARB_CNTL1` tune early read/write switching, error event or halt request behavior, DED mode, and read/write burst limits by cycle and data count.

The fatal-error registers at the end of the chunk provide a captured transaction record. `DAGB0_FATAL_ERROR_CNTL` selects a filter number and `DAGB0_FATAL_ERROR_CLEAR` clears captured fatal state. `DAGB0_FATAL_ERROR_STATUS0` records validity, client ID, and low address bits. `STATUS1` records high address bits. `STATUS2` records client tag, SDP tag, VFID, VF, address space, IO, and size. `STATUS3` records unit ID, operation, security level, write/read TMZ, snoop, invalidation, NACK, read-only, memory-log, internal fatal, and external fatal. The chunk includes `STATUS4` shifts for priority, chain, full, drop, write-address phase, and no-allocate, plus masks for priority, chain, and full; the remaining masks are in the next chunk.

## Control Flow and State Behavior

This chunk has no software control flow. Its effect is compile-time substitution of constants into AMDGPU register access code.

The state represented here is hardware state in MMHUB DAGB0. Some fields are persistent configuration until reset or reprogramming, such as virtual-channel assignment, bandwidth windows, max/min bandwidth, priorities, clock-gating hysteresis, TLB/data/FIFO credits, SDP VC maps, request policy, and performance counter selection. Other fields are status or sticky error state, such as pending bitmaps, FIFO empty/full, credit full, SDP error status, performance counter results, and fatal-error status. A few fields behave as command or control bits, such as performance counter clear bits, SDP error clear, fatal error clear, request blocking, no-allocate and snoop overrides, and busy overrides.

The header does not encode ordering rules. Callers must follow the owning MMHUB and SOC15 initialization paths when sequencing reads, writes, drains, clears, and polls.

## Dependencies and Integration Points

Direct dependencies are the generated MMHUB 3.0.2 register headers and AMDGPU register helpers:

- `mmhub_3_0_2_offset.h` supplies register offsets and base indices for every `DAGB0_*` register in this chunk.
- `mmhub_3_0_2_default.h` supplies reset/default values for related MMHUB registers where generated defaults exist.
- `amdgpu/mmhub_v3_0_2.c` includes this header and the matching offset header, then uses `REG_SET_FIELD` / `REG_GET_FIELD` heavily for MMHUB VM, L1 TLB, L2 cache, invalidation, and fault registers elsewhere in this same generated mask file.
- SOC15 accessors (`RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `SOC15_REG_OFFSET`) are the runtime bridge from these constants to real MMIO accesses.

Within the inspected `mmhub_v3_0_2.c` implementation, the later MMVM fields from this same header are used for page table base programming, GART aperture setup, system aperture setup, TLB and L2 cache enablement, VMID context setup, invalidation request generation, and L2 protection fault decoding. The `DAGB0` fields in this chunk are more likely consumed by initialization, diagnostics, RAS/error handling, perf/debug, or future generation-specific tuning paths that need to inspect or program DAGB datapath arbitration and SDP state.

The client-ID table in `mmhub_v3_0_2.c` maps MMHUB client IDs to names such as VMC, DCEDMC, MP0/MP1, HDP, LSDMA, JPEG, VCN, VSCH, and debug clients. That table is relevant when decoding `CID` fields from MMHUB fault or fatal status registers defined in this header.

## Risks

- Bit drift is high impact. Incorrect masks or shifts can write the wrong hardware field, causing memory-routing faults, arbitration starvation, hangs, bad performance data, or lost fatal-error context.
- The read and write client families are highly repetitive but not semantically interchangeable. Mechanical edits can easily change one client or path while leaving the matching read/write or address/data counterpart inconsistent.
- Bandwidth, urgency, OSD, VC, and credit fields directly affect memory traffic scheduling. Bad values can create unfairness, underutilization, deadlocks, or timeout-sensitive stalls.
- Pending, busy override, no-allocate override, snoop override, SDP request blocking, and clear bits should not be treated as ordinary persistent configuration. Misuse can mask real drains/errors or force traffic behavior outside normal policy.
- SDP error and fatal-error fields are diagnostic and recovery-sensitive. Clearing too early can lose root-cause data; failing to clear sticky state can cause repeated interrupts or misleading later reports.
- Clock-gating and low-power controls interact with block idleness. Incorrect `LS_DISABLE`, hysteresis, or busy override programming can waste power or gate clocks while state is still active.
- The chunk boundary cuts `DAGB0_FATAL_ERROR_STATUS4` before all masks are present, so any merged report must join this chunk with the next one before documenting that register as complete.

## Test and Validation Signals

Useful validation is mostly integration and hardware bring-up coverage:

- Build coverage for AMDGPU sources that include `mmhub/mmhub_3_0_2_sh_mask.h`; this catches renamed, missing, or malformed macros.
- MMHUB GART and VM smoke tests should cover the same header's MMVM fields through `mmhub_v3_0_2_gart_enable`, VMID setup, TLB/cache programming, and invalidation paths.
- VM fault injection should verify that MMHUB client IDs and protection/fatal status fields decode consistently with the client table and hardware documentation.
- Suspend/resume, GPU reset, and clock-gating tests should watch for hangs or lost state around DAGB busy, FIFO, credit, and CGTT controls.
- Performance/debug tests should program `DAGB0_PERFCOUNTER*_CFG`, `DAGB0_PERFCOUNTER_RSLT_CNTL`, and counter result registers, then verify event selection, clear, enable, saturation, and result selection behavior.
- RAS/error tests should exercise SDP error handling and fatal-error capture/clear sequencing, preserving `DAGB0_FATAL_ERROR_STATUS0..4` data long enough for diagnostics.
- Stress tests with display, HDP, SDMA, JPEG/VCN, and VM traffic should catch regressions in read/write client VC mapping, priority, bandwidth, OSD, TLB credit, data credit, and SDP credit configuration.

## Unresolved Cross-Chunk References

This range covers only `mmhub_3_0_2_sh_mask.h` lines 1-2377. It does not include the rest of `DAGB0_FATAL_ERROR_STATUS4`, the following `DAGB0_SDP_CGTT_CLK_CTRL` and `DAGB0_SDP_LATENCY_SAMPLING` definitions, the later `DAGB1` block, PCTL, MMVM L1/L2, VM context, invalidation, framebuffer aperture, and shared MMHUB register families. Those belong to later chunks for the same source file and should be reconciled by the merge lane.
