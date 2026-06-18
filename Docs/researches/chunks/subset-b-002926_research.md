# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 54196-56612

## Scope

This chunk is a generated AMDGPU NBIO 2.3 register field shift/mask header slice. It contains preprocessor constants only: no functions, structs, variables, locking, allocation, persistence code, or executable control flow.

The assigned range starts in the mask half of `PCIE_LC_CNTL5`, then covers PCIe link-controller equalization, link management, straps, L1 PM substates, save/restore, the `nbio_pcie0_pciedir` address block, PRBS diagnostics, software reset controls, clock/power-management controls, receive margining, presence-detect/debug controls, and the beginning of the `nbio_nbif0_bif_cfg_dev0_swds_bifcfgdecp` PCI configuration block. It ends inside `BIF_CFG_DEV0_SWDS0_LINK_CNTL`, before that register's later shift and mask definitions in the following chunk.

Although this path is under a local `ceph-client` source mirror, this file is AMD GPU NBIO/PCIe hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header section is to publish the bit layout contract for NBIO 2.3 PCIe and BIF configuration registers. Each hardware field is represented as one or both of:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for encoding or extracting a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask for isolating, clearing, or preserving that field.

AMDGPU code combines these constants with register addresses from companion offset headers and with register helpers such as `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_OFFSET`. The header names field positions only; it does not describe access ordering or side effects.

## Important Macro Families

The opening `PCIE_LC_*` portion describes link-controller policy and equalization controls. It includes local equalization presets and coefficients, forced 8 GT/s and 16 GT/s pre/cursor/post-cursor coefficients, best equalization settings and FOM reporting, equalization request coefficients, SRIS/SRNS mode and autodetect controls, EIEOS handling, L1/L0s standby behavior, RX recovery timeout, scheduled RX equalization, ESM/PLL state bits, link management enablement, bandwidth hints, link speed/width updates, and link power state tracking.

The strap and low-power link-controller groups include `PCIEP_STRAP_LC`, `PSWUSP0_PCIEP_STRAP_MISC`, `PCIEP_STRAP_LC2`, `PCIE_LC_L1_PM_SUBSTATE`, `PCIE_LC_L1_PM_SUBSTATE2`, `PCIE_LC_PORT_ORDER`, and `PCIEP_BCH_ECC_CNTL`. These constants describe hardware strap-derived link behavior, PLL lane enables, ASPM/L1.1/L1.2 timeout and enable bits, port ordering, and BCH/ECC control/status.

`PCIE_LC_CNTL8` through `PCIE_LC_CNTL12` and `PCIE_LC_SAVE_RESTORE_1/2` provide later-generation link policy fields: SKP/OS generation controls, lane reversal, receiver-detect behavior, forced coefficient extensions, clock gating overrides, SRIS/RX training behavior, extended sync and EIEOS rules, receive margining mode, lane-marginal status, save/restore state selection and enablement, and OBFF-related bits.

The `nbio_pcie0_pciedir` block exposes internal PCIe directory/MMIO fields. It covers scratch/reserved registers, RX NAK counters, top-level PCIe control/config/debug, TX tracking address and status, bandwidth-by-unit ID, RX/TX/CI/bus control, LC state/status snapshots, TX status and write-posted-request controls, last received/transmitted TLP dwords, I2C register access expansion/data, configuration controls, link power-management control, port-order control, protocol buffer/decoder/misc status, RX AD controls, sideband protocol controls, and performance counter controls for TXCLK and SCLK domains.

Diagnostic and low-level test families in this chunk include `PCIE_PRBS_*` registers for PRBS clear/status/free-run/user-pattern/bit-count/error-count state across lanes 0-15, `PCIE_HIP_REG*` implementation-specific HIP fields, and `PCIE_STRAP_*` strap capture fields. These are primarily bring-up, lab, validation, or low-level debug surfaces rather than normal display/graphics data paths.

