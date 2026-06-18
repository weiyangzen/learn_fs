# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h lines 4858-7354

## Scope

This chunk is a generated AMDGPU NBIO 7.2.0 register-offset header segment. It contains 2,397 `#define` lines: 1,199 register-offset macros and 1,198 companion `_BASE_IDX` macros. There are no C functions, structs, enums, variables, loops, branches, allocations, locks, or executable statements in this range.

The range starts in the middle of `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp`, beginning at `regBIF_CFG_DEV0_RC0_SECONDARY_STATUS`, completes the remainder of the dev0 root-complex PCIe configuration block, covers complete dev1 and dev2 root-complex config blocks, then moves through NBIF system/PF windows, RCC strap tables, endpoint and downstream-port control blocks, RCC port-decoder copies for dev0/dev1/dev2, and the beginning of `nbio_nbif0_bif_misc_bif_misc_regblk` through `regBIFC_HSTARB_CNTL`. Adjacent chunks are required to see the earlier dev0 RC0 identity/command registers and the rest of the BIF misc register block.

Although the repository path is under a `ceph-client` source mirror, this file is AMD GPU hardware register metadata. It has no direct Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_2_0_offset.h` provides symbolic offsets for NBIO 7.2.0 registers. Each register macro names a hardware register and maps it to the offset value expected by AMDGPU's generated register access helpers. Each `_BASE_IDX` macro identifies the SOC15 base-index selector used with that offset; every macro in this chunk uses base index `5`.

The chunk gives driver code stable symbolic names for PCIe root-complex configuration, PCIe capability structures, advanced error reporting, virtual-channel/resource controls, lane margining, root-complex controller straps, endpoint/downstream port controls, NBIF mailbox and indirect MMIO windows, DMA attribute overrides, interrupt-line controls, BME/error logging, and host-arbitration/misc controls. The constants are meant to be paired with companion shift/mask/default headers and AMDGPU register helper macros rather than used as standalone behavior.

## Important Macro Families

The first family is the tail of `regBIF_CFG_DEV0_RC0_*` and complete `regBIF_CFG_DEV1_RC0_*` / `regBIF_CFG_DEV2_RC0_*` root-complex configuration blocks. These cover PCI bridge base/limit windows, capability pointers, ROM base, interrupt-line/pin/bridge control, power-management capability, PCIe capability, device/link/slot/root capabilities and controls, MSI, subsystem ID, MSI map, vendor-specific and virtual-channel enhanced capabilities, device serial number, AER status/mask/severity/header-log/root-error registers, TLP prefix logs, secondary PCIe capability, link-control 3, lane-error status, lane equalization controls for lanes 0-15, ACS capability/control, and lane margining controls/status for lanes 0-15.

The `nbio_nbif0_bif_bx_pf_SYSPFVFDEC` and `nbio_nbif0_bif_bx_SYSDEC` groups define PF1 indirect MMIO index/data access and system-level BIF/NBIF registers. These include PCIe index/data windows, scratch registers, mailbox registers, host-power-management control, revision ID, misc/project ID registers, MSI-to-SMI steering, BME reset/pending logging, debug mux, FLR controls, reset logic, clock request, hotplug/PME/DEC error interrupt status and masks, SERR/GFX interrupt status, SWUS/SWUS2 trap controls, and GFX MMIO register CAM programmable request/completion controls.

The `nbio_nbif0_rcc_strap_BIFDEC1:1` and `nbio_nbif0_rcc_strap_rcc_strap_internal` groups are strap-table definitions for the RCC and PCIe endpoints. They include common BIF straps, device/port straps, upstream/downstream port straps, Gen3/Gen4 equalization control, link configuration straps, PCIeP hardware-debug controls, ACPI/PME straps, PCIe clock/power controls, BAR/window sizing, DPA power-allocation straps, and EP function-specific strap sets for dev0/dev1/dev2. These macros describe latched hardware configuration policy exposed through NBIO register space.

The `RCC_EP_*`, `RCC_DWN_*`, and `RCC_DWNP_*` blocks repeat for dev0 in `BIFDEC1`, then for dev0/dev1/dev2 in `RCCPORTDEC`. Endpoint blocks define scratch/control, interrupt control/status, RX/TX/LTR/cfg/bus controls, strap misc registers, DPA capability/control/substate power allocation, PME control, TX requester ID, error control, RX control, and link-speed control. Downstream blocks define reserved/scratch/control/config/RX/bus/cfg/strap registers. Downstream-port blocks define error control, RX control, link-speed control, link-control 2, PCIeP strap misc, and LTR message information received from endpoints.

The `RCC_DEV*` controller blocks expose VDM support, bus control, feature/misc control, link control, common link control, requester-ID restore, LTR switch control, multi-host arbitration, and margining parameter controls. The earlier `regRCC_DEV0_1_*` group also includes RCC error interrupt control/status, signal outputs, feature toggles, power management, filter controls, address translation controls, tag controls, FLR controls, and BME error logging.

The `BIF_BX1_*` and `BIF_BX_PF1_*` groups cover BIF bridge/controller support around BME, interrupts, FLR, straps, debug, SDP, virtual-machine/hypervisor mailbox, and trap or shadow-access plumbing. The final partial `bif_misc` group begins global NBIF/BIF miscellaneous controls: BIOS strap control, scratch, interrupt-line polarity/enable, outstanding virtual-channel allocation, BIFC misc controls, BME error logs, link-controller timer control, RCC/BIH BME error logs, per-device/per-function DMA attribute override registers, DMA attribute control per device, dummy BME controls, and host arbitration control.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated preprocessor namespace:

- `reg<name>` macros provide register offsets.
- `reg<name>_BASE_IDX` macros provide the SOC15 base-index selector.

The header does not define bit positions, masks, reset values, access widths, read/write permissions, write-one-to-clear behavior, reset-domain ownership, or sequencing requirements. Consumers must combine these offsets with NBIO 7.2.0 shift/mask/default headers and AMDGPU access helpers such as SOC15 register read/write macros, PCI config-space access paths, SMN paths, or indirect MMIO helpers selected by the owning code. In this tree, `nbio_7_2_0_offset.h` is included by `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` and by DCN 3.01/3.1 display resource code.

## Control Flow

This header has no local runtime control flow. The implied external flow is:

1. ASIC-specific code selects an NBIO 7.2.0 register macro and base index.
2. The AMDGPU register helper computes the MMIO, config, or indirect access target for the active device.
3. Driver code reads status, decodes fields with companion shift/mask definitions, or writes a value that was composed according to the hardware spec.
4. Hardware side effects occur in PCIe/NBIO/RCC blocks, not in this header.

The register names point at hardware flows that are asynchronous to software: PCIe enumeration and bridge aperture setup, link training and equalization, lane-margining diagnostics, MSI and PME routing, AER status capture and clearing, virtual-channel/resource allocation, FLR/reset handling, strap-latched configuration, endpoint/downstream LTR messaging, BME and atomic/DMA attribute policy, mailbox communication, and interrupt/status propagation.

## State And Persistence Behavior

The header owns no memory and persists nothing. It describes addresses for hardware-visible state. Persistence of the represented state depends on PCIe reset, GPU reset domains, power-gating state, strap latch timing, BIOS/firmware initialization, PSP/SMU ownership, suspend/resume restore, and explicit driver writes.

Represented state includes PCI bridge identity/control/status, base/limit windows, capability and error-reporting status, link/slot/root state, lane equalization and margining controls/status, root-complex strap policy, endpoint/downstream port configuration, LTR and PME settings, DPA substate power allocation, requester IDs, BME and DMA attribute overrides, interrupt-line polarity/enables, scratch/mailbox contents, FLR/reset controls, and host arbitration settings.

Several register names indicate latched or side-effect-prone hardware state (`STATUS`, `INT_STATUS`, `ERR_LOG`, `SCRATCH`, `FLR`, `RESET`, `DPA`, `PME`, `LTR`, and strap registers). The offset header does not specify which bits are read-only, write-one-to-clear, sticky across resets, firmware-owned, or preserved across power transitions; callers must use the hardware programming guide and companion generated metadata.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.2.0 register database and must stay synchronized with sibling headers for shifts, masks, defaults, and other address forms. Cross-generation headers contain similarly named macros, but base indices and register coverage can differ; NBIO 7.2.0 consumers should include the generation-specific header selected by the ASIC implementation.

Primary integration points are AMDGPU NBIO initialization and service code, PCIe root-complex handling, display code paths that need NBIO offsets for DCN resource setup, RAS/AER diagnostics, hotplug/PME and interrupt routing, FLR/GPU reset recovery, virtualization/PF mailbox paths, BME and DMA attribute policy, and power-management/link-management code. The endpoint/downstream/RCC blocks tie software-visible PCIe controls to root-complex controller hardware rather than to ordinary Linux PCI core data structures alone.

## Risks And Edge Cases

- Generated offset drift can compile successfully while sending reads or writes to the wrong register, causing PCIe enumeration failures, broken link training, missed error status, false interrupts, or reset/hotplug regressions.
- This chunk begins mid-address-block. The dev0 RC0 identity, command/status, BAR, and early bridge registers are in the prior chunk; final per-file research must merge both ranges before treating dev0 RC0 coverage as complete.
- This chunk also ends mid-`bif_misc` block at `regBIFC_HSTARB_CNTL`; later BIF misc controls are outside this research item.
- Many offsets deliberately alias the same dword for adjacent PCI config fields, such as control/status halves or MSI/DPA subfields. Callers must use the correct companion bit masks and preserve unrelated fields during read-modify-write operations.
- The dev0/dev1/dev2 and endpoint/downstream blocks are highly patterned. A single generated mismatch in one device or lane can produce topology-specific failures that do not reproduce on simpler configurations.
- Strap and reset/FLR registers can alter persistent hardware policy or reset active devices. Writes must be sequenced with firmware ownership, quiescing, and restore expectations.
- AER, BME, interrupt, PME, LTR, and DMA attribute registers can affect error visibility and transaction ordering. Incorrect programming can hide fatal errors, generate interrupt storms, or change DMA behavior.
- Lane equalization and margining controls are link-training sensitive. Diagnostic writes should be bounded, restore reserved bits, and account for active traffic and retrain requirements.

## Test Signals

- Build AMDGPU with NBIO 7.2.0 support enabled; compile coverage catches removed or renamed generated symbols used by `nbio_v7_2.c`, DCN resource code, and other consumers.
- Run generated-header consistency checks: each register macro in the chunk should have exactly one `_BASE_IDX` companion, base-index values should match the NBIO 7.2.0 address map, and patterned dev/lane/function blocks should be internally aligned.
- Cross-check offsets against NBIO 7.2.0 shift/mask/default headers and the hardware register database, especially aliased PCI config dwords, DPA substate registers, AER log/status registers, and repeated RCC endpoint/downstream blocks.
- On supported hardware, validate PCIe enumeration, bridge aperture setup, link speed/width reporting, link retrain/equalization, lane-margining diagnostics, MSI/PME behavior, AER logging, and hotplug or reset recovery.
- Exercise suspend/resume and GPU reset/FLR paths while tracing RCC strap-derived settings, endpoint/downstream controls, BME logs, and interrupt status to confirm state is restored or intentionally reinitialized.
- For virtualization or multi-function configurations, validate PF mailbox/shadow/trap paths, BME status, DMA attribute overrides per device/function, requester ID programming, and LTR message handling.
