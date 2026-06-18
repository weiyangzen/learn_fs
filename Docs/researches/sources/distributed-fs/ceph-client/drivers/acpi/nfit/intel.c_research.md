# sources/distributed-fs/ceph-client/drivers/acpi/nfit/intel.c

`intel.c` implements Intel NFIT DSM adapters for libnvdimm security and firmware activation. It wraps Intel vendor payloads in `ND_CMD_CALL`, translates firmware status into kernel errors or libnvdimm enums, and exports `intel_security_ops`, `intel_fw_ops`, and `intel_bus_fw_ops` for attachment by `core.c`.

Important functions include `intel_fwa_supported()`, `firmware_activate_noidle_{show,store}()`, security operations for flags, freeze, key change, unlock, disable, erase, overwrite, and query-overwrite, plus bus firmware activation helpers `intel_bus_fwa_businfo()`, `intel_bus_fwa_state()`, `intel_bus_fwa_capability()`, and `intel_bus_fwa_activate()`. DIMM activation helpers are `intel_fwa_dimminfo()`, `intel_fwa_state()`, `intel_fwa_result()`, and `intel_fwa_arm()`.

Security control flow builds packed trailing-overlap command packages, copies passphrases into Intel payload structs, calls `nvdimm_ctl()`, and maps statuses such as invalid passphrase, unsupported operation, invalid state, or overwrite busy. Firmware activation is split between bus-level state/capability/activate and DIMM-level info/result/arm. Bus activation invalidates cached bus state and increments `acpi_desc->fwa_count` so per-DIMM result caches refresh.

State is cached in `struct acpi_nfit_desc` for bus activation state, capability, count, and no-idle policy, and in `struct nfit_mem` for per-DIMM activation state/result/count. Dependencies include libnvdimm, Intel payload definitions in `intel.h`, provider data from `nfit.h`, and DSM masks established by `core.c`.

Risks include ABI-sensitive packed payloads, destructive security operations, passphrase handling, state-cache invalidation, and the `firmware_activate_noidle` quiesce policy. Test signals should cover each Intel status translation, unsupported command masks, master/user passphrase paths, overwrite busy, arm/disarm idempotence, bus armed/idle/busy activation, activation count invalidation, and the sysfs no-idle toggle.
