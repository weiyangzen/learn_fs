# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 118383-120812

## Purpose

This chunk is a generated AMD NBIO 7.7 shift/mask header slice for register fields in several NBIO, BIF, GDC, northbridge configuration, and PCIe root-port blocks. It starts just after the `RCC_DEV0_3_RCC_BUS_CNTL` field list, covers the `RCC_DEV0_2` and `RCC_DEV0_3` register-control/configuration surface, then moves through `nbio_nbif0_bif_bx_BIFDEC1`, `nbio_nbif0_bif_bx_pf_BIFPFVFDEC1`, `nbio_nbif0_gdc_GDCDEC`, `nbio_nbif0_rcc_dev0_epf0_BIFDEC2`, `nbio_iohub_nb_nbcfg_nb_cfgdec`, and the beginning-to-middle of `nbio_pcie0_bifplr0_cfgdecp`.

The file does not contain executable driver code. Its purpose is to expose C preprocessor constants that AMDGPU code can use to extract, set, or test bitfields in NBIO 7.7 registers. The companion offset/default generated headers provide register addresses and reset values; this `_sh_mask` header provides the bit layout.

## Public Surface In This Chunk

The exported API is entirely macro based:

- `REGISTER__FIELD__SHIFT` gives the bit offset for a field.
- `REGISTER__FIELD_MASK` gives the raw register mask for that field.

The first `RCC_DEV0_2` and `RCC_DEV0_3` groups describe VGA/config aperture controls, XDMA bounds, miscellaneous PCIe feature controls, bus-number and dev/function capture/list registers, peer frame-buffer offsets, link entry/exit controls, LTR latency, endpoint requester ID restore, and memory-hub arbitration. These are low-level root-complex/configuration controls used by NBIO setup and virtualization paths.

The `BIF_BX2` block is broad. It includes MM indirect access gating, bus coherency and traffic-class controls, scratch registers, reset/link-training controls, interrupt behavior, CLKREQB pad control, feature-control bits, doorbell control and interrupt state/clear/disable bits, FB read/write enablement, RAS interrupt vector selection, per-VF pending/status/enable masks for register-write, doorbell, and frame-buffer access, HDP remap flush addresses, a BIF ring-buffer control/address/pointer surface, mailbox index, GPUIOV config sizes, and several pad-control registers.

The `BIF_BX_PF2` block exposes physical-function-facing status/control fields: BME-low DMA detection and clear, unsupported atomic-operation error logs and clears, self-ring doorbell GPA aperture base/control fields, HDP coherency flush/invalidate controls, per-engine GPU HDP flush-only/invalidate-only/flush request and done bitmaps, BIF transaction-pending status, GFX address LUT bypass, four transmit and four receive mailbox dwords, mailbox control/interrupt fields, and VMHV mailbox fields.

The `GDC1` block covers NBIF/GDC clock and power-management controls, doorbell range programming for SDMA, IH, VCN, RLC, and CSDMA clients, ATDMA arbitration weights, doorbell fence enablement, S2A miscellaneous doorbell/arbiter settings, early wakeup behavior, and NGDC power-gating master/slave controls.

The `RCC_DEV0_EPF0_1_GFXMSIX` block defines a compact MSI-X table/PBA view for four graphics MSI-X vectors: message address low/high, message data, per-vector mask bit, and pending bits 0-3.

The `NB_NBCFG1` block defines northbridge-style PCI configuration identity and command/status fields: vendor/device IDs, I/O/memory/bus-master enables, capability-list and abort status, revision ID, cache-line and latency registers, header type/device type, subsystem IDs, and scratch register.

The `BIFPLR0_2` block starts a PCIe root-port configuration-space layout. It covers conventional PCI/bridge header fields; command/status; revision, class, cache, latency, header, and BIST bytes; primary/secondary/subordinate bus numbering; I/O, memory, and prefetchable windows; capability pointer; interrupt line/pin; bridge control; PM capability and status/control; PCIe capability, device, link, slot, and root controls/status; PCIe capability 2 device/link/slot fields; MSI and MSI-map fields; SSID and vendor-specific enhanced capability fields; virtual-channel capability/control/status and VC0/VC1 resources; device serial number; AER enhanced capability list; and the uncorrectable error status plus the beginning of the uncorrectable error mask register.

