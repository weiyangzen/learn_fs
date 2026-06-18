# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 106884-109353

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.2.0 shift/mask header. It defines preprocessor constants for field bit positions and masks in NBIO/NBIF PCIe endpoint, downstream-port, root-complex control, BIF, GDC, MSI-X, and PCIe bridge configuration registers.

The range is generated hardware metadata, not executable driver logic. Its role is to let C code use symbolic field names with AMDGPU register helpers instead of open-coded bit positions. Register addresses come from the matching `nbio_7_2_0_offset.h`; this header supplies only field geometry.

This work item starts in the middle of `RCC_EP_DEV0_3_EP_PCIE_TX_CNTL` at the mask definitions and ends in the middle of `BIFPLR0_1_LINK_CNTL` before the final `DRS_SIGNALING_CONTROL_MASK` line. Adjacent chunks are required for a complete per-file view.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, enums, or runtime APIs in this range. The public surface is 2,136 `#define` constants: 1,066 `__SHIFT` definitions and 1,070 `_MASK` definitions. The extra masks are caused by the chunk starting after the first five `RCC_EP_DEV0_3_EP_PCIE_TX_CNTL__*__SHIFT` lines while stopping just before one trailing `BIFPLR0_1_LINK_CNTL` mask.

Macro naming follows the generated register database convention:

- `<REGISTER>__<FIELD>__SHIFT` is the field's starting bit.
- `<REGISTER>__<FIELD>_MASK` is the shifted mask used for extraction, insertion, or testing.
- Prefixes such as `RCC_EP`, `RCC_DWN`, `RCC_DWNP`, `RCC_DEV0`, `BIF_BX2`, `BIF_BX_PF2`, `GDC1`, and `BIFPLR0_1` identify hardware address blocks and instances, not C objects.

The chunk covers 295 register-name groups across these address blocks:

- `nbio_nbif0_rcc_dwn_dev0_BIFDEC1`
- `nbio_nbif0_rcc_dwnp_dev0_BIFDEC1`
- `nbio_nbif0_rcc_dev0_epf0_BIFPFVFDEC1[13440..14975]`
- `nbio_nbif0_rcc_dev0_BIFDEC1`
- `nbio_nbif0_bif_bx_BIFDEC1`
- `nbio_nbif0_bif_bx_pf_BIFPFVFDEC1`
- `nbio_nbif0_gdc_GDCDEC`
- `nbio_nbif0_rcc_dev0_epf0_BIFDEC2`
- `nbio_iohub_nb_nbcfg_nb_cfgdec`
- `nbio_iohub_nb_pciedummy0_pciedummy_cfgdec`
- `nbio_pcie0_bifplr0_cfgdecp`

## Register Coverage

The opening endpoint RCC section finishes `RCC_EP_DEV0_3_EP_PCIE_TX_CNTL` masks for SNR/relaxed-ordering overrides and TPH disable bits for functions 0-2, then covers endpoint requester ID, AER/error control, RX error-ignore policy, completion-timeout disable, PASID/prefix handling, TPH receive disable, and Gen2/Gen3/Gen4 link-speed strap enables.

The `RCC_DWN_DEV0_3` downstream block provides whole-register reserved/scratch fields, HWINIT write lock, unsupported-request reporting disable, LTR unsupported-request handling, extended-tag override, FLR extend mode, PMI and completion-timeout policy, hidden config-register decode enables for Gen2-Gen4, function-0 strap enables, MSI multi-message capability straps, clock power management strap, 64-bit master-address strap, and master-completion-timeout strap.

The `RCC_DWNP_DEV0_3` downstream-port block repeats a narrower endpoint-like control set: AER timer/error-message controls, RX ignore/timeout policy, Gen2-Gen4 link-speed strap enables, data-link-state and link-bandwidth notification disables, multi-function strap, and a full-width `LTR_MSG_INFO_FROM_EP` field.

The `RCC_DEV0_EPF0_1` BIFPFVF decode block exposes per-function or replicated PF/VF-oriented registers for invalid SR-IOV access and doorbell-read error logging, doorbell aperture enables, config memory size/reserved dwords, and IOV function identifiers. The same block reappears later in this chunk for graphics MSI-X table/PBA fields: vectors 0-3 each have address low/high, message data, and vector-control definitions, with three replicated entries per field, followed by PBA bitmaps.

The `RCC_DEV0_*` BIFDEC1 block covers broader device-level RCC controls: error interrupt control, BACO miscellaneous control, reset enable, vendor-defined-message support, PCIe margining parameter controls, GPU IOV region and host-VM enablement, console IOV VF offset/stride controls, peer register ranges, bus-control policy, config aperture sizing, XDMA low/high fields, feature-control miscellaneous bits, bus-number capture/listing, host bus number, peer framebuffer offsets for peers 0-3, devfn lists, device/common link controls, endpoint requester ID restore, LTR low-power switch control, and multi-host arbitration control.

