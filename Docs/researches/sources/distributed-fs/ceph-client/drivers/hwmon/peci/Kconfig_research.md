# sources/distributed-fs/ceph-client/drivers/hwmon/peci/Kconfig

Purpose: Kconfig entries for Intel PECI hwmon clients. It defines user-visible CPU temperature and DIMM temperature monitoring modules plus a hidden shared `SENSORS_PECI` symbol.

Important symbols: `SENSORS_PECI_CPUTEMP` builds the generic PECI CPU temperature client, depends on `PECI`, and selects `SENSORS_PECI` and `PECI_CPU`. `SENSORS_PECI_DIMMTEMP` builds the PECI DIMM temperature client with the same dependency and selections. `SENSORS_PECI` is a hidden tristate used as shared hwmon PECI support.

Control flow: enabling either visible symbol causes the corresponding object from the PECI Makefile to build as built-in or module and ensures the PECI CPU auxiliary-device provider is present. Help text declares module names `peci-cputemp` and `peci-dimmtemp`.

State and persistence: no runtime state. The file controls build-time inclusion and module availability.

Dependencies and integration: integrates hwmon PECI clients with the PECI bus and `PECI_CPU` auxiliary-device layer. The selected hidden symbol groups shared hwmon PECI code paths.

Risks: missing `PECI_CPU` selection would prevent auxiliary device matching. Because both clients select shared support, build coverage should include each symbol alone, both together, built-in, and module forms.

Test signals: `olddefconfig`, `modpost` dependency resolution, module names matching help text, and successful builds with `PECI` disabled/enabled.
