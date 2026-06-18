# sources/distributed-fs/ceph-client/drivers/pps/generators/Makefile

Purpose: builds the PPS generator core and optional generator drivers.

Important rules: `pps_gen_core-y := pps_gen.o sysfs.o`; `obj-$(CONFIG_PPS_GENERATOR) := pps_gen_core.o`; optional objects are `pps_gen-dummy.o` and `pps_gen_tio.o`; debug config adds `-DDEBUG`.

Control flow/state: build-only file.

Dependencies/integration: source module names and Kconfig symbols must align with userspace-visible `/dev/pps-genN` support from the core.

Risks/test signals: build all generator combinations as built-in/module, verify core is present before optional drivers link, and ensure debug builds compile all generator objects.
