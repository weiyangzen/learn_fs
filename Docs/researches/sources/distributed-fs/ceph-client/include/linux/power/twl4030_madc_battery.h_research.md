# sources/distributed-fs/ceph-client/include/linux/power/twl4030_madc_battery.h

Purpose: defines platform calibration data for simple Li-Ion battery capacity estimation using the TWL4030 MADC.

Important APIs and types: `struct twl4030_madc_bat_calibration` maps voltage in mV to capacity percent and uses voltage `-1` as end marker. `struct twl4030_madc_bat_platform_data` supplies total capacity in uAh plus separate charging and discharging calibration tables and sizes.

Control flow: the battery driver reads MADC voltage, selects charging or discharging calibration curve, interpolates capacity/level, and reports battery properties using the supplied total capacity.

State and persistence: static board calibration data only; measured voltage and reported state are runtime driver data.

Dependencies and integration points: integrates with TWL4030 MADC readings and power_supply reporting.

Risks and test signals: risks include unsorted or unterminated calibration tables, wrong charging/discharging curve selection, capacity unit mistakes, and inaccurate endpoints. Test capacity interpolation on both curves, end-marker handling, low/full voltage boundaries, and reported charge units.