The `BIF_BX2` block is the largest block in this range. It includes BIF strap and pinstrap fields, indirect MM access control, bus-control bits for BIOS scratch access, ordering, page request, memory access, interrupt, non-BAR DMA, poisoned-request handling, FLR/host behavior, and partial write/write-combine behavior. It also includes scratch registers, reset controls, interrupt controls, pad controls, BIF feature-control fields, doorbell control and interrupt policy, frame-buffer enable, pending master/slave VF transaction status, BACO controls and exit timers, memory type, NBIF GFX address LUT control and LUT entries 0-15, 32-bit VF enable/status bitmaps for register writes, doorbells, and framebuffer access, HDP remap flush controls, ring-buffer control/base/read/write pointers, mailbox index, GPU IOV config sizes for VCN and SDMA/GFX, PERST/PX/REFCLK/CLKREQ/PWRBRK/WAKE/VAUX pad controls, save/restore control, S5 memory power controls, and dummy registers.

The `BIF_BX_PF2` PF-specific block provides BME status, atomic error logging with request type/tag and address fields, self-ring doorbell GPA aperture base/control, HDP coherency flush/invalidate controls, per-VF GPU HDP flush/invalidate request and done bitmaps, transaction-pending fields, LUT bypass, four transmit mailbox dwords, four receive mailbox dwords, mailbox control bits for valid/ack handshakes, mailbox interrupt control, and a VMHV mailbox register.

The `GDC1` block covers doorbell and NGDC controls. It includes SDP port controls, SHUB register interface control, MP4SDP and MGCG controls, reserved dwords, SOCCLK SDP controls, NBIF GFX doorbell status, doorbell range offset/size fields for SDMA0-5, IH, VCN0/1, and RLC, ATDMA control and status bits, doorbell fence address/match/enable/action fields, S2A miscellaneous timeout and ordering controls, early wakeup, power-gating master/slave controls, and SHUBCLK dynamic power-management controls plus read/write weights and counters.

The ending `BIFPLR0_1` bridge configuration block begins a PCI/PCIe bridge config-space map. This chunk covers vendor/device IDs; command and status bits; revision, class, cache-line, latency, header, and BIST bytes; bus-number and latency register; IO, memory, and prefetchable base/limit windows; secondary status; prefetchable upper base/limit; IO upper base/limit; capability pointer; ROM BAR; interrupt line/pin; bridge control; extended bridge control; vendor capability list; adapter ID; PM capability and status/control; PCIe capability header; device capability/control/status; link capability; and most of link control.

## Control Flow and Runtime Behavior

There is no control flow in this header. The effective runtime flow is external:

1. ASIC-specific AMDGPU code includes `nbio_7_2_0_offset.h` and `nbio_7_2_0_sh_mask.h`.
2. Callers select a register offset such as a `regRCC_*`, `regBIF_BX2_*`, `regGDC1_*`, or `regBIFPLR0_1_*` symbol from the offset header.
3. The macros in this chunk are passed to field helpers such as `REG_GET_FIELD` and `REG_SET_FIELD`, or used directly in read-modify-write code.
4. Actual side effects occur through AMDGPU MMIO, SMN, or PCIe/config-space register accessors outside this generated header.

The represented hardware flows include PCIe request/response policy, error-reporting and AER policy, FLR and link notification behavior, bus-number and peer-address routing, GPU virtualization aperture and VF-permission programming, doorbell routing and monitoring, HDP flush/invalidate handshakes, PF mailbox handshakes, GDC power/clock/doorbell controls, MSI-X vector programming, and bridge config-space enumeration/link control.

## State and Persistence

The file owns no state, performs no I/O, allocates no memory, and persists nothing. State lives in NBIO, BIF, GDC, RCC, and PCIe bridge hardware registers.

State categories represented by this chunk include:

- Policy state: error-reporting disables, completion-timeout disables, RX ignore bits, TPH disables, relaxed-ordering/SNR overrides, hidden config decode enables, bus-control bits, link notification disables, link-control bits, and clock/power-management straps.
- Identity and routing state: requester ID fields, bus-number captures/lists, host bus number, devfn lists, IOV function identifiers, peer register ranges, peer framebuffer offsets, config apertures, and bridge IO/memory/prefetchable windows.
- Virtualization and aperture state: GPU IOV region/host-VM enable, console IOV VF offset/stride, VF register-write/doorbell/framebuffer enable bitmaps, matching status bitmaps, doorbell aperture enables, GDC doorbell ranges, and self-ring GPA aperture controls.
- Diagnostic and status state: invalid SR-IOV access logs, doorbell-read access logs, atomic error logs, transaction-pending bits, HDP flush/invalidate done bits, GDC doorbell status, ATDMA status, SHUBCLK counters, PCI status/device status/link status fields, and MSI-X PBA bits.
- Firmware and power-management state: BACO controls and timers, S5 memory power controls, pad controls, early wakeup and power-gating controls, PMI/PME fields, and bridge power-management capability fields.
- Interrupt and message state: interrupt control, doorbell interrupt control, mailbox transmit/receive dwords and valid/ack bits, mailbox interrupt control, MSI-X vector address/data/control, and bridge interrupt line/pin fields.

