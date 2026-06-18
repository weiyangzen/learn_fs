# sources/distributed-fs/ceph-client/drivers/hwmon/nct6775-platform.c

## Purpose

`nct6775-platform.c` is the platform/LPC frontend for the shared NCT6775-family hwmon core. It discovers Nuvoton Super-I/O monitor devices through configuration ports, decides whether to access hardware directly or through ASUS ACPI WMI methods on selected boards, provides regmap callbacks for those access modes, detects board-specific fan/PWM/VID/intrusion capabilities, handles suspend/resume restoration, and creates platform devices that call into `nct6775_probe()`.

## Important APIs, Types, and Functions

- `struct nct6775_sio_data` carries Super-I/O port, logical device, kind, access mode, and polymorphic Super-I/O callbacks.
- `enum sensor_access` selects direct I/O port access or ASUS WMI access.
- `nct6775_asuswmi_evaluate_method()`, `nct6775_asuswmi_read()`, and `nct6775_asuswmi_write()` wrap ASUS `WMBD` ACPI calls.
- `superio_*` and `superio_wmi_*` implement direct and WMI-backed Super-I/O register operations.
- `nct6775_reg_read/write()` and `nct6775_wmi_reg_read/write()` are regmap callbacks for HWM register access.
- `nct6775_find()` detects supported Super-I/O device IDs, reads the HWM I/O base, enables the logical device if needed, and unlocks newer HM I/O mapping.
- `nct6775_check_fan_inputs()` inspects many chip-specific pinmux registers to determine `has_fan`, `has_fan_min`, and `has_pwm`.
- `nct6775_platform_probe_init()` reads VID/fan debounce/platform feature state and adds the platform-only "other" attribute group.
- `nct6775_suspend()` and `nct6775_resume()` preserve VBAT, fan dividers, SIO enable, limits, and cached thresholds across sleep.
- `sensors_nct6775_platform_init()` handles DMI board matching, access-mode selection, platform device creation, ACPI conflict checks, and driver registration.

## Control Flow

Module init registers the platform driver, checks DMI vendor/name for ASUS boards in the two allowlists, and if matched attempts to find an ASUS WMI ACPI device by UID. If WMI read of the chip ID succeeds, subsequent access uses WMBD methods; otherwise it uses direct Super-I/O and HWM I/O ports.

For each Super-I/O configuration port, the init path fills direct callbacks, calls `nct6775_find()`, and, if a chip is found, allocates a platform device. Direct access devices receive an I/O resource at `address + IOREGION_OFFSET` after ACPI conflict checking. WMI access devices skip I/O resources and swap the callback table to WMI operations. Platform probe allocates `struct nct6775_data`, chooses the direct or WMI regmap config, stores `nct6775_platform_probe_init()` as `driver_init`, and invokes the shared core.

The platform init hook enters Super-I/O configuration mode, optionally reads CPU VID, optionally enables fan debounce based on the module parameter, calls `nct6775_check_fan_inputs()` to populate presence masks, exits Super-I/O mode, and adds `cpu0_vid`, intrusion, and beep-enable attributes. PM resume re-enters Super-I/O mode, restores enable/mapping state, rewrites cached limits and selected control registers, then invalidates the core cache.

## State and Persistence Behavior

Platform state is split between `struct nct6775_sio_data` in platform data and `struct nct6775_data` owned by the core. The frontend stores direct HWM I/O base in `data->addr`, Super-I/O port in `data->sioreg`, the selected access callbacks in platform data, and PM backup values in core fields such as `vbat`, `fandiv1`, `fandiv2`, and `sio_reg_enable`. Direct regmap access caches the currently selected register bank in `data->bank`; WMI access records the bank but relies on ACPI calls rather than raw bank-select I/O.

Hardware changes include enabling logical devices, enabling HM I/O mappings on newer chips, fan debounce configuration, case-open clear toggles, and all writable core hwmon controls. These persist only as chip/firmware state. The driver keeps no disk state.

## Dependencies and Integration Points

The file integrates raw I/O port access, `request_muxed_region()` for Super-I/O configuration ports, platform device/resource management, ACPI resource conflict checks, ACPI `WMBD` method evaluation, DMI board matching, hwmon VID conversion, Linux PM ops, regmap custom callbacks, and the exported NCT6775 core namespace.

## Risks and Edge Cases

- DMI allowlists for ASUS WMI routing are large and require maintenance; unsupported boards fall back to direct access and may conflict with firmware.
- `force_id` can override detected chip IDs and route the core through an incompatible register map.
- Super-I/O probing may forcibly enable the HWM logical device when disabled, with a warning that sensors may be unusable.
- Fan/PWM presence detection is highly chip- and pinmux-specific; mistakes expose missing channels or hide valid ones.
- WMI methods return limited error detail and are globally tied to the selected `asus_acpi_dev`.
- PM resume writes many cached limits back to hardware; stale cache or failed intermediate writes can leave partial restoration.
- Direct and WMI regmap callbacks depend on correct `nct6775_reg_is_word_sized()` behavior for two-byte registers.
- Platform-only "other" attributes share core alarm/beep helpers and require correct bit-map tables from the core.

## Test Signals

Tests should cover Super-I/O ID matching, `force_id`, zero-base rejection, logical-device enable behavior, ACPI resource conflicts, ASUS DMI/WMI access selection for both UIDs, WMI read/write error propagation, direct banked register reads/writes, fan/PWM pin detection for representative chip families, fan debounce parameter effects, VID visibility, intrusion clear behavior, platform probe with both access modes, and suspend/resume restoration including failure paths.
