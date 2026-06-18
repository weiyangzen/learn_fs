# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_0_sh_mask.h lines 1-2377

## Scope

This chunk covers the opening of the generated AMD MMHUB 3.0.0 shift/mask header. The file starts with the AMD MIT-style license, the `_mmhub_3_0_0_SH_MASK_HEADER` include guard, and the beginning of the `mmhub_dagbdec` address block. Lines 1-2377 cover `DAGB0` decoder definitions from the read-client registers through the first fields of `DAGB0_SDP_CGTT_CLK_CTRL`.

The chunk is data-only C preprocessor content. It defines register field offsets and bit masks; it does not define functions, structs, enums, global variables, storage, or executable control flow.

## Purpose

The purpose of this header section is to provide the bit-level ABI for AMDGPU MMHUB 3.0.0 DAGB0 programming. Each field is represented by the standard generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used when shifting a value into or out of a register.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask used to isolate, clear, or compose that field.

Driver code includes this header together with `mmhub_3_0_0_offset.h`. The offset header supplies addresses such as `regDAGB0_CNTL_MISC2`; this header supplies the field layout for those registers. Consumers normally use AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET` instead of open-coding shifts and masks.

## Register Families

### Read Client Control

The chunk starts with `DAGB0_RDCLI0` through `DAGB0_RDCLI23`. These 24 read clients all share the same field layout: `VIRT_CHAN`, `CHECK_TLB_CREDIT`, high and low urgency thresholds, maximum and minimum bandwidth enable/value fields, `OSD_LIMITER_ENABLE`, and `MAX_OSD`.

This family controls how individual MMHUB read request clients are mapped onto virtual channels and throttled. The repeated 24-client layout is important because client IDs elsewhere in MMHUB code identify GPU blocks such as display, HDP, SDMA, JPEG, VCN, and debug clients. A stale shift or mask here would route traffic to the wrong VC or apply an unintended bandwidth/OSD policy to a hardware client.

The shared read-side control registers that follow include:

- `DAGB0_RD_CNTL`, with bandwidth windows, shared VC count, and round-robin enable.
- `DAGB0_RD_IO_CNTL` and `DAGB0_RD_GMI_CNTL`, with two priority override slots plus common priority.
- `DAGB0_RD_ADDR_DAGB`, enabling DAGB address handling, jump-ahead behavior, self-init control, `WHOAMI`, and jump mode.
- `DAGB0_RD_CGTT_CLK_CTRL` and `DAGB0_L1TLB_RD_CGTT_CLK_CTRL`, which expose on-delay, off-hysteresis, light-sleep assertion hysteresis, light-sleep disable, and busy override fields for clock-gating/test control.

### Read Burst, Lazy Timer, VC, and Credit Control

Read address DAGB burst and lazy-timer settings are split into three registers each for clients 0-7, 8-15, and 16-23. `DAGB0_RD_ADDR_DAGB_MAX_BURST*` and `DAGB0_RD_ADDR_DAGB_LAZY_TIMER*` pack eight 4-bit client fields per register.

Virtual-channel control appears as `DAGB0_RD_VC0_CNTL` through `DAGB0_RD_VC5_CNTL`, plus `DAGB0_RD_IO_VC_CNTL` and `DAGB0_RD_GMI_VC_CNTL`. These set storage credits, max/min bandwidth, OSD limiting, and maximum OSD per VC or special IO/GMI channel. Additional read-side credit registers include:

- `DAGB0_RD_CNTL_MISC`, primarily storage pool credit.
- `DAGB0_RD_TLB_CREDIT`, with six packed TLB credit fields.
- `DAGB0_RD_RDRET_CREDIT_CNTL` and `DAGB0_RD_RDRET_CREDIT_CNTL2`, with VC read-return credits, pool credit, VC mode, and fixed equality controls.

The read pending and override registers (`DAGB0_RDCLI_ASK_PENDING`, `GO_PENDING`, `GBLSEND_PENDING`, `TLB_PENDING`, `OARB_PENDING`, `ASK2ARB_PENDING`, `ASK2DF_PENDING`, `OSD_PENDING`, `ASK_OSD_PENDING`, `NOALLOC_OVERRIDE`, and `NOALLOC_OVERRIDE_VALUE`) are full-width bitmaps. They let diagnostic or low-level code observe per-client busy/pending state and override no-allocate behavior.

### Write Client Control

`DAGB0_WRCLI0` through `DAGB0_WRCLI23` mirror the read-client layout: virtual channel, TLB-credit checking, urgency thresholds, bandwidth enable/value fields, OSD limiter, and maximum OSD. The write-side shared controls include:

- `DAGB0_WR_CNTL`, with client/VC bandwidth windows, round-robin enable, and update behavior for FED/NACK.
- `DAGB0_WR_IO_CNTL` and `DAGB0_WR_GMI_CNTL`, with priority override slots.
- `DAGB0_WR_ADDR_DAGB`, `DAGB0_WR_CGTT_CLK_CTRL`, and `DAGB0_L1TLB_WR_CGTT_CLK_CTRL`.
- `DAGB0_WR_ADDR_DAGB_MAX_BURST*` and `DAGB0_WR_ADDR_DAGB_LAZY_TIMER*` for write-address clients.
- `DAGB0_WR_DATA_DAGB`, `DAGB0_WR_DATA_DAGB_MAX_BURST*`, and `DAGB0_WR_DATA_DAGB_LAZY_TIMER*` for the separate write-data path.

The split between write-address and write-data DAGB programming is a key hardware distinction in this chunk. Address arbitration, data arbitration, burst sizing, and lazy timers can be controlled independently, so consumers must use the address-path masks for address DAGB registers and the data-path masks for data DAGB registers.

### Write VC, Credits, Pending, and Overrides

`DAGB0_WR_VC0_CNTL` through `DAGB0_WR_VC5_CNTL`, `DAGB0_WR_IO_VC_CNTL`, and `DAGB0_WR_GMI_VC_CNTL` mirror the read VC controls. `DAGB0_WR_CNTL_MISC` adds storage pool credit and HDP client ID selection.

Write-side credit fields are more varied than the read-side fields:

- `DAGB0_WR_TLB_CREDIT` packs six TLB credit fields.
- `DAGB0_WR_DATA_CREDIT` separates deadlock VC, large burst, middle burst, and small burst credits.
- `DAGB0_WR_MISC_CREDIT` controls atomic credit and deadlock VC number.
- `DAGB0_WR_DATA_FIFO_CREDIT_CNTL1` and `DAGB0_WR_ATOMIC_FIFO_CREDIT_CNTL1` control VC0-VC3 credits, pool credit, VC mode, and fixed arbitration/equality fields.

The write pending bitmaps cover request, grant, global-send, TLB, OARB, fabric, OSD, and data-bus phases. Write-only override groups include GPU snoop override and no-allocate override masks and values. These are hardware state/diagnostic surfaces rather than normal algorithmic data structures.

### DAGB Miscellaneous, FIFO, Performance, and L1TLB Access

The middle of the chunk defines control and status surfaces around DAGB0 itself:

- `DAGB0_DAGB_DLY` selects a delay, client, and position.
- `DAGB0_CNTL_MISC` exposes bandwidth init cycle.
- `DAGB0_CNTL_MISC2` includes read/write/TLB/SDP busy overrides, swap control, parity checking, read/write return clock-gating related controls, and read-return FIFO performance selection.
- `DAGB0_FIFO_EMPTY`, `DAGB0_FIFO_FULL`, `DAGB0_RD_CREDITS_FULL`, and `DAGB0_WR_CREDITS_FULL` are compact status bitmaps.
- `DAGB0_PERFCOUNTER_LO`, `DAGB0_PERFCOUNTER_HI`, `DAGB0_PERFCOUNTER0_CFG`, `DAGB0_PERFCOUNTER1_CFG`, `DAGB0_PERFCOUNTER2_CFG`, and `DAGB0_PERFCOUNTER_RSLT_CNTL` define local DAGB performance counter data, compare value, event selection, mode, enable, clear, trigger, and stop-on-saturate fields.
- `DAGB0_L1TLB_REG_RW` exposes command bits for L1 TLB register read/write control plus a large reserved field.
- `DAGB0_RESERVE1` through `DAGB0_RESERVE4` are full-width reserved masks.

`amdgpu/mmhub_v3_0.c` directly includes this header and uses `DAGB0_CNTL_MISC2` masks while programming MMHUB clock-gating behavior. That consumer demonstrates the intended use pattern: read a register, clear or set named mask bits, then write the register back through SOC15 MMIO helpers.

### SDP Configuration and Error Handling

The final third of this chunk is the start of the `DAGB0_SDP_*` family. It describes the SDP path connecting DAGB traffic to downstream fabric behavior:

- `DAGB0_SDP_RD_BW_CNTL` controls SDP read bandwidth enable/value, minimum bandwidth, and max bandwidth window.
- `DAGB0_SDP_PRIORITY_OVERRIDE` provides two priority override slots with per-direction enables for DRAM, GMI, and IO read/write.
- `DAGB0_SDP_RD_PRIORITY` and `DAGB0_SDP_WR_PRIORITY` assign per-VC priorities.
- `DAGB0_SDP_RD_CLI2SDP_VC_MAP` and `DAGB0_SDP_WR_CLI2SDP_VC_MAP` map SRT, NRT, deadlock, HRT, IO, and GMI traffic classes to SDP VCs.
- `DAGB0_SDP_ENABLE`, `DAGB0_SDP_CREDITS`, `DAGB0_SDP_TAG_RESERVE*`, `DAGB0_SDP_VCC_RESERVE*`, and `DAGB0_SDP_VCD_RESERVE*` control enablement, tag limits, response credits, tag reservation, and credit reservation distribution.
- `DAGB0_SDP_ERR_STATUS` contains read/write response status, read data status/parity error, clear-error command, busy-on-error behavior, fatal/unrecoverable indication, interrupt policy, and completion fatal handling.
- `DAGB0_SDP_REQ_CNTL` defines pass/chain overrides, inner-domain mode, and request block levels for read, write, and atomic traffic.
- `DAGB0_SDP_MISC` and `DAGB0_SDP_MISC2` contain early write-return enables, original-data and link-manager behavior, FIFO margins, request blocking state, and read-response credit release mode.
- `DAGB0_SDP_ARB_CNTL0` and `DAGB0_SDP_ARB_CNTL1` configure early read/write switching, error event/halt behavior, DED mode, and read/write burst limits.

The chunk also covers fatal error reporting registers: `DAGB0_FATAL_ERROR_CNTL`, `DAGB0_FATAL_ERROR_CLEAR`, and `DAGB0_FATAL_ERROR_STATUS0` through `STATUS4`. These fields capture validity, client ID, address low/high portions, CLI/SDP tags, VF/VFID, address space/IO/size, operation, write/read TMZ, snoop, invalidation, NACK, read-only, memory log, internal/external fatal flags, priority, chain/full/drop, write-address phase, and no-allocate state.

The last lines start `DAGB0_SDP_CGTT_CLK_CTRL` and define only its first five shift fields in this chunk. Its masks continue in the next chunk of the same source file.

## Important APIs, Types, and Functions

There are no callable APIs, types, or functions in this chunk. The important interface is the macro namespace itself. Names are generated in a stable pattern that couples:

- Register name comments such as `//DAGB0_RDCLI0`.
- A set of `__SHIFT` constants.
- A matching set of `_MASK` constants.

