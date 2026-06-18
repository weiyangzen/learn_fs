# sources/distributed-fs/ceph-client/drivers/accel/rocket/Makefile

Purpose: wires the Rocket driver object list into Kbuild.

Important APIs and types: builds `rocket.o` when `CONFIG_DRM_ACCEL_ROCKET` is enabled and composes it from `rocket_core.o`, `rocket_device.o`, `rocket_drv.o`, `rocket_gem.o`, and `rocket_job.o`.

Control flow: Kbuild links these objects into one module or built-in object. There are no conditional sub-objects beyond the top-level config gate.

State and persistence: no runtime state.

Dependencies and integration: must stay aligned with source files and Kconfig. The order places core/device/driver/GEM/job objects in one module.

Risks and test signals: compile the module after adding/removing source files and check `modinfo rocket` to confirm the expected module composition.
