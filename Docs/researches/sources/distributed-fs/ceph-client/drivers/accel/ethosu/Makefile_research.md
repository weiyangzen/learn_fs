# sources/distributed-fs/ceph-client/drivers/accel/ethosu/Makefile

Purpose: defines the object composition for the Arm Ethos-U DRM accel driver.

Important entries: `ethosu-y` includes `ethosu_drv.o`, `ethosu_gem.o`, and `ethosu_job.o`; `obj-$(CONFIG_DRM_ACCEL_ETHOSU)` builds the combined `ethosu.o` module or built-in object.

Control flow: Kbuild compiles the driver only when `DRM_ACCEL_ETHOSU` is enabled.

State and persistence: no runtime state.

Dependencies: the object list mirrors the driver split: platform/DRM probe, GEM/cmdstream validation, and scheduler/job execution.

Risks: adding new source files requires updating this list; missing objects cause unresolved symbols for declared helpers.

Test signals: module and built-in builds, incremental builds after each source change, and link checks for all `ethosu_*` symbols.