The effective API consumers rely on is compile-time availability of these exact macro names. Renaming, deleting, or changing a mask is a source-compatible and hardware-compatible change only if all AMDGPU register programming and all matching offset/default headers are updated together.

## Control Flow

This chunk has no runtime control flow. Hardware sequencing is implied by register semantics in consumers:

1. The driver computes field values using `REG_SET_FIELD` or direct mask operations.
2. The driver writes the composed value through SOC15 MMIO helpers to the address from `mmhub_3_0_0_offset.h`.
3. Hardware applies arbitration, credit, clock-gating, pending-state, performance-counter, SDP, or fatal-error behavior.
4. For status and pending registers, driver/debug code reads the register and uses `REG_GET_FIELD` or mask tests to decode the state.

Several fields are command or strobe style controls rather than durable state, especially clear/error, enable/clear performance counter, request block, and override bits. Test or reset code must respect hardware ordering when toggling them.

## State and Persistence

The header itself has no mutable state and persists nothing. The state described by these macros lives in MMHUB hardware registers. Some fields represent configuration that persists until reset or another register write, such as bandwidth windows, VC mappings, credit allocation, clock-gating controls, and SDP request policy. Other fields represent live status or captured error state, such as pending bitmaps, FIFO full/empty indicators, performance counter values, SDP error status, and fatal error status registers.

