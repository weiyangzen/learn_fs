# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 7370-9764

## Scope

This chunk is a generated AMD GC 11.5.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` value and a matching `_MASK` value used by AMDGPU register helpers to compose or decode 32-bit MMIO/indexed-register values. There are no functions, structs, enums, variables, dynamic allocations, locks, callbacks, persistence helpers, or executable branches in this range.

The selected range starts in the tail of `RMI_UTCL1_CNTL1` masks, then covers RMI/UTCL1 controls and status, GC VM shared page-fault and virtual-context aperture registers, GCVM L2 page-table cache and protection-fault controls, ATC L2 and L2 TLB translation-assist registers, per-VMID GCVM context controls for contexts 0-15, and invalidate-engine request/ack/address fields for engines 0-17. It ends at the beginning of `GCVM_INVALIDATE_ENG7_ADDR_RANGE_LO32`; the rest of that address-range family continues in a later chunk.

Although this repository path is under a `ceph-client` mirror, this source is AMDGPU DRM graphics-core hardware metadata, not filesystem implementation.

## Purpose

`gc_11_5_0_sh_mask.h` supplies bit layouts for GC 11.5.0 registers. Driver code pairs these constants with register addresses from the matching GC 11.5.0 offset header and uses common AMDGPU helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` to update or decode individual fields without embedding magic bit positions.

This chunk is centered on address translation, cache invalidation, VM fault handling, and VM apertures:

- RMI and UTCL1 controls expose GPUVM response modes, client invalidation controls, LFIFO/cache-depth reductions, write-combine/reorder controls, scoreboard flush tracking, RMI crossbar arbitration, clock controls, RB-to-GLX client-ID mapping, spare/chicken-bit fields, and redundancy settings.
- UTCL1 registers control per-client bypasses, forced range or global invalidation, page-size encodings, cache bank/way hashing, address-log behavior, and busy/XNACK/range-invalidation status.
- GCMC shared page-fault registers describe MMIO/PCI/TOM/FB/system aperture boundaries, default system aperture physical pages, steering, PF/VF virtual reset requests, active VF/VFID reporting, local/system memory aperture policy, local-FB lock control, and UTCL2/L2 clock-gating controls.
- GCVM L2 registers configure page-table cache behavior, protection-fault enable/default policy, dummy-page fault behavior, fault status/address/default-address capture, identity aperture and physical-offset mapping, cache bank/hash/RT-class selection, parity injection/checking, walker throttling, PTE-cache dump access, GCR settings, and credit-safety update hooks.
- ATC L2 and L2TLB registers define ATS/ATC request concurrency, cache invalidation behavior, cache entry dump data, parity status, clock/memory power controls, SDP port clock gating, TLB status, and GPUVA/VMID translation-assist request/response payloads.
- VM context registers repeat the same context-enable, page-table depth/block-size, retry, and fault interrupt/default controls for GCVM contexts 0 through 15, followed by a context-disable bitmap.
- Invalidate-engine registers provide semaphores, per-VMID invalidation requests, flush type, L2 PTE/PDE and L1 PTE invalidation controls, fault-address-clear requests, 4K-only invalidation mode, per-VMID ack bits, semaphore ack bits, and the first range-address low/high fields for engines 0 through 6 plus the start of engine 7.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register field mask.
- Register address symbols live in the companion `gc_11_5_0_offset.h` header, commonly with `mm...` names matching the register.
- AMDGPU callers normally consume these constants through register field helpers, read-modify-write MMIO helpers, debug dumps, VM invalidation code, reset paths, virtualization paths, and fault-handling paths.

Major macro families in this slice are:

