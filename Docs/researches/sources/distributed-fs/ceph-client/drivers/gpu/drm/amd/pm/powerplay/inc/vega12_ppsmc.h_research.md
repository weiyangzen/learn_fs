# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/vega12_ppsmc.h

## Purpose

`vega12_ppsmc.h` defines Vega12 SMU message IDs and response codes. It is the command-number companion to `vega12/smu9_driver_if.h`, covering feature masks, table transfers, DPM frequency bounds, fan/thermal settings, GFXOFF/ACG controls, Gemini settings, BACO, and debug queries.

## Important APIs, types, and constants

`SMU_UCODE_VERSION` is `0x00270a00`. `PPSMC_Result` is `uint16_t`; `PPSMC_Msg` is `int`. Response codes include OK, failed, unknown command, rejected prerequisite, and busy.

Vega12 splits feature control into low/high allowed masks, enable masks, disable masks, and enabled-feature queries. Table-related messages include driver/tools DRAM address programming and SMU-to-DRAM/DRAM-to-SMU transfers. DPM control uses frequency-oriented commands such as `SetSoftMinByFreq`, `SetSoftMaxByFreq`, `SetHardMinByFreq`, `SetHardMaxByFreq`, `GetMinDpmFreq`, `GetMaxDpmFreq`, `GetDpmFreqByIndex`, and `GetDpmClockFreq`.

Other messages cover memory channel configuration, Gemini mode/aperture, PCIe parameters, overdrive, deep-sleep DCEF, AC/DC interrupt/power-source notification, UCLK fast switch, reset, RPM/video/fan/temperature settings, MP1 unload, DRAM logging, DIDT, display count, margin removal, serial numbers, virtual DRAM address, ACG/BTC, GFXOFF allow/disallow, PPT-limit query, and DC-mode max DPM frequency.

## Control flow

No functions are defined. The runtime pattern is the SMU message transport. Vega12 managers use these IDs with optional parameters and then poll firmware response. Table-transfer messages pair with table IDs from `vega12/smu9_driver_if.h`.

## State and persistence behavior

Messages update firmware feature state, DPM bounds, table buffers, fan/thermal targets, power limits, PCIe policy, Gemini mode, ACG/GFXOFF state, logging state, and reset/unload state. Query messages return firmware state through the message response/argument registers.

## Dependencies and integration points

The header must be used with Vega12 firmware and Vega12 table layouts. It integrates with SMU9 manager code, PowerPlay feature-mask configuration, display and thermal subsystems, overdrive paths, and BACO/reset handling.

## Risks

Many names overlap with Vega10 and Vega20 but numeric values and available messages differ. Cross-generation reuse is unsafe. Feature-control splitting into low/high words requires callers to update both halves when features exceed 32 bits; otherwise firmware state can be partially configured.

Frequency-oriented DPM commands require correct clock-domain encoding in parameters, which this header does not define. Callers must pair the message with the correct Vega12 parameter convention.

## Test signals

Test signals include successful `GetDriverIfVersion`, feature-mask programming, PP/watermark/metrics/overdrive table transfers, DPM min/max frequency queries and updates, fan/RPM messages, GFXOFF allow/disallow, ACG initialization, BACO transitions, and DC-mode max frequency queries on Vega12 hardware.
