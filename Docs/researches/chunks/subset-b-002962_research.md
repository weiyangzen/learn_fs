# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 2526-5053

## Scope

This chunk is a generated AMD NBIO 4.3.0 register shift/mask header segment. It contains only C preprocessor constants; there are no functions, structs, enums, variables, loops, branches, allocations, locking paths, or direct MMIO accesses in the assigned range.

The slice starts inside the `RCC_DEV0_EPF0_VF0` register-control/configuration block, covers the VF0 graphics MSI-X table and pending-bit-array masks, then fully repeats the same per-virtual-function NBIF/RCC register families for VF1 through VF7. It begins VF8 at `BIF_BX_DEV0_EPF0_VF8_BIF_BME_STATUS` and stops at the end of the `BIF_BX_DEV0_EPF0_VF8_GPU_HDP_FLUSH_REQ` masks; the VF8 flush-done, transaction-pending, mailbox, MMIO index/data, RCC, and MSI-X masks continue after this chunk.

Although the file is under a local `ceph-client` source mirror, this header is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this range is to publish bit positions for NBIO 4.3.0 SR-IOV virtual-function register windows. Each generated field is represented as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to pack or extract a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or update a field.

Runtime AMDGPU code combines these constants with matching generated register offsets, especially `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h` and related NBIF offset headers, through helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The VF0 portion is a boundary fragment. It includes the tail of `RCC_DEV0_EPF0_VF0_RCC_DOORBELL_APER_EN`, complete masks for VF0 `RCC_CONFIG_MEMSIZE`, `RCC_CONFIG_RESERVED`, and `RCC_IOV_FUNC_IDENTIFIER`, then the VF0 `GFXMSIX` table under the `nbio_nbif0_rcc_dev0_epf0_vf0_BIFDEC2` address block. The MSI-X vector fields define low/high message address dwords, message data dwords, per-vector mask bits for vectors 0 through 3, and a two-bit pending-bit array.

VF1 through VF7 each have a complete `BIFPFVFDEC1` NBIF register group. The group starts with `BIF_BME_STATUS`, which records DMA activity while bus-master enable is low and supplies a clear bit, and `BIF_ATOMIC_ERR_LOG`, which records unsupported PCIe atomic cases such as opcode, request-enable-low, length, and non-relaxed ordering cases with paired clear bits.

Each full VF block defines a self-ring doorbell aperture: high and low GPA aperture base dwords plus `DOORBELL_SELFRING_GPA_APER_CNTL` enable, mode, and size fields. These fields describe the guest-visible or VF-visible doorbell mapping used by engines to submit work through MMIO doorbells.

Each full VF block defines HDP coherency controls. `HDP_REG_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_ONLY_CNTL`, and `HDP_MEM_COHERENCY_INVALIDATE_ONLY_CNTL` expose one-bit flush or invalidate addresses. `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` each allocate all 32 bits to engine request/done flags: CP0 through CP9, SDMA0 and SDMA1, followed by reserved engine bits 0 through 19. These are used to coordinate GPU-side register and memory visibility.

Each full VF block defines `BIF_TRANS_PENDING` master/slave transaction-pending bits and `NBIF_GFX_ADDR_LUT_BYPASS`. The transaction flags are important reset and quiesce signals because they indicate whether NBIF traffic is still outstanding.

Each full VF block defines mailbox data and handshake registers. `MAILBOX_MSGBUF_TRN_DW0` through `DW3` and `MAILBOX_MSGBUF_RCV_DW0` through `DW3` are full-width message-buffer dwords. `MAILBOX_CONTROL` contains transmit valid/ack and receive valid/ack bits. `MAILBOX_INT_CNTL` enables valid and ack interrupts. `BIF_VMHV_MAILBOX` packs VM/HV mailbox interrupt enables, four-bit transmit and receive message payloads, valid bits, and ack bits into one register.

Each full VF block defines a `SYSPFVFDEC` indirect MMIO aperture with `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI`. `MM_INDEX` carries a 31-bit offset plus an aperture selector bit, `MM_DATA` is a full-width data dword, and `MM_INDEX_HI` carries the high offset dword.

