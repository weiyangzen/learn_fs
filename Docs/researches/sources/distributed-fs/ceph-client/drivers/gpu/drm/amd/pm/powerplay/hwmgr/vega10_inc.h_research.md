# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h

## Purpose
This header centralizes Vega10 register include files needed by the hardware manager and BACO implementation. It pulls in default, offset, and shift/mask definitions for THM, MP, GC, and NBIO register blocks so implementation files can use generated register names and bit masks.

## Important APIs, Types, and Functions
This file declares no functions or types. Its important surface is the include bundle:
- THM 9.0 defaults, offsets, and masks.
- MP 9.0 offsets and masks.
- GC 9.0 defaults, offsets, and masks.
- NBIO 6.1 defaults, offsets, and masks.

## Control Flow and Integration
There is no runtime control flow. Files such as `vega10_baco.c` include it to access register constants used in SOC15 command-table entries and bit manipulation.

## State and Persistence
No state is stored here. It only makes generated register metadata visible at compile time.

## Dependencies
The header depends on generated ASIC register headers under `asic_reg/`. Those headers provide the symbolic register offsets and masks used by SOC15 access macros.

## Risks
- Incorrect register-generation version or wrong IP block include would make register programming target the wrong offsets or masks.
- Because this header is a broad include bundle, users may appear to compile without including the exact IP-specific header they directly need, increasing hidden dependency coupling.

## Test Signals
- Build tests should catch missing generated register headers or renamed symbols.
- Hardware smoke tests that exercise BACO, DPM, thermal, and SMU register paths indirectly validate that the included register definitions match Vega10 silicon.
