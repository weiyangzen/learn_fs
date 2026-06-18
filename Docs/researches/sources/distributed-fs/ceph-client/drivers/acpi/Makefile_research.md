# sources/distributed-fs/ceph-client/drivers/acpi/Makefile

## Purpose
The ACPI Makefile maps Kconfig selections to ACPI core objects, built-in helpers, optional modules, and nested subdirectories. It is the build contract for the files in this subset.

## Important APIs, Types, And Functions
Key object lists are `obj-$(CONFIG_ACPI)`, `acpi-y`, conditional `acpi-$(CONFIG_...)`, and module-specific lists such as `processor-y`, `fan-objs`, and `video-objs`. This subset is wired through entries for `acpi_processor.o`, `acpi_apd.o`, `acpi_platform.o`, `acpi_pnp.o`, `acpi_lpat.o`, `acpi_fpdt.o`, `acpi_lpit.o`, `acpi_pcc.o`, `acpi_ffh.o`, `acpi_mrrm.o`, `acpi_adxl.o`, `acpi_ipmi.o`, `ac.o`, `acpi_tad.o`, `processor.o`, `acpi_memhotplug.o`, `acpi_pad.o`, `acpi_extlog.o`, `acpi_configfs.o`, and `acpi_dbg.o`.

## Control Flow
Built-in ACPI core composition is collected into `acpi-y`, while standalone drivers are assigned to `obj-*`. `CONFIG_ACPI_CUSTOM_DSDT` adds an explicit dependency from `tables.o` to the configured included DSDT file. `CONFIG_TRACE_BRANCH_PROFILING` disables branch profiling for `processor_idle.o`. Nested directories are added conditionally by subsystem or architecture.

## State And Persistence
The Makefile does not manage runtime state. It persists the build topology: whether objects are linked into the ACPI core module/built-in object, emitted as independent modules, or omitted.

## Dependencies And Integration Points
It depends directly on Kbuild conventions and the Kconfig symbols defined in this and nested ACPI Kconfig files. It integrates ACPI with PMIC, DPTF, APEI, NFIT, NUMA, architecture subdirectories, processor cpufreq/idle/throttling helpers, and video/fan composite objects.

## Risks
Moving objects between `acpi-y` and `obj-*` changes module boundaries, initialization ordering, symbol visibility, and module parameters. The comment that IPMI initializes before other drivers is important because AML IPMI OpRegions may be used by unrelated ACPI drivers. Missing conditional dependencies can silently drop firmware support.

## Test Signals
Allmodconfig/allyesconfig and minimal ACPI builds should verify object inclusion. Module builds should confirm expected module names (`ac`, `acpi_ipmi`, `acpi_tad`, `processor`, `acpi_pad`, `acpi_configfs`, `acpi_dbg`, `acpi_extlog`) and built-in core linkage for helper files.
