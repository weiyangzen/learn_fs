# sources/distributed-fs/ceph-client/include/linux/mfd/mt6359p/registers.h

## Purpose

This header defines MT6359P-specific register addresses and helper macros for the MT6359 regulator driver. MT6359P is close enough to MT6359 to share driver logic, but many LDO monitor/control and ELR offsets differ; this file isolates those differences.

## Important APIs, Types, and Functions

The file exports `MT6359P_CHIP_VER`, key chip/version and trap/TMA-key addresses, MT6359P buck/LDO/analog register addresses, regulator helper address aliases such as `MT6359P_RG_BUCK_VCORE_VOSEL_ADDR`, `MT6359P_RG_LDO_VSRAM_PROC1_VOSEL_ADDR`, `MT6359P_RG_LDO_VUSB_EN_0_ADDR`, and `MT6359P_RG_VBBCK_VOSEL_ADDR`, plus `MT6359P_VM_MODE_ADDR`, `MT6359P_TMA_KEY_ADDR`, and `TMA_KEY`.

## Control Flow

The header itself has no flow. `mt6359-regulator.c` selects MT6359P descriptors for MT6359P hardware and then uses these macros in normal regulator operations. For some VM mode reads, the driver writes `TMA_KEY` to `MT6359P_TMA_KEY_ADDR`, reads `MT6359P_VM_MODE_ADDR`, and clears the key afterward.

## State and Persistence Behavior

No memory is owned here. The macros target persistent PMIC control state for regulators and protected test/mode access. The TMA key sequence is transient but security-sensitive: leaving the key enabled or writing it on the wrong chip can expose or alter protected PMIC state.

## Dependencies and Integration Points

The header is included by `drivers/regulator/mt6359-regulator.c` alongside `mt6359/registers.h` and `mt6397/core.h`. It assumes the shared MT6359 regulator IDs and descriptor machinery, while providing MT6359P-specific address overrides and the chip-version constant used for hardware selection.

## Risks and Edge Cases

MT6359P offsets often differ by small increments from MT6359 offsets, making copy/paste mistakes hard to spot. Some macros intentionally map VA09 and VA12 voltage selection to ELR registers rather than the apparent analog control addresses. TMA-key writes must be paired with cleanup even on errors. Because many helper macros omit masks/shifts and rely on MT6359 defaults, descriptor code must ensure reused defaults are valid for MT6359P.

## Test Signals

Probe on MT6359P hardware and verify chip version `0x5930`; register all expected regulators; exercise VCORE, VGPU11 SSHUB, VSRAM, VEMC, VUSB, VA09, and VA12 voltage reads/sets; run error-path tests or fault injection around TMA key read sequences; and confirm plain MT6359 hardware still uses the non-P addresses.