## Important Register Families

The RCC register families describe how the device participates in PCIe configuration and peer addressing. The config aperture registers (`RCC_CONFIG_F0_BASE`, `RCC_CONFIG_APER_SIZE`, `RCC_CONFIG_REG_APER_SIZE`) and XDMA/peer FB offsets define address decoding windows. Bus-number and dev/function lists are relevant to requester-ID matching, host-bus capture, virtualization, and peer routing. The feature-control fields include UR handling for ATC/PASID and page-request traffic, MSI/MSI-X pending behavior, ECRC-related device-error behavior, and poisoned payload handling.

The BIF bus, doorbell, interrupt, and ring-buffer fields are central to host-to-GPU command submission plumbing. Doorbell controls decide whether translated or untranslated doorbells are allowed, whether self-ring behavior is disabled, whether monitor interrupts are generated, and how doorbell/RAS/ATHUB interrupt status is cleared or disabled. The ring-buffer fields describe enablement, size, write-pointer writeback, overflow handling, reset-on-FLR behavior, base address, read/write pointer offsets, and writeback address programming.

The VF mask/status families are repeated 31-bit maps for virtual functions. `BIF_BX2_VF_REGWR_EN`, `BIF_BX2_VF_DOORBELL_EN`, and `BIF_BX2_VF_FB_EN` grant or mask VF register write, doorbell, and framebuffer access; the corresponding status registers report which VFs are active or pending in those areas. Their per-VF repetition makes them easy to misuse if the VF index-to-bit mapping is generated incorrectly.

The PF2 HDP coherency registers provide request/done bitmaps for CP0-CP9, SDMA0/1, and reserved engine slots. Separate flush-only, invalidate-only, and full flush request registers reflect different cache-coherency operations. The matching done bits are synchronization signals for code that must wait for host data path coherency before exposing results to the CPU or GPU engines.

The GDC doorbell and fence registers define per-client doorbell offset/size windows and fence enablement for CP, SDMA0-5, RLC, VCN0/1, IH, and CSDMA. These fields integrate NBIO doorbell routing with engine-specific queue submission, interrupt, and scheduling paths. GDC power-management fields control clock gating, power-gating hysteresis, deep-sleep allowance, early wakeup, and wake-on-AER behavior.

The `BIFPLR0_2` PCIe root-port fields mirror standard PCI/PCIe configuration-space concepts. Command/status and bridge windows decide whether memory, I/O, and bus mastering are enabled and which downstream address ranges are decoded. PM fields cover PME support, current power state, PME enable/status, and bridge extension support. PCIe device/link/slot/root fields include payload and read-request sizing, relaxed/no-snoop ordering, error-reporting enables, FLR, link speed/width, ASPM, retrain/link disable/common-clock controls, slot power/hotplug/MRL/attention/presence state, and root PME/error signaling. Device/link/slot capability 2 fields add completion timeout, AtomicOp, LTR, OBFF, IDO, EETLP, emergency power reduction, target link speed, compliance/de-emphasis/transmit-margin controls, and DRS-related status/control.

The VC and AER families are safety-critical PCIe feature surfaces. VC fields control traffic-class to virtual-channel mapping, arbitration table load/select, VC IDs, VC enablement, and negotiation-pending status. AER uncorrectable status/mask fields include data-link protocol, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. The chunk ends before the uncorrectable error mask register is complete; adjacent chunks are needed for the rest of AER.

## Control Flow And State

There is no runtime control flow in this header. Use is compile-time substitution:

1. An AMDGPU translation unit includes `nbio_7_7_0_sh_mask.h`.
2. Driver code selects a register address from a matching offset header such as `nbio_7_7_0_offset.h`.
3. Register helper code reads or prepares a raw register value.
4. The caller applies the `*_MASK` and `*_SHIFT` constants to decode or compose one field.

The header itself stores no C state and has no persistence layer. The persistent or semi-persistent state is in hardware registers: PCI configuration registers, bridge aperture registers, MSI-X/MSI state, doorbell ranges, VF access maps, mailbox dwords, HDP coherency request/done bits, interrupt status/clear/disable bits, power-gating controls, and AER status/mask fields. Some of these are configuration state that survives until reset or reprogramming; others are live status bits, clear-on-write controls, request/done handshakes, or hardware-owned status surfaces.

