# sources/distributed-fs/ceph-client/drivers/nvdimm/dimm.c

## Purpose
`dimm.c` is the NVDIMM DIMM driver. It probes `nvdimm` devices, initializes per-DIMM driver data, unlocks or marks security/label state, reads namespace label-area geometry and label data, reserves DPA for active labels, and registers/unregisters the DIMM driver.

## Important APIs, Types, And Functions
The main driver callbacks are `nvdimm_probe()` and `nvdimm_remove()`. Module lifecycle entry points are `nvdimm_init()` and `nvdimm_exit()`, registering an `nd_device_driver` with type `ND_DRIVER_DIMM`.

The probe constructs `struct nvdimm_drvdata`, initializes its DPA resource root, namespace index state, device reference, and kref, then delegates most work to helpers in `dimm_devs.c`, `label.c`, and security code.

## Control Flow
Probe first sets up security event tracking. It checks whether config-data commands are available; `-ENOTTY` is treated as nonfatal for non-aliased DIMMs. If labels are supported, it clears stale locked state, allocates driver data, attempts security unlock, initializes namespace area geometry, and handles `-EACCES` specially as locked capacity. It then reads and validates label data; `-EACCES` here marks the DIMM locked and fails probe because regions cannot safely parse labels.

After label data is available, the driver takes the bus lock and, if a current namespace index exists, reserves DPA for all active labels through `nd_label_reserve_dpa()`. Successful reservation sets the DIMM labeling flag. Remove clears driver data under the bus lock and drops the driver-data kref.

## State And Persistence Behavior
Persistent label state is read from DIMM config data into `ndd->data`. Probe reserves volatile resource-tree entries under `ndd->dpa` for active labels so namespace creation and allocation code can reason about used DPA. Security state is refreshed during probe and may mark the DIMM locked, affecting later namespace probing.

## Dependencies And Integration Points
The file depends on security helpers in `dimm_devs.c`/security support, config-data access in `dimm_devs.c`, label parsing in `label.c`, DPA reservation, and bus locking from `core.c`. It registers with the NVDIMM bus infrastructure from `bus.c`.

## Risks And Edge Cases
The distinction between `-ENOTTY` and `-ENXIO` from config-data support affects whether a DIMM can probe without labels. Locked DIMMs can still enumerate labels if only capacity is locked, but label-data access failures stop probe. If DPA reservation fails after labels are read, probe unwinds and drops driver data, preventing regions from consuming ambiguous label state.

## Test Signals
Tests should cover DIMMs without config-data commands, locked DIMM status during namespace-area and label-data reads, security unlock failure tolerance, label validation failure with no current index, active label DPA reservation, labeling flag setting, probe failure unwind, and remove clearing `dev_get_drvdata()` plus releasing the final kref.
