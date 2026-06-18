# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/r600_dpm.h

## Purpose

`r600_dpm.h` defines legacy R600-family DPM constants and small enums used by older AMD power-management code. It captures default timing, ramping, voltage-response, PLL, thermal, fan, and table-size parameters that are shared by R600-style DPM implementations.

## Important APIs, Types, and Macros

The header provides default constants such as `R600_ASI_DFLT`, `R600_BSP_DFLT`, `R600_VOLTAGERESPONSETIME_DFLT`, `R600_SPLLSTEPTIME_DFLT`, `R600_MPLLLOCKTIME_DFLT`, and many up/down threshold defaults. Table dimensions include `R600_PM_NUMBER_OF_TC`, `R600_PM_NUMBER_OF_SCLKS`, `R600_PM_NUMBER_OF_MCLKS`, `R600_PM_NUMBER_OF_VOLTAGE_LEVELS`, and `R600_PM_NUMBER_OF_ACTIVITY_LEVELS`. Thermal bounds are `R600_TEMP_RANGE_MIN` and `R600_TEMP_RANGE_MAX`. Fan mode macros are `FDO_PWM_MODE_STATIC` and `FDO_PWM_MODE_STATIC_RPM`.

Enums define `r600_power_level` values low/medium/high/context-switch, `r600_td` direction values auto/up/down, `r600_display_watermark` low/high, and `r600_display_gap` behavior for vblank/watermark/ignore.

## Control Flow

The header has no executable logic. R600-era DPM source files use these constants while constructing hardware performance levels, voltage timing tables, thermal thresholds, fan behavior, and display watermark/gap decisions.

## State and Persistence Behavior

There is no state in this header. Values become runtime state only when copied into ASIC-specific power-info structs or programmed into hardware/SMC registers by including source files.

## Dependencies and Integration Points

The file is standalone apart from kernel integer conventions in users. It belongs to the same `legacy-dpm` folder as newer KV support but targets older R600-style code. It provides common vocabulary for display watermark and power-level decisions that later families kept in similar form.

## Risks and Edge Cases

Many constants are magic hardware tuning values; changing them can affect stability, voltage ramp timing, fan behavior, or display underrun margins. The thermal range has the same uncertain comment as KV. Consumers must know whether values are raw register units, microseconds, milliseconds, or millidegrees.

## Test Signals

Compile coverage of R600 legacy DPM users catches enum and macro dependency issues. Runtime tests should watch boot DPM initialization, thermal interrupt thresholds, fan mode programming, display watermark transitions, suspend/resume, and stable clock/voltage switching under low/medium/high forced levels.
