# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_sh_mask.h lines 2367-4719

## Scope

This chunk covers 2,353 lines from the generated AMD MMHUB 1.8.0 shift/mask header. It starts inside the `DAGB1_RD_VC4_CNTL` field group at `DAGB1_RD_VC4_CNTL__MAX_BW__SHIFT`, continues through the rest of the DAGB1 read and write data-arbitration group B field definitions, includes DAGB1 status, fatal-error, performance-counter, and L1 TLB register fields, then enters the `aid_mmhub_dagb_dagbdec2` address block for DAGB2 read/write field definitions. The slice ends inside `DAGB2_WR_ADDR_DAGB_LAZY_TIMER0`, after the `CLIENT1_MASK` field; the remaining `CLIENT2..CLIENT7` masks and later DAGB2 write fields are outside this chunk.

The range contains 2,185 `#define` macros and no C functions, structs, enums, storage objects, inline helpers, or executable statements. The macros define bit positions and masks only; the companion `mmhub_1_8_0_offset.h` file supplies register offsets such as `regDAGB1_*` and `regDAGB2_*`.

## Purpose

`mmhub_1_8_0_sh_mask.h` is a generated hardware-register field map for the AMDGPU MMHUB 1.8.0 block. This chunk describes the per-field layout of DAGB1 and part of DAGB2, where DAGB means data arbitration group B in the MMHUB register namespace. These registers shape how MMHUB read and write clients are assigned to virtual channels, how bandwidth and outstanding-data limits are applied, how credits are distributed across TLB, storage, EA, GMI, OSD, and read-return paths, and how status/debug/performance information is exposed.

The header lets driver code use `REG_SET_FIELD`, `REG_GET_FIELD`, and direct mask operations with named fields instead of hard-coded bit arithmetic. For example, a caller can set `DAGB1_CNTL_MISC2__DISABLE_WRREQ_CG_MASK` or use fields from a `DAGB*_WRCLI_GPU_SNOOP_OVERRIDE` register while the offset header identifies the actual MMIO register number.

## Important APIs, Types, And Data

The exported API is the macro namespace. Major groups in this chunk are:

- `DAGB1_RD_VC4_CNTL` tail plus complete `DAGB1_RD_VC5_CNTL`, `DAGB1_RD_VC6_CNTL`, and `DAGB1_RD_VC7_CNTL`: read virtual-channel credit, max/min bandwidth, OSD limiter, and max outstanding-data fields. The chunk boundary omits the first three `DAGB1_RD_VC4_CNTL` shifts, which are immediately above line 2367.
- `DAGB1_RD_CNTL_MISC`, `DAGB1_RD_TLB_CREDIT`, `DAGB1_RD_RDRET_CREDIT_CNTL`, and `DAGB1_RD_RDRET_CREDIT_CNTL2`: read-side shared pool, EA, IO, TLB, read-return FIFO, VC-mode, and equality-fix credit controls.
- `DAGB1_RDCLI_*_PENDING`, `DAGB1_RDCLI_NOALLOC_OVERRIDE`, and `DAGB1_RDCLI_NOALLOC_OVERRIDE_VALUE`: busy/status bitmaps and no-allocation override controls for read clients.
- `DAGB1_WRCLI0` through `DAGB1_WRCLI15`: per-write-client virtual-channel assignment and throttling fields. Each client has `VIRT_CHAN`, `CHECK_TLB_CREDIT`, `URG_HIGH`, `URG_LOW`, `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `OSD_LIMITER_ENABLE`, and `MAX_OSD` masks.
- `DAGB1_WR_CNTL`, `DAGB1_WR_GMI_CNTL`, `DAGB1_WR_ADDR_DAGB`, and `DAGB1_WR_DATA_DAGB`: global write-side clock/window, IO-level, GMI, address-DAGB, data-DAGB, jump-ahead, self-init, `WHOAMI`, and jump-mode fields.
- `DAGB1_WR_OUTPUT_DAGB_*`, `DAGB1_WR_ADDR_DAGB_*`, and `DAGB1_WR_DATA_DAGB_*`: 4-bit per-VC or per-client max-burst and lazy-timer fields. The `*_0` registers cover clients 0-7 and `*_1` registers cover clients 8-15.
- `DAGB1_WR_VC0_CNTL` through `DAGB1_WR_VC7_CNTL`, `DAGB1_WR_CNTL_MISC`, `DAGB1_WR_TLB_CREDIT`, `DAGB1_WR_DATA_CREDIT`, `DAGB1_WR_MISC_CREDIT`, `DAGB1_WR_OSD_CREDIT_CNTL1/2`, and `DAGB1_WR_ATOMIC_FIFO_CREDIT_CNTL1`: write-side virtual-channel credit, bandwidth, OSD, TLB, GMI, pool, data FIFO, miscellaneous, atomic, and return-credit fields.
- `DAGB1_WRCLI_GPU_SNOOP_OVERRIDE` and `_VALUE`: bitmaps controlling per-write-client GPU snoop override enable/value behavior. In `mmhub_v1_8.c`, SDMA is treated as bit 15 in these registers.
- `DAGB1_WRCLI_*_PENDING` and `DAGB1_WRCLI_DBUS_*_PENDING`: write-client busy/status bitmaps for ask/go/global-send/TLB/OARB/OSD/DBUS stages.
- `DAGB1_DAGB_DLY`, `DAGB1_CNTL_MISC`, and `DAGB1_CNTL_MISC2`: delay, disable, disable-self-init, reset, interrupt, and clock-gating controls. `DAGB1_CNTL_MISC2` includes fine-grained clock-gating disable bits for write request/return, read request/return, TLB write/read, and tap-chain clock gating.
- `DAGB1_FATAL_ERROR_CNTL`, `_CLEAR`, and `_STATUS0..3`: fatal-error enable, clear, and status fields for read requests/responses, write requests/responses, TLB, credits, OSD, DAGB state machines, and DBUS conditions.
- `DAGB1_FIFO_EMPTY`, `DAGB1_FIFO_FULL`, `DAGB1_WR_CREDITS_FULL`, and `DAGB1_RD_CREDITS_FULL`: status bitmaps for request, data, read-return, TLB, OSD, DBUS, and credit FIFOs.
- `DAGB1_PERFCOUNTER_LO/HI`, `DAGB1_PERFCOUNTER0_CFG`, `DAGB1_PERFCOUNTER1_CFG`, `DAGB1_PERFCOUNTER2_CFG`, and `DAGB1_PERFCOUNTER_RSLT_CNTL`: local performance counter result, selector, enable, clear, and latency-measurement fields.
- `DAGB1_L1TLB_REG_RW`: register-read/write pass-through controls for L1 TLB access, with `REGISTER_INDEX`, `REGISTER_WR_DATA`, `REGISTER_RD_DATA`, `REGISTER_RW_SEL`, `REGISTER_ACCESS`, and `REGISTER_STATUS` fields.
- `DAGB2_RDCLI0..15`, `DAGB2_RD_*`, `DAGB2_WRCLI0..15`, and early `DAGB2_WR_*` groups: the same generated field pattern for the next DAGB instance, starting at the `aid_mmhub_dagb_dagbdec2` address block. This chunk reaches through `DAGB2_WR_ADDR_DAGB_LAZY_TIMER0__CLIENT1_MASK`.

The field layouts are highly regular. Per-client write/read client controls use low bits for VC selection and credit checks, mid bits for urgency and bandwidth controls, and high bits for OSD limits. Per-VC credit registers use repeated 4-bit, 5-bit, or 6-bit fields. Busy, override, FIFO, full, and error registers commonly expose 16-bit or 32-bit bitmaps.

## Control Flow

This header has no runtime control flow. It participates in runtime behavior when a C file includes the mask header and writes or reads MMHUB registers with SOC15 helpers:

1. `amdgpu/mmhub_v1_8.c` includes both `mmhub_1_8_0_offset.h` and this shift/mask header.
2. Initialization calls `mmhub_v1_8_init_snoop_override_regs()` during `mmhub_v1_8_gart_enable()`.
3. That function computes the register-distance between `regDAGB1_WRCLI_GPU_SNOOP_OVERRIDE` and `regDAGB0_WRCLI_GPU_SNOOP_OVERRIDE`, then loops over five DAGB instances by applying the same distance from DAGB0.
4. For each MMHUB instance in `adev->aid_mask`, the driver reads `regDAGB0_WRCLI_GPU_SNOOP_OVERRIDE` and `regDAGB0_WRCLI_GPU_SNOOP_OVERRIDE_VALUE`, sets bit 15 for SDMA, and writes the values back. The named field masks in this chunk define the DAGB1 layout corresponding to that repeated hardware pattern.
5. Other fields in this chunk are available to debug, RAS, clock-gating, performance, firmware, or future initialization paths even when current `mmhub_v1_8.c` only directly references the snoop override register offsets from this range.

The chunk also aligns with older and newer MMHUB implementations that manipulate DAGB fields, especially `DAGB1_CNTL_MISC2` clock-gating masks in `mmhub_v1_7.c`, `mmhub_v3_0.c`, `mmhub_v4_1_0.c`, and `mmhub_v4_2_0.c`. That reuse pattern is important because generated register families tend to preserve names while offsets and exact field availability vary by IP version.

## State And Persistence Behavior

The macros are compile-time constants and persist no software state. The hardware registers they describe are stateful MMIO registers whose contents persist until reset, suspend/resume restoration, GPU reset, firmware programming, or another driver write changes them.

Important state classes described by this chunk include:

- Per-client routing state: `RDCLI*` and `WRCLI*` fields assign clients to virtual channels and configure urgency, credit checks, bandwidth limits, and OSD limits.
- Credit and arbitration state: `*_CREDIT`, `*_CNTL`, `*_MAX_BURST*`, and `*_LAZY_TIMER*` fields tune request admission and return-resource allocation. Bad values can persistently starve clients or overcommit FIFOs.
- Snoop override state: `WRCLI_GPU_SNOOP_OVERRIDE` and `_VALUE` hold per-client policy bits. `mmhub_v1_8_init_snoop_override_regs()` sets SDMA snoop override during GART enable for non-SR-IOV-VF devices.
- Clock/power-gating state: `*_CGTT_CLK_CTRL`, `DAGB1_CNTL_MISC`, and `DAGB1_CNTL_MISC2` fields can force or disable clock-gating behavior. These affect power and availability rather than normal kernel memory.
- Diagnostic state: pending, FIFO empty/full, credits-full, fatal-error status, and performance-counter registers expose live hardware state. Clear and control fields such as `DAGB1_FATAL_ERROR_CLEAR` and `DAGB1_PERFCOUNTER_RSLT_CNTL__PERFCOUNTER_CLEAR_MASK` can modify diagnostic state.
- L1 TLB indirect access state: `DAGB1_L1TLB_REG_RW` holds an index, write data, read data, access select, access trigger, and status for low-level TLB register access.

There is no disk state, allocation, reference counting, locking, or software-owned lifetime in the header. Ordering, concurrency, reset sequencing, and SR-IOV policy are imposed by the AMDGPU MMHUB/GMC callers and by firmware.

## Dependencies

This chunk depends on the generated MMHUB 1.8.0 register specification and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_offset.h`, which defines the corresponding `regDAGB1_*` and `regDAGB2_*` register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.c`, the local MMHUB 1.8 consumer that includes this file and programs DAGB snoop override state.
- SOC15 register helpers and field helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD`.
- AMDGPU runtime state used by the consumer path: `struct amdgpu_device`, `adev->aid_mask`, `for_each_inst()`, SR-IOV checks such as `amdgpu_sriov_vf()`, GMC/GART enable sequencing, and PSP-mediated programming for other MMHUB registers.
- Related generated MMHUB versions where similar DAGB field names are consumed by clock-gating code. Cross-version copy/paste is common in AMDGPU register programming, so field-name drift between versions is a practical dependency.

