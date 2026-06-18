# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 5054-7579

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header segment. It contains 2,063 preprocessor `#define` entries across 2,526 source lines. There are no C functions, structs, enums, variables, allocations, locks, or executable statements in this range.

The range starts inside the `VF8` virtual-function register template at `BIF_BX_DEV0_EPF0_VF8_GPU_HDP_FLUSH_DONE`, covers all corresponding BIF/RCC system PF/VF decode and MSI-X register field maps for `VF9` through `VF14`, and then enters `VF15` through `RCC_DEV0_EPF0_VF15_GFXMSIX_VECT1_ADDR_LO__MSG_ADDR_LO__SHIFT`. The boundaries are artificial: the `VF8` flush-request fields are before this chunk, and the rest of `VF15` MSI-X vector definitions continue after it.

## Purpose

`nbio_4_3_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 4.3.0 hardware interface. For each named NBIO register, it provides:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position for extracting or packing a field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate, preserve, or compose that field.

The matching register offsets live in `nbio_4_3_0_offset.h`; consumers include the generated offset and mask headers together. This chunk specifically maps SR-IOV virtual-function NBIO/BIF/RCC registers for endpoint function 0. The repeated `BIF_BX_DEV0_EPF0_VF<n>_*` and `RCC_DEV0_EPF0_VF<n>_*` namespaces describe per-VF state for DMA enable reporting, atomic-operation error logging, doorbell aperture selection, HDP coherency flush/invalidate control, PF/VF mailbox messaging, indirect MMIO access, SR-IOV decode errors, and MSI-X message routing.

## Important Macro Families

The `BIF_BX_DEV0_EPF0_VF*_BIFPFVFDEC1` families define per-VF BIF-facing state:

- `BIF_BME_STATUS` exposes whether bus-master enable is set for the VF.
- `BIF_ATOMIC_ERR_LOG` reports atomic-operation error status, including `ERR_VALID`, `ERR_UPID`, `ERR_ADDR`, `ERR_OPCODE`, `ERR_FUNC_NUM`, and `ERR_VF`.
- `DOORBELL_SELFRING_GPA_APER_BASE_HIGH`, `DOORBELL_SELFRING_GPA_APER_BASE_LOW`, and `DOORBELL_SELFRING_GPA_APER_CNTL` define the guest physical doorbell aperture base, size, select-ring enable, and process-isolation logic.
- `HDP_REG_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_ONLY_CNTL`, and `HDP_MEM_COHERENCY_INVALIDATE_ONLY_CNTL` provide coherency flush and invalidate controls.
- `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` expose 32 engine bits for command processors `CP0` through `CP9`, `SDMA0`, `SDMA1`, and reserved engines `RSVD_ENG0` through `RSVD_ENG19`.
- `BIF_TRANS_PENDING` exposes master and slave transaction-pending bits used for quiesce/reset sequencing.
- `NBIF_GFX_ADDR_LUT_BYPASS` controls address LUT bypass behavior.
- `MAILBOX_MSGBUF_TRN_DW[0-3]` and `MAILBOX_MSGBUF_RCV_DW[0-3]` define four-word transmit and receive buffers.
- `MAILBOX_CONTROL`, `MAILBOX_INT_CNTL`, and `BIF_VMHV_MAILBOX` define valid/ack handshakes, interrupt enables, compact message data fields, and VM/hypervisor mailbox status.

The `BIF_BX_DEV0_EPF0_VF*_SYSPFVFDEC` families define an indirect MMIO access path:

- `MM_INDEX` contains a 31-bit `MM_OFFSET` and the `MM_APER` selector bit.
- `MM_DATA` carries the 32-bit data payload.
- `MM_INDEX_HI` extends the offset through `MM_OFFSET_HI`.

The `RCC_DEV0_EPF0_VF*_BIFPFVFDEC1` families define RCC-side virtualization and configuration state:

- `RCC_ERR_LOG` has status bits for invalid SR-IOV register access and doorbell-read access.
- `RCC_DOORBELL_APER_EN` exposes the BIF doorbell aperture enable bit.
- `RCC_CONFIG_MEMSIZE` and `RCC_CONFIG_RESERVED` carry full-width configuration values.
- `RCC_IOV_FUNC_IDENTIFIER` contains a function identifier bit and high `IOV_ENABLE` bit.

The `RCC_DEV0_EPF0_VF*_BIFDEC2` families define graphics MSI-X state:

- `GFXMSIX_VECT[0-3]_ADDR_LO` and `_ADDR_HI` carry the MSI-X message address. The low address field starts at bit 2 and masks the lower alignment bits.
- `GFXMSIX_VECT[0-3]_MSG_DATA` carries the 32-bit MSI-X message data.
- `GFXMSIX_VECT[0-3]_CONTROL` exposes the vector mask bit.
- `GFXMSIX_PBA` exposes pending bits for the four MSI-X vectors.

## APIs, Types, And Functions

There are no runtime APIs or C types in this chunk. The public interface is the generated macro namespace. Runtime code normally combines these masks with register offsets and AMDGPU helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, and `WREG32_SOC15`.

The macros are untyped integer constants with an `L` suffix. They encode bit layout only; they do not encode register access method, privilege, reset behavior, write-one-to-clear semantics, polling requirements, or whether a field is read-only, write-only, sticky, or side-effecting.

## Control Flow

This header has no local control flow. Runtime flow is external:

1. AMDGPU or firmware-facing code selects a register offset from `nbio_4_3_0_offset.h`.
2. The caller reads, modifies, writes, polls, or decodes the register using the `__SHIFT` and `_MASK` constants from this header.
3. Hardware implements the state transition, such as mailbox valid/ack exchange, HDP flush completion, transaction quiesce, doorbell aperture programming, MSI-X vector delivery, or error-log update.

Important external flows represented by this chunk include VF bring-up, SR-IOV PF/VF isolation, virtual doorbell mapping, PF/VF or hypervisor mailbox communication, HDP cache coherency maintenance before command submission or reset, transaction-drain checks before reset or teardown, indirect MMIO access through `MM_INDEX/MM_DATA`, and MSI-X interrupt setup and masking.

## State And Persistence Behavior

The header stores no state. It names hardware-visible state in NBIO/BIF/RCC registers for SR-IOV virtual functions. Persistence is controlled by GPU reset domains, PF-managed SR-IOV lifecycle, VF function-level reset, suspend/resume save/restore, firmware initialization, and explicit driver writes.

Represented state includes:

- VF bus-master status and transaction-pending state.
- Atomic-operation error logs and invalid-access logs.
- Doorbell aperture base, size, enable, and process-isolation controls.
- HDP register and memory coherency flush/invalidate request and completion bits.
- PF/VF mailbox buffers, valid/ack flags, and interrupt enables.
- Indirect MMIO index/data registers.
- RCC configuration memory size, reserved configuration storage, IOV enablement, and function identifier state.
- MSI-X message address, message data, per-vector mask bits, and pending-bit-array state.

Several fields are not ordinary storage bits. HDP flush request bits are paired with done bits and generally require polling/order guarantees. Error-log status bits can be sticky or clear-on-write depending on the hardware register contract. Mailbox valid/ack bits are protocol state and can deadlock if producer and consumer order is wrong. MSI-X address/data/control fields directly affect interrupt routing. Doorbell and IOV fields affect virtualization isolation and DMA-facing access.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 4.3.0 register set:

- `nbio_4_3_0_offset.h` supplies matching register addresses and base indices.
- `nbio_4_3_0_sh_mask.h` supplies the field layout documented here.
- Other generated NBIO headers may provide defaults or companion register metadata for the same IP block.

Observed include-level integration in this tree includes `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, SMU 13 power-management files such as `pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `pm/swsmu/smu13/smu_v13_0_7_ppt.c`, and DCN 3.2 display resource files that include the NBIO 4.3.0 offset header. The macros integrate with AMDGPU NBIO initialization, power management, SR-IOV virtualization paths, interrupt delivery, register debugging, reset/quiesce sequencing, and firmware or hypervisor mailbox protocols.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata and has no direct distributed-filesystem behavior.

## Risks And Edge Cases

- Generated bitfield drift can compile successfully while making runtime code touch the wrong hardware bit. The highest-risk fields here are doorbell aperture controls, IOV enablement, MSI-X routing, HDP flush request/done bits, and mailbox valid/ack bits.
- The chunk starts and ends inside repeated VF templates. Merge/reconciliation must not treat the missing `VF8` flush-request prefix or incomplete `VF15` MSI-X suffix as source omissions.
- Per-VF repetition is intentional. A mismatch among `VF9` through `VF14` may be meaningful generator/register-database drift, but boundary truncation for `VF8` and `VF15` must be accounted for first.
- Mailbox fields combine payload, valid, ack, and interrupt-enable bits. Incorrect masking or write ordering can lose messages, duplicate notifications, or wedge PF/VF synchronization.
- HDP coherency bits gate correctness between CPU-visible memory, GPU engines, and DMA. Wrong engine masks or polling logic can leave stale data visible to command processors or SDMA engines.
- Doorbell aperture and process-isolation fields affect guest access to doorbells. Wrong base, size, enable, or process-isolation logic can cause missed submissions or cross-tenant isolation failures.
- MSI-X vector address/data/control/PBA fields affect interrupt routing. Bad masks can cause lost, spurious, or misdirected interrupts.
- Atomic and RCC error logs are diagnostic and possibly sticky; treating them as ordinary writable state can clear evidence or fail to clear real fault conditions.

## Test Signals

- Build AMDGPU with NBIO 4.3 support enabled. Missing or misspelled generated macros should be caught by consumers of the header set.
- Runtime probe on affected AMD GPUs should show stable NBIO initialization and no register-access faults for NBIO 4.3.0 paths.
- SR-IOV tests should enumerate multiple VFs and verify that VF-specific doorbell, mailbox, MM index/data, and interrupt state does not alias across VFs.
- Doorbell tests should validate programmed guest physical aperture base/size, enable state, and process-isolation behavior under VF command submission.
- Coherency tests should exercise HDP flush request/done paths for CP and SDMA engines and verify data visibility after command submission, reset, and queue teardown.
- Mailbox tests should verify four-DW transmit/receive payload transfer, valid/ack handshakes, and interrupt-enable behavior in both PF-to-VF and VF-to-PF directions.
- MSI-X tests should verify vector address/data programming, per-vector masking, PBA pending bits, and interrupt delivery for vectors 0 through 3.
- Error-injection or fault-path tests should verify atomic error logging, invalid SR-IOV register access reporting, doorbell-read access reporting, and preservation/clear behavior for diagnostic status fields.
