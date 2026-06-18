# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 25015-27550

## Scope And Purpose

This chunk is generated AMD NBIF 6.3.1 register bitfield metadata. It contains no executable C code, functions, structs, allocation, locking, or direct MMIO operations. Its public interface is a large set of C preprocessor constants describing bit shifts and masks for PCIe/NBIO virtual-function register fields.

The line range starts in the middle of `BIF_BX_DEV0_EPF0_VF0_GPU_HDP_FLUSH_DONE`, covering the reserved-engine tail and all mask definitions for VF0's HDP flush-done register. It then defines VF0 transaction-pending, mailbox, system PF/VF decode, RCC error/configuration, and GFX MSI-X vector fields. The range fully covers the repeated VF1 through VF7 blocks and ends at the opening of VF8's `BIF_ATOMIC_ERR_LOG` definitions. Because the chunk boundaries are artificial, the beginning depends on the previous chunk for the first VF0 flush-done shift fields and the end depends on the next chunk for the rest of VF8.

The purpose of these macros is to let AMDGPU NBIF/NBIO code name hardware bitfields instead of hard-coding numeric masks. The macros are paired with register offsets from `nbif_6_3_1_offset.h` and consumed by field helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15_PREREG`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

Although this repository is rooted under `distributed-fs/ceph-client`, this file is Linux AMD GPU driver hardware metadata. It is not Ceph filesystem code and has no filesystem persistence behavior.

## Important Macro Families

The chunk uses the generated convention `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. The covered range contains 2065 `#define` lines, including 1026 shift definitions and 1071 mask definitions.

The `BIF_BX_DEV0_EPF0_VF*_BIF_BME_STATUS` registers expose `DMA_ON_BME_LOW` status and `CLEAR_DMA_ON_BME_LOW`. These fields track and clear DMA activity observed while PCI bus-master enable was low, which is relevant to virtualization and PCIe error diagnosis.

The `BIF_BX_DEV0_EPF0_VF*_BIF_ATOMIC_ERR_LOG` registers log unsupported-request atomic conditions: opcode, request-enable-low, length, and non-relaxed ordering, plus matching clear bits in the upper half of the register. VF1 through VF7 are complete here; VF0 began in the previous chunk and VF8 begins at the chunk tail.

The `DOORBELL_SELFRING_GPA_APER_*` registers define per-VF self-ring doorbell GPA aperture base high/low values and aperture controls. The control fields include enable, mode, and size. These are security- and isolation-sensitive because doorbell apertures let GPU clients signal queues through mapped MMIO/GPA windows.

The HDP coherency control families include `HDP_REG_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_ONLY_CNTL`, and `HDP_MEM_COHERENCY_INVALIDATE_ONLY_CNTL`. Each exposes a small address/control field used to trigger host data path register or memory coherency operations.

The `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` families publish a 32-bit engine bitmap. Fields cover command processor engines `CP0` through `CP9`, `SDMA0`, `SDMA1`, and reserved engine bits `RSVD_ENG0` through `RSVD_ENG19`. Request bits initiate HDP flushes for engines; done bits report completion. The VF0 done masks are at the start of this chunk; complete request/done pairs are present for VF1 through VF7.

The `BIF_TRANS_PENDING` registers expose `BIF_MST_TRANS_PENDING` and `BIF_SLV_TRANS_PENDING`, used to observe outstanding master/slave transactions before reset, power transitions, or virtualization state changes.

The mailbox block for each VF includes four transmit dwords, four receive dwords, `MAILBOX_CONTROL`, `MAILBOX_INT_CNTL`, and `BIF_VMHV_MAILBOX`. The basic mailbox control bits are transmit valid/ack and receive valid/ack. Interrupt control bits enable valid and ack interrupts. The VM/HV mailbox packs small transmit/receive data fields, valid/ack flags, and interrupt-enable bits for hypervisor/virtual-machine communication.

The `SYSPFVFDEC` block defines indirect MMIO access registers `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI`. `MM_INDEX` carries a 31-bit offset and an aperture bit, `MM_INDEX_HI` carries the high offset, and `MM_DATA` carries the 32-bit data payload.

