# sources/distributed-fs/ceph-client/drivers/hwmon/peci/Makefile

Purpose: build rules for the PECI hwmon clients.

Important entries: `peci-cputemp-y := cputemp.o` and `peci-dimmtemp-y := dimmtemp.o` define module object composition. `obj-$(CONFIG_SENSORS_PECI_CPUTEMP)` and `obj-$(CONFIG_SENSORS_PECI_DIMMTEMP)` include those modules based on Kconfig state.

Control flow: Kconfig selects determine whether the CPU temperature and DIMM temperature clients are built-in, loadable modules, or omitted. There is no multi-object common library beyond the header-only `common.h`.

State and persistence: no runtime state. The Makefile only maps config symbols to object files.

Dependencies and integration: pairs with `drivers/hwmon/peci/Kconfig` and the parent hwmon build. Module names are derived from `peci-cputemp.o` and `peci-dimmtemp.o`.

Risks: object names must match documented module names and source files. Adding shared C code later would require updating these `*-y` aggregations rather than only adding an `obj-*` line.

Test signals: kernel builds for each config as `m` and `y`, module file names, and no unresolved namespace imports for `PECI_CPU`.
