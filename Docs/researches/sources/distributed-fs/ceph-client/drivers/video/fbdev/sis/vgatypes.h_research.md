# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/vgatypes.h

## Purpose
`vgatypes.h` supplies base type definitions for the SiS universal mode-setting code. In this kernel copy it mainly defines the IO address type, the `__iomem` annotation macro used by shared structures, and the canonical `SIS_CHIP_TYPE` enumeration.

## Important APIs And Types
- `SISIOMEMTYPE` is first defined empty, then `linux/types.h` is included, and `SISIOMEMTYPE` is redefined to `__iomem`. `vstruct.h` uses it to annotate memory-mapped pointers inside `struct SiS_Private`.
- `typedef unsigned long SISIOADDRESS;` represents VGA/bridge IO port base addresses and relocated IO addresses used by `SiS_SetReg*()`/`SiS_GetReg*()`.
- `SIS_CHIP_TYPE` enumerates logical chip families: legacy/old chips, SiS 300/540/630/730, SiS 315/550/650/740/330/661/741/670/660/760/761/762/770/340/341/342, XGI 20/21/40, and `MAX_SIS_CHIP`.

## Control Flow And Use
- There is no runtime control flow; this file is consumed at compile time by `sis.h` and `vstruct.h`.
- `sis_main.c` stores chip IDs in `ivideo->chip`, `ivideo->chip_real_id`, and `SiS_Pr.ChipType` using these values and switches on them for DRAM sizing, bridge detection, POST, and mode validation.
- `SISIOADDRESS` flows through register access function prototypes and `struct SiS_Private` fields for sequencer, CRTC, DAC, bridge, capture, and playback ports.

## State And Persistence Behavior
- The enum values are ABI-like internal constants. Several values are explicitly numbered, such as `SIS_660 = 35`, `SIS_340 = 55`, and `XGI_20 = 75`, preserving compatibility with shared SiS mode-setting code.
- No mutable state is defined here.

## Dependencies And Integration Points
- Includes `<linux/types.h>` solely to get `__iomem`.
- Integrated by `sis.h`, `vstruct.h`, and any low-level mode-setting source that needs chip IDs or IO address typing.
- Bridges hardware-specific branches in `sis_main.c` and low-level init code by giving both layers a shared chip taxonomy.

## Risks And Edge Cases
- Changing enum numeric values would break switch logic and shared tables that rely on stable chip family ordering or explicit IDs.
- `SISIOADDRESS` as `unsigned long` is suitable for port-like addresses in this driver but should not be treated as a pointer; memory-mapped pointers use `SISIOMEMTYPE`.
- `SISIOMEMTYPE`'s redefine pattern is unusual; include-order changes could accidentally lose or duplicate sparse annotations.

## Test Signals
- Sparse/build checks should confirm `__iomem` annotations remain valid after including this header.
- Compile all files using `SIS_CHIP_TYPE` switches to catch missing cases after enum edits.
- Runtime chip detection for SiS and XGI cards should map PCI IDs to the expected enum values in `sisfb_chip_info[]`.
