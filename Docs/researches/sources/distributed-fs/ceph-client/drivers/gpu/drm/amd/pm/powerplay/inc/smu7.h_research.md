# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu7.h

## Purpose

`smu7.h` defines shared SMU7 firmware constants and compact structures for older discrete GPU PowerPlay support. It describes DPM level limits, scratch-register bit fields, VR configuration encoding, PID control parameters, feature masks, firmware header layout, and display configuration enum values.

## Important APIs, Types, And Functions

The file defines SMU and VBIOS context IDs, maximum levels for voltage rails, graphics, memory, GIO, PCIe link, UVD, VCE, ACP, SAMU, and SMIO. It exports DPM action constants, GPIO clamp modes, scratch B target/current index masks for PCIe/UVD/VCE/ACP/SAMU, VR configuration masks and shifts, VR source values, `SMU7_PIDController`, feature-enable masks, handshake-disable masks, `SMU7_Firmware_Header`, `SMU7_FIRMWARE_HEADER_LOCATION`, and `enum DisplayConfig`.

`SMU7_Firmware_Header` maps firmware image metadata and table offsets: digest, version, sizes, entry point, RTOS, soft registers, DPM table, fan table, CAC tables, MC register/timing tables, PM fuse table, globals, reserved space, and signature.

## Control Flow And Data Flow

No code is present. Driver code uses constants to parse firmware headers, locate SMC tables, configure DPM limits, interpret scratch register indexes, and encode voltage-controller configuration. Display configuration values feed SMC policy for display PHY/link conditions.

## State And Persistence Behavior

The header defines layouts for persistent firmware image data and runtime SMC table/register state. Scratch fields reflect current/target DPM levels maintained by firmware. VR and handshake settings persist after table or soft-register programming.

## Dependencies And Integration Points

It depends on `SMU__NUM_*` macros from generation-specific headers such as `smu71.h` or sibling ASIC headers, plus fixed-width types. It integrates with SMU7 hwmgr, firmware loading, PP table conversion, MC table setup, voltage controller setup, display configuration policy, UVD/VCE/ACP/SAMU DPM, and PCIe DPM.

## Risks And Edge Cases

`SMU7_CONTEXT_ID_SMC` and `SMU7_CONTEXT_ID_VBIOS` are duplicated. Macro dependencies mean include order matters. Scratch masks assume three-bit level indexes. Firmware header layout is packed ABI and must match the firmware image exactly.

## Test Signals

Useful checks are SMU7 firmware header parsing, DPM table offset validation, scratch register decode during clock changes, voltage-controller configuration tests, UVD/VCE/PCIe DPM transitions, display config changes, and firmware signature/version sanity.