- `RMI_UTCL1_CNTL1`, `RMI_UTCL1_CNTL2`, `RMI_UTC_UNIT_CONFIG`, `RMI_TCIW_FORMATTER*`, `RMI_SCOREBOARD_*`, `RMI_XBAR_ARBITER_CONFIG*`, `RMI_CLOCK_CNTRL`, `RMI_UTCL1_STATUS`, `RMI_RB_GLX_CID_MAP`, `RMI_SPARE*`, and `CC_RMI_REDUNDANCY`.
- `UTCL1_CTRL_1`, `UTCL1_HASH_CTRL`, `UTCL1_ALOG`, and `UTCL1_STATUS`, covering UTCL1 bypass/invalidation/page-size/hash/logging/status fields.
- `GCMC_VM_*` and `GCMC_SHARED_*` shared VM/aperture registers, including MMIO base/limit, PCI control, top-of-memory, FB offset, system aperture defaults, cacheable/local memory ranges, local FB ranges, AGP ranges, active function identity, virtual reset request, VA 1TB control, and L1 TLB control.
- `GCVM_L2_*`, `GCVML2_*`, and `GCUTCL2_*` page-table cache, fault, parity, bank selection, walker throttle, PTE cache dump, clock-gating, GCR, and credit-safety fields.
- `GC_ATC_L2_*`, `GCL2TLB_TLB0_STATUS`, and `GCUTC_GPUVA_VMID_TRANSLATION_ASSIST_*`, covering ATC L2 cache behavior and explicit translation-assist request/response registers.
- `GCVM_CONTEXT0_CNTL` through `GCVM_CONTEXT15_CNTL` and `GCVM_CONTEXTS_DISABLE`, giving per-context enable/page-table/fault behavior and disable bits.
- `GCVM_INVALIDATE_ENG[0-17]_{SEM,REQ,ACK}` plus `GCVM_INVALIDATE_ENG[0-6]_ADDR_RANGE_{LO32,HI32}` and the beginning of `GCVM_INVALIDATE_ENG7_ADDR_RANGE_LO32`.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow in consumers is:

1. Select the GC 11.5.0 register definitions for the active ASIC.
2. Choose the matching register address from `gc_11_5_0_offset.h`.
3. Read a current register value, prepare a register write, or decode a diagnostic/fault/status snapshot.
4. Use the `__SHIFT`/`_MASK` pairs, normally via helper macros, to pack a field value or extract one.
5. Execute the actual MMIO, indirect register access, polling loop, command submission, VM invalidation, debug dump, or recovery sequence in AMDGPU code.

For VM invalidation, higher-level code programs an invalidate engine semaphore/range, writes a request with per-VMID bits and cache-level controls, then polls or observes ack/semaphore state. For VM context setup, code programs page-table depth and fault policies per context and may use the disable bitmap to gate contexts. For protection faults, runtime code reads status and address registers, decodes VMID/client/perms/source/default behavior, may clear captured fault address state through invalidate request bits, and reports or recovers at the VM/KFD/AMDGPU layers. For UTCL1/GCVM/ATC cache controls, the actual ordering, drain, poll, timeout, and reset rules are not encoded here.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe GPU registers whose state is owned by hardware, firmware, and AMDGPU runtime programming.

RMI, UTCL1, GCVM L2, ATC L2, and aperture controls are persistent hardware configuration until changed, reset, lost through power transitions, or restored during resume/GPU reset. Many fields affect global address translation behavior: bypasses, page-size encodings, cache invalidation policy, cache fragment sizes, bank/hash selection, clock-gating overrides, walker throttles, and local/system/FB aperture boundaries. Incorrect values can persistently change translation correctness or performance across all clients using those paths.

Fault/status registers are mostly live or sticky hardware state. `GCVM_L2_PROTECTION_FAULT_STATUS` exposes fault attribution and access type fields, while address/default-address registers hold captured or programmed page information. `UTCL1_STATUS`, `GCVM_L2_STATUS`, `GC_ATC_L2_STATUS`, `GC_ATC_L2_STATUS2`, and `GCL2TLB_TLB0_STATUS` can change asynchronously with memory traffic, invalidations, parity events, and faults. The header does not express read-only, sticky, write-one-to-clear, self-clearing, or clear-on-read semantics.

`GCVM_CONTEXT0_CNTL` through `GCVM_CONTEXT15_CNTL` represent persistent per-VMID/context policy for page-table depth, block size, retry behavior, and whether specific protection faults interrupt or resolve to default pages. These settings directly shape how GPU VM faults are surfaced to the kernel, KFD, or userspace workloads.

Invalidate-engine registers represent short-lived synchronization and cache maintenance state. Semaphore, request, ack, and range-address fields must be coordinated with hardware sequencing. Per-VMID invalidation bitmaps cover up to 16 VMIDs per engine; request fields select flush type, L2 PTE/PDE invalidation, L1 PTE invalidation, optional fault-address clear, and 4K-only invalidation. Ack bits and range-address fields are hardware-owned during invalidation and should not be treated as ordinary persistent configuration.

