# sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/Makefile

Purpose: Kbuild file for the DPAA2 DPIO driver and service layer.

Important build behavior: `fsl-mc-dpio-y` links `dpio.o`, `qbman-portal.o`, `dpio-service.o`, and `dpio-driver.o`; `obj-$(CONFIG_FSL_MC_DPIO)` builds the module or built-in object.

Control flow and integration: this object grouping combines MC command wrappers, software portal mechanics, exported DPAA2 IO service APIs, and fsl-mc bus probing into one driver.

State and persistence: no direct runtime state.

Risks and test signals: risk is missing one component from the composite object, producing unresolved service or portal symbols. Test signals are build/link success and exported `dpaa2_io_*` APIs present when `CONFIG_FSL_MC_DPIO` is enabled.
