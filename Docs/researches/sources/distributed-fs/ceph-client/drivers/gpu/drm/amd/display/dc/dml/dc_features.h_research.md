# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dc_features.h

## Purpose

`dc_features.h` is a compile-time feature and capacity definition header for AMD display core/DML. It enumerates the local DC hardware feature shape visible to DML and related display code: counts of DPP/OPP/OTG/DIG/AUX/audio/PHY resources, maximum array dimensions, feature-presence booleans, sync cell parameters, memory power-gating flags, and top-block presence flags.

The header has no executable logic. Its purpose is to give DML and generated display-mode code fixed preprocessor constants for sizing arrays and compiling feature-specific branches.

## Important APIs, Types, And Macros

There are no functions or types. Important macro groups include:

- Core presence/capacity: `DC__PRESENT`, `DC__NUM_DPP`, `DC__NUM_DPP__MAX`, `DC__NUM_OPP`, `DC__NUM_OTG`, `DC__NUM_PIPES`, `DC__VOLTAGE_STATES`.
- Display engine resources: DPP, OPP, DSC, ABM, ODM, OTG, DWB/CWB, DIG, AUX, HPD, DDC, cursor, PHY, and low-power PHY/DIG variants.
- Audio resources: `DC__NUM_AUDIO_STREAMS`, `DC__NUM_AUDIO_ENDPOINTS`, input stream/endpoint counts, audio PLL count.
- Link/output feature flags: HDMI, DP, MST, low-power DP/HDMI/MST, DSI, DAC/DVO, TMDS link type, PHY broadcast, UNIPHY presence, UNIPHY voltage/stagger flags.
- FIFO/sync parameters: digital/DAC/DVO resync FIFO sizes, sync cell choice, latch counts for DISPCLK, DVOCLK, PIXCLK, SYMCLK, DPPCLK, DPREFCLK, REFCLK, PCIE_REFCLK, MVPCLK, SCLK, DCEFCLK, AMCLK, DSICLK, BYTECLK, ESCCLK, and DB clock.
- Memory power-gating flags: `DC__MEM_PG`, block-specific `*_MEM_PG` definitions for DP, AFMT, HDMI, I2C, DSCL, CM, OBUF, WBIF, VGA, FMT, ODM, DSI, AZ, WBSCL memories, DMCU memory, and HUBBUB/HUBPREQ/HUBPRET memories.
- Top block presence: `DC__TOP_BLKS__DCCG`, `DCHUBBUB`, `DCHUBP`, `HDA`, `DIO`, `DCIO`, `DMU`, `DPP`, `MPC`, `OPP`, `OPTC`, `MMHUBBUB`, `WB`, plus max count.
- DML sizing constants consumed elsewhere: `DC__VOLTAGE_STATES` is used for clock-limit arrays, and `DC__NUM_DPP__MAX`, `DC__NUM_CURSOR__MAX`, and `DC__NUM_PIPES__MAX` are used heavily in DML/VBA arrays.

The header also emits value-specific macros such as `DC__NUM_DPP__4`, `DC__NUM_DPP__0_PRESENT`, and `DC__NUM_DPP__MAX__8`, allowing generated code to test either a current value or a supported maximum.

## Control Flow

There is no runtime control flow. Inclusion of this header affects compilation by:

1. Defining exact local feature values, such as four DPPs and four pipes.
2. Defining maximum limits, such as eight maximum DPPs and forty voltage states.
3. Enabling or disabling generated branches through `*_PRESENT` and value-specific macros.
4. Sizing static arrays in DML structures and utility code.

## State And Persistence Behavior

This header holds no runtime state and performs no persistence. The macros become compile-time constants in any translation unit that includes them directly or indirectly. Any change requires recompilation and can alter ABI-like assumptions for structs containing macro-sized arrays.

## Dependencies And Integration Points

`dc_features.h` is an input to DML and display-mode generated code. Repository references show these macros in:

- `dc.h` and `display_mode_structs.h` for `clock_limits[DC__VOLTAGE_STATES]`.
- DML VBA headers and source for arrays sized by `DC__NUM_DPP__MAX`, `DC__NUM_CURSOR__MAX`, `DC__NUM_PIPES__MAX`, and `DC__VOLTAGE_STATES`.
- DCN resource/FPU code that constructs clock tables bounded by `DC__VOLTAGE_STATES`.

The header must stay consistent with hardware resource pools and generated DML model expectations. If hardware support grows, both the current counts and max dimensions may need coordinated updates.

## Risks And Edge Cases

- These macros size stack and struct arrays. Lowering max values can create compile errors or memory corruption if loops elsewhere still assume larger generated limits.
- Raising current resource counts without matching real resource-pool construction can make validation accept configurations the driver cannot program.
- Raising max counts can increase stack usage in generated DML functions with large local arrays.
- Value-specific flags such as `DC__NUM_DPP__4` and `DC__NUM_DPP__MAX__8` can become inconsistent with the base numeric macro if hand-edited.
- Several feature flags are zero despite corresponding max counts being nonzero. Code must distinguish "present now" from "maximum supported by generated model."
- Because this header is broad and generated-looking, unrelated display code can acquire hidden dependencies on specific values; small changes should be treated as platform-wide.

## Test Signals

Useful validation signals include:

- Full display driver build coverage after any macro change, especially DML generated sources that instantiate macro-sized arrays.
- Static analysis for loops bounded by resource pool counts versus macro max counts.
- Boot/display smoke tests confirming the resource pool count matches macro-advertised current counts.
- Mode validation stress tests with maximum DPP/pipe/cursor paths after increasing any max macro.
- ABI/structure layout checks for DML structs if out-of-tree or firmware-facing code consumes the same definitions.
