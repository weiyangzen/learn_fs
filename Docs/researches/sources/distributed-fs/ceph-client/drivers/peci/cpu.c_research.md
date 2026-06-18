# sources/distributed-fs/ceph-client/drivers/peci/cpu.c

Purpose: Implements the PECI CPU client driver and exports convenience read APIs for CPU temperature, package config space, local PCI config, endpoint PCI config, and endpoint MMIO reads. It also creates auxiliary devices for CPU and DIMM temperature consumers once a supported Intel CPU is detected.

Important APIs and functions: Exported `PECI_CPU` APIs are `peci_temp_read()`, `peci_pcs_read()`, `peci_pci_local_read()`, `peci_ep_pci_local_read()`, and `peci_mmio_read()`. `struct peci_cpu` stores the backing PECI device and matched ID. `adev_alloc()`, `devm_adev_add()`, and `peci_cpu_add_adevices()` create `cputemp.<platform>` and `dimmtemp.<platform>` auxiliary devices. `peci_cpu_device_ids` maps Intel VFM IDs for Haswell through Emerald Rapids Xeon families to short platform strings.

Control flow: The PECI bus matches a detected CPU's `x86_vfm` against `peci_cpu_device_ids` and calls `peci_cpu_probe()`. Probe stores driver data and tries to add both auxiliary devices, warning but continuing if one fails. Read helper functions allocate and execute request helpers from `request.c`, check completion codes where applicable, copy typed data out of the response buffer, and free the request.

State and persistence: The driver stores only per-device driver data and devm-managed auxiliary devices. Auxiliary IDs combine controller ID and PECI address to keep child device identities stable per controller/address. Read APIs do not cache data; each call performs a PECI transaction and returns current target state.

Dependencies and integration points: Depends on `linux/peci.h`, `linux/peci-cpu.h`, the auxiliary bus, and request helpers from `internal.h`. The auxiliary devices are consumed by PECI hwmon-style drivers. It imports `PECI` and exports `PECI_CPU`.

Risks: Helper APIs return raw PECI/target errors, so clients must distinguish transport failure from completion-code failure. Auxiliary device names depend on `id->data`; new VFM entries must use names expected by child drivers. Probe does not fail if auxiliary creation fails, which keeps CPU binding alive but can hide missing sensors without checking warnings.

Test signals: Successful binding for each supported VFM, appearance of auxiliary devices, GetTemp reads, PCS/package config reads, endpoint reads on supported platforms, module autoload via PECI modalias, and negative tests for unsupported VFM IDs.