The macros use the conventional generated naming form `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`. Callers rely on exact spelling for `REG_SET_FIELD` expansion and on exact mask/shift values for direct bit operations.

## Integration Points

- `mmhub_v1_8_init_snoop_override_regs()` programs the write-client GPU snoop override/value register family. Although it starts from DAGB0 offsets, it uses the DAGB instance spacing to reach DAGB1 and later DAGBs; the `DAGB1_WRCLI_GPU_SNOOP_OVERRIDE*` field definitions in this chunk document the bit layout for one of those repeated instances.
- `mmhub_v1_8_gart_enable()` invokes snoop override setup after GART aperture, system aperture, TLB, and cache setup, and before system-domain, identity-aperture, VMID, and invalidation programming.
- `amdgpu_sriov_vf(adev)` gates snoop override setup out for SR-IOV VFs. That matters because these registers affect client-level routing and coherency policy and may be PF/host-owned in virtualized environments.
- Clock-gating integration is visible by analogy with other MMHUB versions that use `DAGB1_CNTL_MISC2` masks to enable or disable DAGB request/return and TLB clock gating. The MMHUB 1.8 `set_clockgating` hook is currently a stub, but the generated masks in this chunk are the register interface it would use if implemented.
- Debug and bring-up tools can use the pending, FIFO, fatal-error, perf-counter, and L1TLB pass-through fields to inspect hardware state or clear latched conditions. These are not surfaced as normal userspace APIs in this header, but they are part of the driver-visible register contract.
- DAGB2 groups in this chunk integrate with the same repeated-register model as DAGB1. The offset header places `regDAGB2_*` after DAGB1, and code can compute instance-relative distances when the hardware layout is regular.