## Dependencies And Integration Points

This chunk depends on the AMD generated register-header convention. The `_sh_mask` file provides bitfields; matching generated offset headers provide register addresses; default headers, where present, provide reset/default values. Correct use also depends on AMDGPU register access helpers that understand the target register aperture, index space, and any indirect access requirements.

The direct in-tree integration point for this NBIO generation is AMDGPU NBIO 7.7 support, including files that include `asic_reg/nbio/nbio_7_7_0_sh_mask.h`. Functional consumers span PCIe setup, reset, interrupt handling, RAS/error handling, SR-IOV/GPUIOV, doorbell setup, HDP flush synchronization, mailbox communication, power management, and debug register dumping.

Semantic dependencies come from both AMD hardware specifications and standard PCI/PCIe behavior. Standard families include PCI command/status, bridge windows, PM capability, MSI/MSI-X, PCIe capability, VC, and AER. AMD-specific families include NBIO RCC controls, BIF doorbell/ring-buffer and VF access maps, GDC doorbell/power controls, HDP flush/invalidate request protocols, GPUIOV config sizing, VMHV mailbox fields, and ESM/vendor-specific behavior exposed in adjacent chunks.

## Risks And Maintenance Notes

- The file is generated and repetitive. A one-bit shift or mask drift can silently target the wrong hardware bit, especially in per-VF and per-engine bitmap families.
- This chunk starts immediately after a `RCC_DEV0_3_RCC_BUS_CNTL` field from the previous slice and ends mid-register inside `BIFPLR0_2_PCIE_UNCORR_ERR_MASK`; cross-chunk reconciliation is required for full per-file coverage.
- Status, clear, and request/done registers are not interchangeable. Macros only describe bit layout; they do not encode write-one-to-clear behavior, posted-write ordering, polling requirements, or read side effects.
- Doorbell, VF enable, and GPUIOV fields can affect isolation between physical and virtual functions. Incorrect masks can expose MMIO, doorbell, or framebuffer access to the wrong VF.
- HDP flush/invalidate fields are synchronization primitives. Dropping a request bit, polling the wrong done bit, or confusing flush-only with invalidate-only can produce stale CPU/GPU views of memory.
- PCIe command, bridge window, VC, link, slot, root, and AER controls can affect memory decoding, interrupt routing, error containment, power state, and link stability.
- Full-width masks such as `0xFFFFFFFFL` and high-bit masks such as `0x80000000L` should stay within the established AMDGPU unsigned register-value paths to avoid signedness or truncation problems.
- Many fields are hardware-version-specific. Nearby NBIO generations can have similar names with different offsets, widths, or feature presence.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for AMDGPU files that include the NBIO 7.7 generated headers.
- Static checks that every `*_SHIFT` macro has the expected matching `*_MASK`, masks align with shifts, and repeated VF/engine fields maintain monotonic bit positions.
- Cross-header checks that every register family named here has matching NBIO 7.7 offset definitions in the corresponding offset header.
- Runtime register dumps on NBIO 7.7 hardware comparing decoded PCI/NB identity, command/status, bridge windows, PM/PCIe capability fields, MSI/MSI-X state, VC resources, and AER status/masks with `lspci -vvxxx` and AMDGPU debug output.
- SR-IOV or GPUIOV tests that toggle VF register-write, doorbell, and framebuffer access and verify that the intended VF bits change without affecting adjacent VFs.
- Doorbell submission tests across CP, SDMA, RLC, VCN, IH, and CSDMA paths, including doorbell range/fence programming and interrupt status/clear behavior.
- HDP coherency tests that issue CP/SDMA flush, invalidate, and flush-only requests and verify matching done bits before CPU-visible or GPU-visible data is consumed.
- Error-path tests that exercise BME-low detection, atomic unsupported-request logging, AER uncorrectable status/mask handling, and RAS/ATHUB/doorbell interrupt masking and clearing.
- Power-management tests around CLKREQB pad control, NGDC early wakeup, deep-sleep allowance, power-gating hysteresis, D3-only behavior, PME, and link-state transitions.