Each full VF block defines RCC error/configuration fields. `RCC_ERR_LOG` records invalid SR-IOV register accesses and doorbell read access status. `RCC_DOORBELL_APER_EN` exposes the BIF doorbell aperture enable bit. `RCC_CONFIG_MEMSIZE` and `RCC_CONFIG_RESERVED` are full-width configuration dwords. `RCC_IOV_FUNC_IDENTIFIER` carries a one-bit function identifier and an `IOV_ENABLE` bit at bit 31.

Each full VF block ends with an RCC `BIFDEC2` graphics MSI-X table. For each of vectors 0 through 3, the table exposes message address low bits 31:2, message address high bits 31:0, message data bits 31:0, and one mask bit. The per-VF `GFXMSIX_PBA` pending-bit-array field covers pending bits 0 and 1 in this NBIO 4.3.0 slice.

The VF8 portion is another boundary fragment. It covers `BIF_BME_STATUS`, `BIF_ATOMIC_ERR_LOG`, self-ring doorbell aperture base/control, HDP register/memory flush/invalidate control dwords, and all `GPU_HDP_FLUSH_REQ` shift/mask bits. The matching VF8 `GPU_HDP_FLUSH_DONE` and later state are outside this work item.

## Control Flow

There is no executable control flow in this header. Runtime behavior occurs only in code that includes these generated constants:

1. AMDGPU selects a generated register offset such as a `regBIF_*`, `regRCC_*`, or matching SOC15 register identifier.
2. It reads, composes, or updates a 32-bit register value through the NBIO/NBIF access layer.
3. It applies this header's `__SHIFT` and `_MASK` macros directly or through `REG_SET_FIELD`/`REG_GET_FIELD`.
4. It writes a doorbell, mailbox, MSI-X, coherency, transaction, error-clear, or configuration value, or polls a hardware-owned status bit.

Typical consumers are NBIO setup, SR-IOV virtual-function management, doorbell aperture programming, HDP flush/remap setup, VM/HV mailbox messaging, MSI-X interrupt delivery, and reset/quiesce paths that need to know whether VF traffic is pending.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed register state owned by the GPU, firmware, platform PCIe/SR-IOV configuration, host kernel policy, and AMDGPU's NBIO/NBIF management code.

The represented state includes VF doorbell aperture base/enable/size/mode, memory-size and reserved configuration values, IOV function enable/identity, atomic-error and invalid-access logs, BME-low DMA diagnostics, HDP flush and invalidate request/done state, transaction-pending status, indirect MMIO index/data state, mailbox payload and handshake bits, mailbox interrupt enables, MSI-X vector address/data/mask fields, and MSI-X pending bits.

Some fields are static configuration or capability-like values, some are software-programmed controls, some are hardware-updated status, and some are sticky diagnostics with explicit clear bits. The generated masks do not encode reset defaults, access permissions, write-one-to-clear semantics, polling timeouts, ownership boundaries, or ordering requirements; those rules must come from the NBIO/NBIF programming sequence and hardware documentation.

## Dependencies And Integration Points

The primary dependency is the generated NBIO/NBIF register database. This chunk must remain synchronized with the matching offset headers, especially `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h` and the NBIF 6.3.1 offset/mask headers that expose the same VF-oriented register naming in neighboring generated files.

Direct in-tree NBIO 4.3 users include `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c` and SMU13 power-management files such as `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`. The local `nbio_v4_3.c` code includes this header and uses adjacent NBIO masks for revision ID decoding, memory-size reads, doorbell aperture control, HDP flush remapping, interrupt setup, and clock/power controls.

The most relevant integration surfaces for this chunk are:

- SR-IOV VF register windows for VF0 through VF8.
- Doorbell and self-ring doorbell aperture setup.
- HDP memory/register coherency flush and invalidate operations.
- GPU engine flush request/done handshakes for CP and SDMA engines.
- Transaction-pending checks during reset, quiesce, or function teardown.
- VM/HV mailbox message transport and mailbox interrupt signaling.
- VF graphics MSI-X vector programming and pending-bit handling.
- RCC error logging for invalid SR-IOV accesses and doorbell read attempts.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts after the VF0 `RCC_DOORBELL_APER_EN` shift definition and stops after VF8 `GPU_HDP_FLUSH_REQ`; adjacent chunks are required for complete VF0 and VF8 analysis.
- These are untyped preprocessor constants. A stale mask or shift can compile cleanly while extracting or programming the wrong hardware bit.
- The VF blocks are mechanically repetitive. Off-by-one suffix mistakes around VF1 through VF8 can silently target the wrong virtual function and affect SR-IOV isolation, guest interrupt delivery, or diagnostics.
- Register-offset and field-mask mismatches are easy in generated headers. A valid VF4 mask applied to a VF5 offset, or an NBIO mask applied to an NBIF offset with a different generation, may still produce plausible-looking register operations.
- Doorbell aperture fields affect GPU command submission. Incorrect base, size, mode, or enable values can cause missed submissions, writes to the wrong aperture, or guest/host isolation problems.
- HDP coherency fields are ordering-sensitive. Missing or incorrect flush/invalidate request and done handling can leave stale CPU-visible or GPU-visible data, especially across queue submission, VM updates, reset, or power transitions.
- Flush request/done fields are dense 32-bit bitmaps. Engine-bit mislabeling can cause software to wait on the wrong engine, skip a required flush, or time out during reset.
- Mailbox valid/ack fields are handshake state. Incorrect clear/set ordering or interrupt-enable handling can lose PF/VF messages, wedge VM/HV communication, or produce interrupt storms.
- MSI-X address/data/mask/PBA fields directly affect interrupt delivery. Width mistakes, address-low alignment mistakes, stale mask bits, or pending-bit confusion can cause lost, misrouted, or unexpectedly masked interrupts.
- Error-log and clear bits may be sticky or write-one-to-clear. Generic read/modify/write treatment can erase diagnostic evidence or fail to clear latched error state.
- `MM_INDEX`/`MM_DATA` indirect access fields can reach broad register space. Incorrect aperture or high-offset handling can redirect indirect accesses to unrelated registers.

## Test Signals

Useful validation is mostly build-time, generated-header consistency, and hardware-integration oriented:

- Build AMDGPU with NBIO 4.3 support enabled; missing, renamed, or duplicated macros should surface in `nbio_v4_3.c`, SMU13 files, or generated-header include paths.
- Compare this chunk against `nbio_4_3_0_offset.h` and neighboring NBIF generated headers to confirm VF suffixes, register names, base indices, and repeated VF strides stay synchronized.
- Boot affected NBIO 4.3 hardware and confirm memory-size, doorbell aperture, interrupt, HDP remap, and clock/power paths still initialize without register-access faults.
- In SR-IOV configurations, create and remove VFs spanning VF0 through VF8, bind guest drivers, and verify VF isolation, doorbell writes, mailbox messaging, MSI-X delivery, and reset behavior.
- Exercise graphics, compute, and SDMA workloads while monitoring HDP flush request/done progress; stale data, timeout logs, or hung queues can indicate flush bit or offset drift.
- Exercise VF reset, suspend/resume, runtime power transitions, and quiesce flows while checking `BIF_TRANS_PENDING` and engine flush done state.
- Trigger or observe mailbox traffic between PF/hypervisor and VFs; lost valid/ack transitions or unexpected mailbox interrupts point to mailbox field layout problems.
- Exercise MSI-X masking/unmasking and interrupt-heavy workloads; lost interrupts or stuck pending bits can indicate vector table or PBA field mismatches.
- Use SR-IOV error and diagnostics paths, where available, to verify BME-low DMA status, atomic error logging, invalid register access logging, and doorbell read status map to expected bits.

## Chunk Notes

- Lines 2526-2538 are the tail of VF0 RCC configuration and IOV identifier masks.
- Lines 2540-2592 cover VF0 graphics MSI-X vector and PBA masks.
- Lines 2596-4937 cover complete VF1 through VF7 NBIF/RCC/SYSPFVFDEC/MSI-X mask groups.
- Lines 4941-5053 begin VF8 and stop after `BIF_BX_DEV0_EPF0_VF8_GPU_HDP_FLUSH_REQ__RSVD_ENG19_MASK`.
- The assigned range contains 2,065 `#define` entries for 374 register-name prefixes, with 1,032 shift definitions and 1,033 mask definitions.
