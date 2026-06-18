# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h lines 4990-7548

## Purpose

This chunk is a generated AMD NBIO 4.3.0 register-offset header segment. It has no executable code; it exports C preprocessor constants that map NBIO/PCIe/NBIF register names to numeric hardware offsets. The chunk is hardware metadata used by AMDGPU code together with `nbio_4_3_0_sh_mask.h` and SOC15 register-access helpers.

The assigned range starts inside the `nbio_nbif0_bif_cfg_dev0_epf0_vf11_bifcfgdecp` PCI configuration-space block at the tail of VF11's standard header and capability offsets. It then covers complete config-space offset blocks for `VF12` through `VF15`, full per-VF BIF/RCC decode windows for `VF0` through `VF15`, PCIe link/controller register windows, the root/endpoint direct configuration-space register views, and the beginning of the direct `VF0` configuration-space register view. The range ends at `regBIF_CFG_DEV0_EPF0_VF0_DEVICE_CNTL`; the rest of direct VF0 and later VFs continue after this chunk.

## Exported API Surface

The only API surface is macro definitions:

- `cfgBIF_CFG_DEV0_EPF0_VF<n>_0_*` constants are byte-addressed PCI configuration-space offsets for SR-IOV-style virtual functions under device 0, endpoint function 0.
- `cfgBIF_BX_DEV0_EPF0_VF<n>_*` constants are per-VF BIF decode-window addresses for BME status, atomic-error logging, doorbell self-ring apertures, HDP coherency flush controls, transaction-pending status, address-LUT bypass, and mailbox registers.
- `cfgRCC_DEV0_EPF0_VF<n>_*` constants are per-VF RCC decode-window addresses for error logging, doorbell aperture enablement, memory-size reporting, IOV function identity, and GFX MSI-X vector table/PBA registers.
- `reg*` constants are SOC15-style register indices. Each one is paired with a `*_BASE_IDX` macro, and callers must preserve that base-index association when resolving a physical MMIO address.

There are no functions, structs, enums, callbacks, globals, storage declarations, or inline helpers in this source range.

## Register Groups Covered

The opening lines complete VF11 config-space offsets from `BASE_ADDR_5` through `PCIE_ARI_CNTL`. Complete `cfgBIF_CFG_DEV0_EPF0_VF12_0_*`, `VF13_0_*`, `VF14_0_*`, and `VF15_0_*` blocks follow. Each full VF block repeats the standard PCI header, BARs, adapter/ROM/capability pointer, PCIe device/link capability and control registers, MSI/MSI-X capability registers, vendor-specific enhanced capability, AER status/mask/severity/header/TLP-prefix logs, and ARI enhanced capability/control offsets. These high-address `0xfffe1030c000` through `0xfffe1030f000` values are the config-address view, not the later direct `reg...` register-index view.

For `VF0` through `VF15`, the chunk defines four generated decode groups per VF:

- `BIFPFVFDEC1` BIF registers at bases `0xd0000000`, `0xd0080000`, and so on, advancing by `0x80000` per VF. These include `BIF_BME_STATUS`, `BIF_ATOMIC_ERR_LOG`, doorbell self-ring GPA aperture base/control, HDP register/memory coherency flush controls, flush-only/invalidate-only controls, `GPU_HDP_FLUSH_REQ`, `GPU_HDP_FLUSH_DONE`, `BIF_TRANS_PENDING`, `NBIF_GFX_ADDR_LUT_BYPASS`, four transmit mailbox dwords, four receive mailbox dwords, mailbox control/interrupt control, and `BIF_VMHV_MAILBOX`.
- `SYSPFVFDEC` registers exposing `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI` for per-VF indirect MMIO access.
- RCC `BIFPFVFDEC1` registers exposing `RCC_ERR_LOG`, `RCC_DOORBELL_APER_EN`, `RCC_CONFIG_MEMSIZE`, `RCC_CONFIG_RESERVED`, and `RCC_IOV_FUNC_IDENTIFIER`.
- RCC `BIFDEC2` GFX MSI-X windows exposing four vector entries (`ADDR_LO`, `ADDR_HI`, `MSG_DATA`, `CONTROL`) and a pending-bit array register.

