# sources/distributed-fs/ceph-client/drivers/firmware/smccc/smccc.c

## Purpose
`smccc.c` stores global ARM SMCCC discovery results and registers SMCCC-backed devices such as TRNG. It is initialized by PSCI when firmware reports SMCCC v1.1+ support.

## Important APIs And Functions
- Global state: `smccc_version`, `smccc_conduit`, `smccc_trng_available`, `smccc_soc_id_version`, and `smccc_soc_id_revision`.
- `arm_smccc_version_init()` records version/conduit, probes TRNG, and for SMCCC 1.2+ queries `ARCH_SOC_ID`.
- `arm_smccc_1_1_get_conduit()` and `arm_smccc_get_version()` are exported.
- `arm_smccc_get_soc_id_version()` and exported `arm_smccc_get_soc_id_revision()` expose SOC_ID data.
- `arm_smccc_hypervisor_has_uuid()` checks vendor hypervisor UUID.
- `smccc_devices_init()` registers `smccc_trng` if available.

## Control Flow
PSCI calls `arm_smccc_version_init()` with the discovered SMCCC version and conduit. The function probes architecture TRNG support and, when supported, uses `ARM_SMCCC_ARCH_FEATURES` to detect `ARCH_SOC_ID`, then queries version and revision. Later, a device initcall registers a simple `smccc_trng` platform device when TRNG is available.

## State And Persistence
Discovery state is stored in `__ro_after_init` globals where applicable and persists for the boot. There is no persistent storage; the values reflect firmware responses.

## Dependencies And Integration Points
It depends on SMCCC call helpers, PSCI/SMCCC version encodings, architecture random support, and platform-device registration. `soc_id.c`, KVM discovery, and hypervisor-specific drivers consume these values and helpers.

## Risks
The default version is SMCCC 1.0 until PSCI initializes it, so users must not assume discovery happened early. SOC_ID values are accepted only if the feature probe succeeds and returned values are nonnegative. Hypervisor UUID checks rely on vendor call availability.

## Test Signals
Boot logs from PSCI should report SMCCC version. Presence of the `smccc_trng` platform device, successful SOC_ID sysfs registration, and correct hypervisor UUID matching validate discovery paths.
