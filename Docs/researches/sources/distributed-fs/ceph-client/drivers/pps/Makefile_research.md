# sources/distributed-fs/ceph-client/drivers/pps/Makefile

Purpose: builds the PPS core and descends into client/generator directories.

Important rules: `pps_core-y := pps.o kapi.o sysfs.o`; `pps_core-$(CONFIG_NTP_PPS) += kc.o`; `obj-$(CONFIG_PPS) := pps_core.o`; `obj-y += clients/`; `obj-$(CONFIG_PPS_GENERATOR) += generators/`; debug config adds `-DDEBUG`.

Control flow/state: build-only file. The clients directory is always visited so individual client objects can follow their own Kconfig symbols. Generator core is only included when `CONFIG_PPS_GENERATOR` is set.

Dependencies/integration: aligns with top-level Kconfig and header-provided exported PPS APIs.

Risks/test signals: confirm `kc.o` appears only with `CONFIG_NTP_PPS`, clients still build as modules when `PPS` is enabled, generator directory is skipped unless configured, and debug builds emit expected dev/pr debug calls.