## Risks

- Generated-field drift is the central risk. A wrong shift or mask compiles cleanly but causes the driver to modify the wrong bits in MMHUB hardware.
- The chunk boundaries split register groups. `DAGB1_RD_VC4_CNTL` is incomplete at the start, and `DAGB2_WR_ADDR_DAGB_LAZY_TIMER0` is incomplete at the end. Merge/reconciliation should avoid treating either group as fully documented by this chunk alone.
- Per-client and per-VC fields are highly repetitive. A single off-by-one client index, virtual-channel index, or DAGB instance distance can apply bandwidth, snoop, credit, or lazy-timer settings to the wrong client.
- Snoop override bits affect coherency. The current MMHUB 1.8 path explicitly sets SDMA bit 15 so SDMA writes probe/invalidate read-write lines; losing or misplacing that bit can create subtle stale-cache behavior.
- Credit, bandwidth, max outstanding-data, max-burst, and lazy-timer fields affect arbitration fairness and progress. Bad values can starve display/media/SDMA clients, overrun FIFOs, or cause hangs that look like unrelated VM faults.
- Clock-gating override and disable fields can break low-power behavior or, if toggled without sequencing, stall a live hardware block.
- Fatal-error clear/status fields are stateful diagnostics. Clearing too broadly can erase evidence needed by RAS or postmortem handling; enabling too broadly can convert recoverable conditions into fatal flows.
- L1 TLB indirect register access fields are low-level debug/programming controls. Incorrect index, access select, or trigger values can touch internal TLB state outside normal MMHUB setup paths.
- SR-IOV ownership matters. PF, VF, PSP, or firmware may own subsets of DAGB and TLB controls, so direct writes in VF mode can be blocked, ignored, or unsafe.

## Test Signals

- Build coverage: compile AMDGPU with MMHUB 1.8 support. Because this is a generated macro header, missing or renamed fields primarily surface as compile failures in `mmhub_v1_8.c` or related consumers.
- Register-write trace coverage: during `mmhub_v1_8_gart_enable()`, confirm non-SR-IOV paths read and write the DAGB write-client GPU snoop override and value registers for each enabled AID/MMHUB instance, and confirm SR-IOV VF paths skip those writes.
- Functional coherency signal: SDMA write workloads that interact with GPU-cached read/write lines should not exhibit stale data after the SDMA snoop override bit is programmed.
- VM/GART regression signal: MMHUB GART enable/disable, VMID setup, invalidation, and fault-default tests should remain stable after any change to this generated field file, even if the touched fields are not directly in the high-level VM aperture path.
- Debug/RAS signal: fatal-error status/clear, FIFO empty/full, credits-full, pending, and perf-counter reads should decode consistently with hardware documentation and should not show impossible bit combinations after idle or stress runs.
- Power-management signal: if clock-gating support is added for MMHUB 1.8 using `DAGB1_CNTL_MISC2` or `*_CGTT_CLK_CTRL` fields, validate suspend/resume, runtime clock-gating flags, and stress workloads under both enabled and disabled clock-gating states.