Reserved and spare fields appear throughout the range. Callers should preserve undocumented bits during read-modify-write unless a golden setting or hardware workaround explicitly documents a full-register value.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.5.0 register family remaining synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h` provides matching register addresses.
- Any generated GC 11.5.0 default/header metadata must agree with these bit assignments where reset values or enumerations exist.
- AMDGPU VM, MM hub/GMC-adjacent code, GFX initialization, KFD/compute memory management, SR-IOV/virtualization, interrupt/fault handling, reset, suspend/resume, debugfs, and hang-dump paths can rely on these definitions.

Important integration points include VM context creation and teardown, GPUVM page-table setup, invalidation after PTE/PDE updates, VM fault reporting and recovery, dummy/default page behavior, cache/TLB parity diagnostics, address-range invalidation, ATS/ATC translation assistance, SR-IOV active function and virtual reset handling, local/system/FB aperture setup, clock/power gating golden settings, and low-level debug dump decoding.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but can set the wrong hardware bit, corrupt VM context policy, or misdecode a protection fault.
- The chunk boundaries are artificial. It starts after the `RMI_UTCL1_CNTL1` shifts and ends before the complete invalidate-engine range-address family, so adjacent chunks are needed for full register-family context.
- VM context controls are repeated 16 times. A generator or copy/paste mismatch affecting one `GCVM_CONTEXTn_CNTL` register could produce failures isolated to a subset of VMIDs or queues.
- Invalidate engines 0-17 are highly repetitive and sequencing-sensitive. Incorrect per-engine request, ack, or semaphore masks can make invalidations appear complete while stale PTE/PDE/TLB entries remain visible.
- Address fields are unit- and alignment-sensitive. Aperture, FB, AGP, default physical page, identity aperture, translation-assist, fault-address, and range-address fields are not necessarily raw byte addresses despite full-width-looking masks.
- Fault policy bits are security and correctness sensitive. Misprogramming interrupt/default handling for range, dummy page, PDE0, valid, read, write, or execute faults can hide real faults, over-report recoverable faults, or allow accesses to resolve through default pages unexpectedly.
- Virtualization fields such as PF/VF reset requests, active VF/VFID, request VMID/VFID/VF, client ID, and fault attribution must be decoded exactly for SR-IOV isolation and diagnostics.
- Clock-gating, credit-safety, walker-throttle, cache-fragment, bank-select, parity-injection, and spare/chicken-bit fields can cause performance cliffs or rare hangs if altered outside documented golden settings.
- Live status and counter-like fields can race with in-flight memory traffic. Polling code must use documented drains, timeouts, and stable-snapshot rules.
- The macros cannot encode access permissions. Full-width `DATA`, `ADDR`, or `STATUS` masks do not imply that arbitrary writes are valid or that readback is stable.

## Test Signals

Useful validation is primarily generated-data consistency, build coverage, and hardware/runtime VM testing:

- Kernel build coverage for AMDGPU files that include `gc_11_5_0_sh_mask.h` with the matching GC 11.5.0 offset header.
- Mechanical comparison against AMD's authoritative GC 11.5.0 register database for every shift/mask pair in this range.
- Static sanity checks that masks align with shifts, fields in each register do not overlap except documented aliases/reserved areas, all register names have matching address definitions, and repeated families remain structurally identical where expected.
- VM invalidation tests that update PTEs/PDEs, issue per-VMID and range invalidations through multiple invalidate engines, poll ack/semaphore bits, and verify stale mappings are not observed.
- GPUVM fault tests for invalid, read, write, execute, range, dummy-page, and PDE faults, checking interrupt/default-page behavior and decoded `GCVM_L2_PROTECTION_FAULT_STATUS` attribution.
- Context tests across VMIDs 0-15 to confirm page-table depth, block size, retry behavior, context disable bits, and per-context fault policy behave consistently.
- Suspend/resume and GPU reset tests that verify VM aperture, GCVM L2, UTCL1, ATC L2, and invalidate-engine state is reprogrammed or cleared as expected.
- SR-IOV/virtualization tests that trigger PF/VF reset requests, active-function changes, VM faults, and translation-assist operations, then validate VF/VFID/VMID/client attribution.
- ATC/ATS and translation-assist tests that exercise request/response fields, permissions, fragment size, TMZ, NACK/ACK, and no-PTE paths.
- Debug/hang-dump tests that verify UTCL1, GCVM L2, ATC L2, L2TLB, scoreboard, and protection-fault status fields decode coherently under memory traffic and fault injection.
- Regression signals include unexplained VM faults, stale mappings after invalidation, GPUVM page-table update races, KFD process eviction/restore failures, SR-IOV attribution errors, parity/fault status that cannot be cleared, translation-assist timeouts, or GPU reset loops near VM/cache invalidation paths.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002552`. It covers lines 7370-9764 of `gc_11_5_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the partial `RMI_UTCL1_CNTL1` and `GCVM_INVALIDATE_ENG7_ADDR_RANGE_LO32` families and to place the VM/invalidation metadata in the full GC 11.5.0 register map.
