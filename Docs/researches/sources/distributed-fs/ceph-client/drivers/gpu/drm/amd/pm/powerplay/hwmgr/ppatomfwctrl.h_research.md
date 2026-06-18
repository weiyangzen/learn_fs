# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ppatomfwctrl.h

## Purpose
`ppatomfwctrl.h` defines the hwmgr-facing structures and prototypes for atomfirmware-era BIOS control. It is the SOC15/Vega-style companion to the older `ppatomctrl.h` interface.

## Important APIs and types
The header defines `BIOS_CLKID`, atomfirmware master command/data table index macros, `PP_ATOMFWCTRL_MAX_VOLTAGE_ENTRIES`, and normalized output structs for voltage tables, GPIO pin assignment, SOC15 clock dividers, AVFS parameters, GPIO parameters, VBIOS boot values, and SMC DPM parameters. The SMC DPM struct includes I2C addresses/lines, sensor presence, voltage step limits, VR mappings, phase shedding masks, telemetry limits/offsets, AC/DC and VR-hot GPIOs, LEDs, PLL/UCLK/SOCCLK/ACG spread settings, and a second VR I2C address.

Function prototypes expose GPU PLL divider calculation, voltage table and GPIO-voltage detection, AVFS/GPIO/boot/SMC DPM reads, and clock lookup by SMU clock ID.

## Control flow and state
There is no executable code. The declared functions use caller-owned output buffers and normally return `0` on success or a negative/nonzero error on missing tables, unsupported revisions, or failed command execution.

## Dependencies and integration points
The header includes `hwmgr.h` and references atomfirmware enums/struct layouts through `atomfirmware.h` in the implementation. It is consumed by Vega/SOC15 hwmgr code that needs VBIOS-derived AVFS, voltage, PLL, boot, and SMC DPM information.

## Risks and test signals
The interface has many firmware-unit fields and fixed array bounds, so regressions often appear as wrong units or partial copies rather than compile errors. `GetIndexIntoMasterCmdTable` and `GetIndexIntoMasterDataTable` depend on exact atomfirmware v2.1 master-list layouts. Tests should pair header ABI checks with implementation fixtures for v4 voltage objects, v4.1/v4.2 AVFS, firmwareinfo 3.1/3.2, and SMC DPM v4.1 structures.
