<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/Makefile -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/Makefile

Purpose: kernel build manifest for IIO magnetometer drivers. It maps Kconfig symbols to object files and groups multi-object ST magnetometer core/buffer pieces.

Important APIs/types/functions: declarative `obj-$(CONFIG_...) += ...` entries build per-driver modules. Shared cores are represented by `bmc150_magn.o`, `hmc5843_core.o`, and `rm3100-core.o`, while bus front-ends build separate I2C/SPI objects. `st_magn-y := st_magn_core.o` and `st_magn-$(CONFIG_IIO_BUFFER) += st_magn_buffer.o` define a compound object.

Control flow: kbuild evaluates enabled symbols from `.config`, adds corresponding objects to the directory build, and produces modules or built-in objects. Ordering is mostly alphabetical as noted in comments, with blank lines grouping families.

State/persistence: no runtime state exists. Build outputs are determined entirely by Kconfig state and kbuild rules.

Dependencies/integration: integrates with the Kconfig file in the same directory, module namespace imports in bus wrappers, and object names expected by help text and packaging. It includes entries for drivers beyond this work item, so changes can affect the whole magnetometer subtree.

Risks: missing an object entry for a Kconfig option silently prevents a selected driver from building. Renaming a file without updating this manifest breaks module builds. Shared-core and bus-wrapper symbols must remain paired or wrappers will link without exported common code.

Test signals: run `make M=drivers/iio/magnetometer` under all relevant configs, including module and built-in combinations for BMC150, HMC5843, RM3100, and MMC5633 I2C/I3C. `scripts/checkkconfigsymbols.py` and modpost namespace checks should remain clean.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/Makefile -->