The reset and power-management groups include `SWRST_COMMAND_STATUS`, `SWRST_GENERAL_CONTROL`, `SWRST_COMMAND_0/1`, `SWRST_CONTROL_0` through `_6`, `SWRST_EP_COMMAND_0`, `SWRST_EP_CONTROL_0`, `CPM_CONTROL`, `CPM_SPLIT_CONTROL`, `LC_CPM_CONTROL_0/1`, `PCIE_PGMST_CNTL`, and `PCIE_PGSLV_CNTL`. These constants describe command/status bits, reset selection, BIF/port/PHY/PCS/AXI/CPM/reset-domain controls, endpoint reset bits, clock power management enables, timers, gating allows, and master/slave power-gating controls.

The final PCI config-space portion begins `addressBlock: nbio_nbif0_bif_cfg_dev0_swds_bifcfgdecp` and defines standard bridge/downstream-device fields for `BIF_CFG_DEV0_SWDS0_*`: vendor and device IDs, command/status, revision and class code, cache-line/latency/header/BIST, BARs, bus numbering, I/O and memory base/limit registers, bridge secondary status, prefetchable limits, capability pointers, ROM base, interrupt line/pin, bridge control, power-management capability/status-control, PCIe capability, device capability/control/status, link capability, and the first shift definitions for link control.

## Control Flow

There is no runtime control flow in this header. The practical runtime sequence is supplied by consumers:

1. Select a register address from the matching NBIO offset metadata or from a locally defined SMN address.
2. Read a register value through the AMDGPU PCIe/SOC register accessors.
3. Decode or modify fields using these `__SHIFT` and `_MASK` constants, directly or through helper macros.
4. Write the value back, poll status bits, or clear sticky status according to the hardware programming sequence.