The `RCC_DEV0_EPF0_VF*_RCC_*` families describe per-VF RCC error and configuration registers. They include SR-IOV invalid register access status, doorbell read access status, doorbell aperture enable, configured memory size, reserved configuration data, and `RCC_IOV_FUNC_IDENTIFIER` with a function identifier bit and an IOV enable bit.

The `RCC_DEV0_EPF0_VF*_GFXMSIX_*` block defines four MSI-X vector table entries per VF in this range. Each vector has low/high message address, message data, and a `MASK_BIT` control field. The `GFXMSIX_PBA` register exposes pending bits for vector 0 and vector 1.

## Control Flow And Runtime Use

There is no runtime control flow in this header. The only behavior is C preprocessing: driver code names a register field, and the compiler substitutes the generated shift and mask constants.

Runtime sequencing lives in the AMDGPU NBIF/NBIO implementation. `amdgpu/nbif_v6_3_1.c` includes both `nbif_6_3_1_offset.h` and this mask header. It uses the same generated register stack to read the NBIF revision ID, get memory size from `RCC_DEV0_EPF0_RCC_CONFIG_MEMSIZE`, configure doorbell aperture enable, program doorbell ranges, remap HDP registers for KFD, provide HDP flush request/done offsets, configure interrupt handling, set the MMIO remap window, and handle the RAS ATHUB interrupt path.

The direct NBIF 6.3.1 implementation mostly uses PF0, BIF_BX0, GDC, PCIE, and non-VF RCC register families rather than every VF-specific macro in this chunk. The VF macro families still form the same hardware interface for SR-IOV/virtualization flows, diagnostics, firmware/hypervisor programming, and future code that needs to address per-VF doorbell, mailbox, HDP flush, transaction, RCC, or MSI-X state.

Older and sibling NBIO implementations in the tree show the common VF0 HDP remap pattern: in SR-IOV or when the normal MMIO hole cannot be used, `rmmio_remap.reg_offset` may be based on a VF0 HDP memory coherency flush register offset. That pattern explains why the VF HDP fields are important even when most NBIF 6.3.1 code paths use PF0 register names.

## State And Persistence Behavior

The header itself stores no state and performs no I/O. Its constants become part of compiled driver code wherever included.

The described hardware registers are device state. Doorbell aperture base/control values, RCC memory size/configuration, IOV enable/function identifier, MSI-X vector address/data/mask fields, and mailbox interrupt enables persist in hardware until reset, power loss, function reset, firmware/hypervisor reprogramming, or driver reinitialization.

Several fields are live status or sticky error state. `DMA_ON_BME_LOW`, atomic unsupported-request flags, BIF master/slave transaction pending bits, mailbox valid/ack bits, VM/HV mailbox valid/ack bits, MSI-X pending bits, and HDP flush-done bits may change asynchronously as hardware, firmware, host, or guest activity proceeds.

Several fields are command-like or clear-on-write by naming. `CLEAR_DMA_ON_BME_LOW`, the atomic error clear fields, HDP flush request bits, mailbox ack bits, and interrupt clear/ack style bits must be handled with the access semantics expected by the hardware specification. The generated mask file does not distinguish read-only, write-one-to-clear, pulse, sticky, firmware-owned, or reserved behavior; callers must know that from the register spec and implementation context.

## Dependencies And Integration Points

The immediate dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_offset.h`, which supplies the matching `reg...` offsets and base indices. This shift/mask header supplies only field layout; it is not sufficient to address registers by itself.

The primary implementation integration point is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c`. That file includes this header and uses AMDGPU SOC15 register helpers to program NBIF/NBIO hardware. It exposes the `amdgpu_nbio_funcs` table for higher-level AMDGPU code, including HDP flush offsets, PCIe indirect offsets, memory-controller access, memory-size query, doorbell range setup, interrupt handling, ASPM programming, register remap setup, and RAS interrupt registration.

The fields also integrate indirectly with GPUVM/KFD and queue signaling because HDP flush and doorbell aperture setup affect coherency and queue wakeup behavior. The KFD MMIO remap path uses HDP flush remap registers so user-mode compute paths can reach a controlled MMIO window.

SR-IOV and hypervisor integration is central to this chunk. Per-VF register families define isolation surfaces for doorbells, mailbox messaging, MSI-X vectors, transaction drain status, invalid register access logging, and IOV function identity. Mistakes in these masks can affect guest/host communication, interrupt routing, or memory aperture isolation.

