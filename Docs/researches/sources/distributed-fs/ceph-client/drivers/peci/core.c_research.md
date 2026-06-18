# sources/distributed-fs/ceph-client/drivers/peci/core.c

Purpose: Provides the PECI bus core: controller allocation/registration, controller removal cleanup, automatic device scanning, PECI bus matching/probe/remove callbacks, and module-level bus registration.

Important APIs and types: `devm_peci_controller_add()` is the exported controller registration API. `peci_controller_scan_devices()` probes PECI CPU addresses `0x30` through `0x37`. `peci_controller_alloc()` creates `struct peci_controller`, assigns an ID with `IDA`, initializes the embedded device, and sets up `bus_lock`. `peci_bus_type` supplies `.match`, `.probe`, `.remove`, and bus sysfs groups. `peci_controller_type` provides the release method.

Control flow: A hardware controller driver calls `devm_peci_controller_add()` late in probe. The core names the controller `peci-N`, enables runtime PM without callbacks, mirrors the firmware node, adds the device, registers a devm cleanup action, then scans all PECI CPU slots. Driver binding checks only PECI devices, matches `peci_device_id.x86_vfm`, and passes the matched ID to the PECI driver probe. Controller unregister walks children in reverse and destroys PECI devices before unregistering the controller device.

State and persistence: Persistent runtime state consists of the controller IDA allocation, controller device, child devices, firmware-node reference, runtime PM state, and `bus_lock`. The release path frees the ID and destroys the mutex. Scanning failures are intentionally non-fatal to controller registration because CPU availability can be transient.

Dependencies and integration points: Depends on Linux device core, bus core, IDA, firmware node/property, runtime PM, and the public PECI API. Integrates with `device.c` for PECI child creation/destruction, `sysfs.c` for bus attributes, and controller drivers such as `peci-npcm.c`.

Risks: `devm_peci_controller_add()` requires a non-null `.xfer`; controller drivers that register too early may expose a bus before hardware is usable. Device scan ignores per-address absence errors, so diagnostics require lower-level debug. The bus match assumes every PECI device has valid `info.x86_vfm`; broken detection in `device.c` prevents later driver binding.

Test signals: Build with `CONFIG_PECI`, bus registration at module load, controller add/remove, rescans, child cleanup on controller removal, module namespace exports, and successful binding of `peci-cpu` to detected Intel VFM IDs.