The PCIe controller portions begin at `nbio_pcie0_pswusp0_pciedir_p` and `nbio_pcie0_pciedir`. They cover port/controller scratch and control registers, requester ID, lane status, error controls and injection registers, RX/TX credit accounting, NAK counters, link-control and link-training controls, link state/status registers, L1 PM substates, fine-grain clock-gating overrides, equalization coefficient controls, replay/sequence/ack-latency controls, flow-control registers, common AER masking, I2C expand/data registers, PCIe configuration control, performance counters, and additional PHY/link management surfaces.

`nbio_pcie0_pswuscfg0_cfgdecp` defines a small bridge-style config-space block beginning at base `0x1a300000`, including `cfgPSWUSCFG0_0_VENDOR_ID`, command/status/class/header/BIST fields, and `IRQ_BRIDGE_CNTL`. `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` maps the root-complex direct `regIRQ_BRIDGE_CNTL` register at base `0x10100000`.

The `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` block is the direct SOC15 register-index view of EPF0 PCI configuration space at base `0x10140000`. It starts at `regBIF_CFG_DEV0_EPF0_VENDOR_ID` index `0x10000` and reaches through PCIe 32 GT/s link capability/control/status registers. It includes endpoint identity, BARs, PM capability, PCIe device/link capability and control, MSI/MSI-X, vendor-specific and virtual-channel capabilities, device serial number, AER logs, BAR enhanced capability, power budget, DPA, secondary PCIe, per-lane equalization, ACS, ATS, PRI, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, data-link feature, 16 GT/s and 32 GT/s link registers, lane margining, and VF resize BAR capability/control registers. Packed PCI fields intentionally share register indices, for example vendor/device IDs at `0x10000`, command/status at `0x10001`, and control/status halves in several capability registers.

The final block starts direct `regBIF_CFG_DEV0_EPF0_VF0_*` configuration-space registers at base `0x10160000`, from `VENDOR_ID` through `DEVICE_CNTL`. It is only a prefix of the direct VF0 block; subsequent VF0 status/link/MSI/MSI-X/AER/ARI offsets are outside this work item.

## Control Flow

There is no local control flow. Runtime control flow lives in AMDGPU callers:

1. The device's NBIO implementation selects this generated header for NBIO 4.3.0 hardware.
2. Driver code names a `cfg...` or `reg...` macro for the desired PCIe/NBIO register.
3. SOC15 helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_FIELD15_PREREG` combine the register index with the matching `*_BASE_IDX` and hardware instance.
4. Field-safe updates then use masks/shifts from `nbio_4_3_0_sh_mask.h`, commonly via `REG_SET_FIELD` and `REG_GET_FIELD`.

The `cfg...` constants and `reg...` constants are related but not interchangeable. `cfg...` names are config-space style byte addresses or decode-window addresses, while `reg...` names are register indices used by the SOC15 MMIO framework.

## State and Persistence Behavior

The header itself has no state and persists nothing. It names hardware state stored in the GPU/NBIO register file and PCI configuration surfaces. Writes through these offsets persist only until reset, FLR, power-state transition, firmware ownership changes, SR-IOV VF reset, or explicit driver/hypervisor writes.

Important state represented in this chunk includes VF PCI identity/capability presentation, BARs, MSI/MSI-X programming, AER status and log registers, ARI/ATS-related capability surfaces, per-VF doorbell aperture state, HDP coherency flush request/done state, BIF transaction-pending state, VF mailbox contents/control, RCC memory-size and IOV function identity, PCIe link training/equalization/margining state, ASPM/LTR-related link control, SR-IOV capability/control registers in the EPF0 direct view, and 16 GT/s/32 GT/s link capability registers.

## Dependencies and Integration Points

The direct include users in this tree are `amdgpu/nbio_v4_3.c`, the SMU 13.0.0 and 13.0.7 PPT files, and DCN32/DCN321 resource files. The most concrete runtime integration is `amdgpu/nbio_v4_3.c`, which includes both `nbio_4_3_0_offset.h` and `nbio_4_3_0_sh_mask.h`.

Relevant `nbio_v4_3.c` uses tied to this chunk include:

- `nbio_v4_3_set_reg_remap()` uses `regBIF_BX_DEV0_EPF0_VF0_HDP_MEM_COHERENCY_FLUSH_CNTL` with `SOC15_REG_OFFSET(...) << 2` for the SR-IOV/VF-oriented HDP flush remap path.
- `nbio_v4_3_remap_hdp_registers()` programs remap registers so KFD-visible HDP flush offsets point at the selected NBIO flush controls.
- `nbio_v4_3_program_ltr()` and `nbio_v4_3_program_aspm()` read/write `regBIF_CFG_DEV0_EPF0_DEVICE_CNTL2`, `regBIF_CFG_DEV0_EPF0_PCIE_LTR_CAP`, `regPSWUSP0_PCIE_LC_CNTL2`, `regPCIE_LC_CNTL*`, and related strap/link-control registers, using masks from the sibling sh/mask header.
- Doorbell setup code uses NBIO/RCC/S2A doorbell registers from the same generated offset family to route IH, SDMA, VCN, GC, and self-ring doorbells.
- RAS interrupt handling uses BIF doorbell interrupt control registers in the broader file to enable, clear, and process ATHUB error events.

The SMU and DC resource includes are broader integration points: they bring the same NBIO register constants into power-management and display-resource compilation units so generated register-list and platform code can resolve NBIO 4.3.0 symbols.

## Risks and Maintenance Notes

The main risk is silent hardware misaddressing. These macros encode a hardware ABI; a stale generated value, wrong IP-version include, wrong VF number, or wrong base index can compile cleanly while driving a different register.

The chunk has several intentional overlaps. PCI config-space fields smaller than 32 bits share direct register indices, and MSI layouts overlap depending on 32-bit versus 64-bit MSI format. Consumers must use the matching mask/shift definitions and access width assumptions rather than treating every macro name as a distinct DWORD.

The per-VF decode windows are repetitive and easy to misuse. BIF/RCC bases advance by `0x80000` per VF in this range, while the RCC GFX MSI-X table window for each VF is offset into a neighboring `BIFDEC2` range. Copying a VF0 macro where a VF-specific macro is required can affect the wrong function's doorbell, HDP flush, mailbox, or MSI-X state.

The `cfg...` high-address view, per-VF BIF/RCC decode windows, and direct `reg...` SOC15 config views represent different access paths. Code must not substitute `cfgBIF_CFG_DEV0_EPF0_VF12_0_DEVICE_CNTL` for `regBIF_CFG_DEV0_EPF0_DEVICE_CNTL` or vice versa; the prefixes indicate different addressing domains.

This work item has artificial boundaries. It starts in the middle of the VF11 config block and ends in the early direct VF0 block. The final per-file report should reconcile adjacent chunks before making complete statements about VF11 or direct VF0 coverage.

## Test Signals

There are no unit-testable functions in the header. Useful validation signals are build and hardware integration checks:

- Kernel build coverage for `amdgpu/nbio_v4_3.c`, SMU 13 PPT files, and DCN32/DCN321 resource files confirms referenced generated symbols and `_BASE_IDX` macros still resolve.
- NBIO 4.3.0 probe should read revision and memory-size registers correctly, program HDP flush remaps, and avoid hangs in `RREG32_SOC15`/`WREG32_SOC15` accesses using these offsets.
- SR-IOV/VF tests should verify VF enumeration, VF BARs, MSI/MSI-X programming, AER visibility, ARI capability behavior, VF mailbox communication, and VF doorbell aperture routing.
- KFD/graphics workloads should validate HDP coherency flush request/done behavior after `regBIF_BX_DEV0_EPF0_VF0_HDP_MEM_COHERENCY_FLUSH_CNTL` is used as the remap target.
- PCIe power-management tests should exercise ASPM/LTR programming, link-state transitions, 16 GT/s and 32 GT/s capability reporting, lane equalization, and lane margining status without AER regressions.
- Error-injection or stress tests should watch AER status/log registers, BIF transaction-pending state, mailbox interrupt status, and doorbell interrupt clear/status paths for stuck bits or misrouted interrupts.