Display code under `drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c` includes `nbif_6_3_1_offset.h`, showing that NBIF 6.3.1 register addresses can be shared outside the core `amdgpu/nbif_v6_3_1.c` file. This chunk's field masks remain part of the same generated register contract even when a particular consumer only needs offsets.

## Risks And Edge Cases

The largest risk is treating generated metadata as ordinary editable code. A one-bit shift or mask error can make valid driver logic write the wrong hardware bit while still compiling cleanly.

Chunk boundaries are incomplete. VF0 `GPU_HDP_FLUSH_DONE` begins before this range, and VF8 `BIF_ATOMIC_ERR_LOG` continues after it. Any final per-file analysis must merge adjacent chunks before claiming complete coverage for those two registers.

The repeated VF blocks invite copy/paste and wrong-function mistakes. VF1 through VF7 have nearly identical field layouts and offsets in the matching offset header. Code must select the correct VF register namespace and address window for the function it is managing; using VF0 masks or offsets for a different VF can target the wrong virtual function.

Doorbell aperture and RCC IOV fields are isolation-sensitive. Wrong base, size, enable, or IOV identity masks can expose doorbell pages incorrectly, prevent a guest from signaling queues, or allow access patterns outside the intended function boundary.

Mailbox fields are handshake-oriented. Setting valid/ack bits out of order, failing to preserve unrelated bits during read-modify-write, or mishandling interrupt enables can wedge host/guest mailbox communication or lose messages.

HDP flush request/done fields are coherency-sensitive. Incorrect masks for CP or SDMA engines can make the driver believe a flush completed for the wrong engine, which can surface as stale CPU/GPU views of memory, compute queue corruption, or hard-to-reproduce synchronization failures.

MSI-X vector fields are interrupt-routing-sensitive. Address low fields start at bit 2 and mask off alignment bits; incorrect packing can program unaligned message addresses or mask/unmask the wrong vector. PBA fields in this chunk expose only two pending bits despite four vector entries, so consumers should not assume a one-to-one complete pending-bit layout without checking the full hardware spec.

Status and clear fields sit close together in several registers. Read-modify-write helpers must be used carefully where write-one-to-clear or pulse semantics exist, otherwise diagnostic evidence may be cleared or command bits may be retriggered.

## Test Signals

Build coverage should compile AMDGPU paths that include `nbif_6_3_1_sh_mask.h`, especially `amdgpu/nbif_v6_3_1.c`. Macro drift normally appears as compile failures in `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15_PREREG`, or register-offset references.

Static validation should compare this generated mask header against `nbif_6_3_1_offset.h` and the source register database used to generate both files. Useful checks include verifying every field has a matching `__SHIFT` and `_MASK`, masks align with their shifts and widths, and repeated VF1-VF7 blocks remain structurally identical where expected.

Runtime smoke tests on NBIF 6.3.1 hardware should cover NBIF initialization, memory-size readback, doorbell aperture enable/disable, SDMA/VCN/IH/GC doorbell range setup, HDP flush request/done polling, MMIO remap setup, and RAS ATHUB interrupt enable/clear paths.

SR-IOV tests should exercise PF and VF boot, guest doorbell signaling, mailbox transmit/receive valid/ack handshakes, per-VF MSI-X programming and masking, and invalid-register-access/error-log reporting. Tests should include VF1 through VF7 explicitly because this chunk fully defines those repeated blocks.

Coherency tests should trigger CP and SDMA HDP flushes and verify that the expected done bits are observed before CPU-visible memory is consumed. Failures may appear as queue timeouts, stale memory, or inconsistent KFD/user-mode queue behavior.

Error-path tests should trigger or simulate BME-low DMA status, unsupported atomic request logs, BIF transaction-pending observation, RCC invalid-access status, and MSI-X pending state, then verify that clear bits clear only the intended latched status.

Regression indicators include mailbox timeouts, missing or misrouted interrupts, VF doorbell failures, unexpected SR-IOV isolation faults, HDP flush hangs, stale-memory symptoms after flush, incorrect memory-size reporting, persistent BIF transaction-pending bits during reset, or RAS ATHUB interrupt clear failures.
