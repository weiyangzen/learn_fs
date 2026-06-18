
# sources/distributed-fs/ceph-client/drivers/soc/imx/soc-imx.c

## Purpose
Legacy/32-bit i.MX SoC bus registration. It identifies the current i.MX/VF SoC from `__mxc_cpu_type`, reads machine model and optional OCOTP/IIM unique ID, formats revision, and registers a `soc_device`.

## Important APIs, Types, and Functions
- `imx_soc_device_init()` is a `device_initcall()`.
- Uses CPU type constants from `soc/imx/cpu.h`, revision from `imx_get_soc_revision()`, syscon regmap lookups for OCOTP/IIM, and `soc_device_register()`.

## Control Flow
The initcall exits if not running on an i.MX CPU. It allocates `soc_device_attribute`, reads root model, maps CPU type to `soc_id` and OCOTP compatible, reads UID in SoC-specific layouts if a regmap is found, formats revision and serial number, registers the SoC device, and frees allocated strings on errors.

## State and Persistence
Registers one SoC bus device and allocated attribute strings. No file persistence. UID/revision are read from hardware fuses/global state.

## Dependencies and Integration Points
Depends on architecture-provided `__mxc_cpu_type`, OF root model, syscon OCOTP/IIM nodes, and SoC bus core.

## Risks
- Missing root `model` fails registration.
- OCOTP lookup failure logs but still registers with serial zero.
- No unregister path for the initcall-created SoC device, which is normal for built-in early SoC identity code.

## Test Signals
CPU-type mapping coverage, UID paths for i.MX7ULP, MX51/MX53, and OCOTP variants, missing OCOTP fallback, allocation failure paths, and expected `/sys/devices/soc0` attributes.