Because these are memory-mapped hardware registers, persistence is hardware lifecycle dependent. GPU reset, power gating, firmware initialization, or PF/VF separation in SR-IOV can restore or block access to subsets of this state.

## Dependencies and Integration Points

Primary dependencies are:

- `mmhub_3_0_0_offset.h`, which supplies the register addresses matching these field layouts.
- AMDGPU SOC15 register helpers and bitfield helpers, especially `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.
- `drivers/gpu/drm/amd/amdgpu/mmhub_v3_0.c`, which includes this header and uses MMHUB 3.0.0 masks while configuring VM, TLB/cache, fault handling, clock gating, and register addresses.
- Hardware documentation or generator inputs that define MMHUB 3.0.0 DAGB0 field positions.

This header is also structurally paired with nearby generated headers for other MMHUB IP versions. Similar register families appear in `mmhub_2_0_0_sh_mask.h`, `mmhub_3_0_1_sh_mask.h`, and later MMHUB headers, but field presence can vary by generation. Version-specific C code must include the matching version header.

## Risks

The main risk is silent hardware misprogramming. These constants are trusted by low-level driver code; an incorrect bit position can change unrelated fields, route traffic through the wrong virtual channel, overconstrain credits, leave clock gating disabled, fail to clear errors, or decode fatal errors incorrectly.

Large repeated client blocks are susceptible to generator or copy/paste drift. The `RDCLI*` and `WRCLI*` families are intentionally repetitive, but even one inconsistent mask would affect only one hardware client and could appear as a workload-specific GPU hang, bandwidth regression, or VM fault.

Read/write address/data path separation is another hazard. Write address DAGB and write data DAGB registers look similar but are distinct. Using the wrong macro family could configure burst or lazy timer behavior for the wrong pipeline stage.

Status and command fields share registers in some families. Code that clears or enables bits without preserving unrelated fields can accidentally drop fatal status, alter interrupt policy, or change request blocking. Consumers should prefer read-modify-write helpers with the correct masks.

The file ends mid-register for `DAGB0_SDP_CGTT_CLK_CTRL` in this chunk. Any per-file analysis or generated documentation must reconcile this with the following chunk before treating that register as fully documented.

## Test Signals

Useful signals for validating code that depends on this chunk include:

- Successful compile of `amdgpu/mmhub_v3_0.c` with `mmhub_3_0_0_offset.h` and this header included together.
- GPU boot without MMHUB register-access faults on ASICs using MMHUB 3.0.0.
- Correct GART/VM initialization, TLB invalidation, and MMHUB protection fault reporting in `dmesg`.
- Clock-gating tests that toggle `DAGB0_CNTL_MISC2` fields and observe expected power/performance behavior without hangs.
- Stress workloads that exercise display, HDP, SDMA, JPEG/VCN, and IO/GMI clients without read/write pending bitmaps sticking.
- Performance counter configuration that increments, clears, triggers, and saturates according to `DAGB0_PERFCOUNTER*` settings.
- Error-injection or fault tests that populate `DAGB0_SDP_ERR_STATUS` and `DAGB0_FATAL_ERROR_STATUS*` fields with decodable client, address, VF, tag, operation, and fatality information.