One direct consumer is `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which defines `smnPCIE_LC_CNTL6`, reads it with `RREG32_PCIE`, sets `PCIE_LC_CNTL6__LC_L1_POWERDOWN_MASK` and `PCIE_LC_CNTL6__LC_RX_L0S_STANDBY_EN_MASK`, and programs `PCIE_LC_CNTL6__LC_SPC_MODE_8GT` by clearing the mask and shifting a new value into place. Other control flows for PRBS, reset, CPM, performance counters, straps, and bridge config are similarly outside this file.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware state held in GPU registers, PCI configuration space, strap capture registers, and firmware/hardware-managed status fields.

The represented state includes link training/equalization coefficients, selected link speed/width and power states, L1 substate timers and enables, link-management event masks and status, strap values, last TLP debug snapshots, PRBS counters and error counters, performance counter configuration/results, reset command/status bits, CPM and clock gating settings, receive margining settings, bridge command/status bits, bus/window configuration, BAR/ROM values, power-management capability/status, and PCIe device/link capability/control/status fields.

Some fields are normal driver-programmed controls, some are strap/capability readouts, some are hardware-updated status, and some may be command or sticky clear-on-write bits. The generated macro names do not encode read/write permissions, volatility, reset domain, or clear semantics.

## Dependencies And Integration Points

The direct dependency is the generated NBIO 2.3 register database. This shift/mask file must remain synchronized with sibling address/default headers under `drivers/gpu/drm/amd/include/asic_reg/nbio/`; for example `nbio_2_3_offset.h` provides `cfgBIF_CFG_DEV0_SWDS0_LINK_CNTL` at offset `0x0068`, while this chunk provides the early field positions for that register.

Primary integration is with AMDGPU NBIO, PCIe link-management, power-management, reset, diagnostics, SRIS/SRNS, PRBS validation, clock-gating, and PCI configuration paths. The same macro names also appear across later NBIO generations, so code in files such as `amdgpu/nbio_v2_3.c`, `amdgpu/nbio_v6_1.c`, and `amdgpu/nbio_v7_4.c` can share field-level programming patterns where the ASIC layout is compatible.

The bridge-style `BIF_CFG_DEV0_SWDS0_*` definitions integrate with PCI enumeration and configuration surfaces. Consumers rely on these constants when decoding or programming command/status bits, bus numbers, bridge windows, power-management state, PCIe device controls, link capabilities, link retraining, common clock configuration, and ASPM-related controls.

## Risks And Edge Cases

- The chunk boundaries are partial. The first line begins after several `PCIE_LC_CNTL5` shifts and masks already appeared, and the last line stops before `BIF_CFG_DEV0_SWDS0_LINK_CNTL` is complete. Adjacent chunks are required for whole-register conclusions.
- These macros are untyped constants. A missing or renamed macro is likely to fail at build time, but an incorrect shift or mask can compile cleanly and program an adjacent hardware field.
- Link training and equalization fields are interoperability-sensitive. Bad coefficient, SRIS, EIEOS, RX recovery, scheduled RXEQ, ESM, or SPC-mode masks can cause link training failures, bandwidth regressions, resume instability, or marginal signal integrity.
- Power-management fields are liveness-sensitive. Incorrect L1/L1.1/L1.2, standby, CPM, clock-gating, or link power-state fields can produce hangs, failed wakeups, high idle power, or missed bandwidth transitions.
- Reset command/control bits can affect wide hardware domains, including ports, BIF, PHY, PCS, AXI, endpoint config, and clock/reset fabric. Ordinary read-modify-write treatment is risky if bits are command strobes or self-clearing status.
- Diagnostic fields such as PRBS counters, last TLP snapshots, performance counters, and debug/status fields may be volatile. Polling or clearing them without following hardware sequencing can lose evidence or disturb validation flows.
- PCI bridge configuration fields mix 8-bit, 16-bit, and 32-bit PCI config semantics. Wrong access width or offset pairing can corrupt neighboring command/status, bus numbering, window, interrupt, or capability fields.
- Several field names contain repeated `MASK` tokens, such as `PCIE_LINK_MANAGEMENT_MASK__..._MASK_MASK`, because the hardware register itself is a mask register. Tooling and human review should distinguish the register name from the C macro's field-mask suffix.

## Test Signals

Useful validation is mostly build, boot, and hardware-integration oriented:

- Build AMDGPU with NBIO 2.3 support enabled; drift in names used by `nbio_v2_3.c` should surface as compile failures around `PCIE_LC_CNTL6` and related masks.
- Run generated-header consistency checks against the NBIO 2.3 source database and sibling offset headers, including shift/mask pair coverage, non-overlap, field-width, and register-boundary checks.
- Boot affected ASICs and confirm stable PCI enumeration, bridge windows, BAR/ROM values, bus numbers, class codes, capability-list traversal, and PCIe link capability/control/status reporting.
- Exercise PCIe link transitions: Gen speed changes, width changes, retraining, ASPM/L1 substates, SRIS/SRNS paths, equalization, EIEOS handling, suspend/resume, runtime power management, and bandwidth-hint flows.
- Validate reset paths that touch NBIO/BIF/port/PHY/PCS/endpoint domains; unexpected hangs, stuck reset status, or failed re-enumeration point to field-layout or sequencing issues.
- Use PRBS, performance counter, last-TLP, and RX margining diagnostics during bring-up or lab validation; lane-specific error-counter mismatches and impossible counter values are strong signals of bad masks or offsets.
- Monitor power and wake behavior under clock gating, CPM, L1 PM substates, and standby settings; regressions include elevated idle power, missed wakeups, link flaps, or display/compute workload stalls.

## Chunk-Specific Notes For Merge

Merge this with adjacent chunks before producing final file-level research for `nbio_2_3_sh_mask.h`. Preserve that this slice transitions from late link-controller definitions into the `nbio_pcie0_pciedir` MMIO block and then into the beginning of the downstream/bridge PCI config decoder block, ending mid-`BIF_CFG_DEV0_SWDS0_LINK_CNTL`.