Retention across warm reset, FLR, BACO, S5, suspend/resume, or full GPU reset is not specified by this header. Callers must rely on hardware documentation and initialization code to know which fields are sticky, write-one-to-clear, reset-on-FLR, or restored by driver/firmware.

## Dependencies and Integration Points

The main source-tree dependency is the generated NBIO 7.2.0 register-header set. This file must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h`, which provides the matching register address macros. This tree does not have a same-generation `nbio_7_2_0_default.h`, so reset/default values for these exact fields cannot be derived from a companion default header here.

The direct C integration point is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which includes both the offset and shift/mask headers. Display resource files for DCN 3.0.1 and DCN 3.1 include the NBIO 7.2.0 offset header for base/register integration, although they do not directly include this shift/mask header in the searched tree.

Likely runtime consumers are NBIO setup, PCIe/NBIO link and error-handling paths, SR-IOV and GPU virtualization setup, doorbell programming, HDP flush/invalidate paths, BACO/power-management paths, PF/VF mailbox handling, MSI-X setup, and debug/diagnostic code that decodes PCIe bridge and BIF status registers.

Semantic dependencies include the PCI and PCI Express specifications for standard bridge config-space fields, PM capability, PCIe device/link capability and control/status fields, MSI-X table/PBA semantics, AER/error-reporting behavior, requester IDs, FLR behavior, LTR and TPH behavior, and link training/link-bandwidth notification policy. The generated names do not encode access permissions, legal values, side effects, or ordering requirements.

## Risks and Maintenance Notes

- Boundary splitting is intentional here. `RCC_EP_DEV0_3_EP_PCIE_TX_CNTL` shifts are in the previous chunk, and `BIFPLR0_1_LINK_CNTL__DRS_SIGNALING_CONTROL_MASK` is on the next source line after this chunk.
- A wrong mask or shift can silently program the wrong hardware bit. In this range that can affect PCIe error reporting, link behavior, requester identity, VF isolation, doorbell access, HDP coherency, mailbox handshakes, power transitions, or bridge resource windows.
- Many blocks are highly repetitive. VF enable/status bitmaps, GFX MSI-X vector replicas, GDC doorbell ranges, NBIF address LUT entries, HDP flush request bitmaps, and bridge config fields differ mostly by index or suffix.
- Full-width `0xFFFFFFFFL` fields appear for scratch, reserved, mailbox, LUT, MSI-X address/data, PBA, and log-style registers. A full-width mask only describes field geometry; it does not mean writing all ones is safe.
- Fields named `*_STATUS`, `*_ERR_LOG`, `*_PENDING`, `*_DONE`, or bridge status bits may be hardware-updated, sticky, clear-on-read, or write-one-to-clear depending on the register. The header does not provide those semantics.
- Straps and HWINIT/write-lock fields can reflect hardware initialization policy. Treating them as ordinary mutable software settings can conflict with firmware or reset sequencing.
- Virtualization-related masks control PF/VF isolation and access to registers, doorbells, and framebuffer resources. Misprogramming can expose resources to the wrong VF or block a valid VF from making progress.
- Mailbox valid/ack fields require protocol sequencing by the caller. The masks alone do not prevent lost messages, double-acknowledgement, or stale payload reads.
- Bridge config-space fields must be consistent with platform enumeration. Incorrect resource-window or link-control programming can break PCIe enumeration, routing, or link stability.

## Test and Validation Signals

Useful validation signals for this chunk are:

- Build coverage for AMDGPU configurations that compile `amdgpu/nbio_v7_2.c` and include NBIO 7.2.0 generated headers.
- Generated-header consistency checks that every complete register in lines 106884-109353 has paired `__SHIFT` and `_MASK` definitions, while explicitly allowing the start/end boundary exceptions.
- Cross-checks against `nbio_7_2_0_offset.h` so each register family documented here has a matching address/offset symbol and the same ASIC-generation prefix.
- Mechanical symmetry checks across repeated fields: VF 0-31 enable/status bitmaps, NBIF GFX LUT entries 0-15, HDP flush/invalidate request/done bitmaps, GDC doorbell ranges, MSI-X vectors 0-3 with `_1` and `_2` replicas, and bridge capability fields.
- Hardware readback tests on NBIO 7.2.0 ASICs that decode PCIe bridge config space and compare vendor/device/class, command/status, PM, PCIe device/link, and resource-window fields with `lspci -vvxxx` or equivalent debug dumps.
- PCIe error-path tests that exercise AER/error reporting, completion timeout policy, RX ignore controls, link bandwidth/state notifications, and requester-ID restoration without unexpected link drops.
- SR-IOV or virtualization tests that verify VF register-write, doorbell, framebuffer, IOV identifier, config aperture, console IOV, and peer framebuffer routing behavior.
- Doorbell and HDP coherency tests that verify doorbell ranges/status, doorbell monitor/interrupt policy, self-ring apertures, HDP flush/invalidate request bits, and done bits.
- Mailbox protocol tests that send and receive PF messages using the transmit/receive dwords and valid/ack control bits, including interrupt generation where enabled.
- Power-management tests around BACO, S5 memory power, pad controls, clock/power gating, PME/PMI state, and link retraining to confirm driver reinitialization restores required policy fields.
