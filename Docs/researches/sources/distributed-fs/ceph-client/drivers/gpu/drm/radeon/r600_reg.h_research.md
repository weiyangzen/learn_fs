# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600_reg.h

## Purpose

`r600_reg.h` is a compact register-definition header for R600/R700 Radeon code. It names PCIe, RCU, UVD context, memory-controller aperture, RAM configuration, power-management GPIO, display swap, HDP, bus/configuration, ROM, SPLL, BIOS scratch, audio, and HDMI offset registers plus selected masks/shifts/bit values.

## Important APIs, Types, and Functions

This file declares macros rather than functions or types. Important groups include:

- Indexed register ports: `R600_PCIE_PORT_INDEX/DATA`, `R600_RCU_INDEX/DATA`, and `R600_UVD_CTX_INDEX/DATA`.
- Memory-controller aperture registers and masks for R600 and R700, including FB location, AGP top/bottom/base, system aperture low/high/default, and logical page masks.
- Display and memory configuration bits such as `R600_RAMCFG`, channel-size bits, `R600_D1GRPH_SWAP_CONTROL`, endian swap selectors, and channel crossbar selectors.
- Power and GPIO registers such as `R600_GENERAL_PWRMGT`, `R600_OPEN_DRAIN_PADS`, `R600_LOWER_GPIO_ENABLE`, and voltage GPIO control registers.
- Bus, config, blackout, ROM, SPLL, and BIOS scratch registers.
- Audio register addresses for HDA-like capabilities and current stream status.
- HDMI instance offsets for DCE2 and DCE3.2.

## Control Flow

There is no runtime control flow. Other source files include these macros and pass them into MMIO helpers such as `RREG32`, `WREG32`, and `WREG32_P`, or use masks/shifts to encode and decode register values.

## State and Persistence Behavior

The header stores no state. Its definitions describe persistent hardware registers that other code reads and writes. A wrong macro value can redirect MMIO operations to the wrong register and cause persistent hardware misconfiguration until reset or reprogramming.

## Dependencies and Integration Points

`r600_reg.h` is guarded by `__R600_REG_H__` and has no includes. It integrates broadly with Radeon R600 family code, especially memory-controller setup, BIOS scratch handling, audio/HDMI programming, power management, and display surface configuration. Some audio definitions are used alongside `r600_hdmi.c` and Radeon audio helpers.

## Risks and Edge Cases

- Register headers are low-level contracts with hardware; typos in addresses, masks, shifts, or enum-like values are difficult to detect at compile time.
- Comments note that audio registers were reverse engineered and naming may be inaccurate, so semantic assumptions should be verified against behavior.
- R600 and R700 memory-controller register layouts differ; callers must select the correct macro family for the ASIC.
- HDMI offsets differ for DCE2 versus DCE3.2; using the wrong offset can program the wrong instance.
- Because macros have no type safety, expressions with side effects or incorrect width can produce bad bitfield values.

## Test Signals

Build tests only prove macro names resolve. Real signals are hardware init success, correct VRAM/aperture setup, working BIOS scratch communication, display scanout with expected channel swizzles/endian settings, DPM GPIO programming, HDMI/audio operation on DCE2 and DCE3.2, and register dumps matching known-good traces for R600/R700 boards.
