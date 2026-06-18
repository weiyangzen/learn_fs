# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu10.h

## Purpose

`smu10.h` defines SMU10 firmware feature bits, workload bits, firmware status scratch layout, and SMU table IDs. It is a compact driver/firmware ABI header used by Raven/Picasso-era PowerPlay code to reason about enabled features and firmware-visible DPM levels.

## Important APIs, Types, And Functions

The file declares 64 feature bit positions for controllers and power features such as CCLK, fan, PPT/TDC/thermal/FIT/EDC, PLL power down, ULV, VDDOFF, VCN/ACP/ISP/FCLK/SOCCLK/MP0/LCLK/SHUB/DCEF/GFX DPM, deep sleep clocks, S0i2, whisper mode, MGCG, GFX CKS, PSI0, PROCHOT, CPUOFF, STAPM, and core C-states. It defines masks for many low feature bits and workload bit positions for fullscreen 3D, video, VR, compute, and custom policy.

`FwStatus_t` is a packed bitfield view of MP1 external scratch registers. It tracks current and target DPM levels for ACP, ISP, VCN, LCLK, MP0CLK, FCLK, SOCCLK, DCEFCLK, and SHUBCLK, plus ULV/S0i2/whisper status and a two-dword feature status bitmap. Table IDs include BIOS IF, watermarks, custom DPM, PM status log, DPM clocks, and momentary PM.

## Control Flow And Data Flow

No executable code is present. Driver code reads scratch registers into `FwStatus_t` or interprets equivalent words, checks feature masks, selects workload bits, and requests table transfers using table IDs. Firmware updates status fields asynchronously as DPM levels and low-power states change.

## State And Persistence Behavior

`FwStatus_t` represents firmware-maintained persistent status in MP1 scratch registers. Feature masks and table IDs are compile-time constants. Programmed SMU tables persist in firmware memory until replaced, reset, or firmware reload.

## Dependencies And Integration Points

The header depends on fixed-width types and packed layout. It integrates with `smu10_driver_if.h`, SMU10 hwmgr code, firmware status polling, feature enable/disable controls, workload policy selection, watermarks, custom DPM, PM logging, and DPM clock table transfers.

## Risks And Edge Cases

Several masks use plain `1 << bit`; bits above 31 would overflow a 32-bit int if masks were added for high features without `1ULL`. Bitfield layout is compiler-sensitive. Feature-status arrays span two dwords, so callers must handle 64-bit masks carefully.

## Test Signals

Useful tests are SMU10 build coverage, firmware feature-status reads, DPM level readback during clock changes, S0i2/ULV/GFX DPM transitions, workload switching, table transfer of watermarks/custom DPM/DPM clocks, and high feature bit mask handling.
