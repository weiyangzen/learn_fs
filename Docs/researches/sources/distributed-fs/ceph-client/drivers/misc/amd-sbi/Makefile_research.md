# sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/Makefile

Purpose: defines the object composition for the AMD SB-RMI driver module.

Important APIs and entries: `sbrmi-i2c-objs` includes `rmi-i2c.o` and `rmi-core.o`. `sbrmi-i2c-$(CONFIG_AMD_SBRMI_HWMON)` adds `rmi-hwmon.o`. `obj-$(CONFIG_AMD_SBRMI_I2C)` builds the final `sbrmi-i2c.o` module or built-in object.

Control flow: kbuild always links the transport/probe layer with the ioctl/mailbox core, and optionally links hwmon callbacks when configured.

State and persistence: no runtime state. The build artifact shape determines whether `create_hwmon_sensor_device` is a real function or the inline stub from `rmi-core.h`.

Dependencies and integration points: tied to Kconfig symbols in the same directory and to exported symbols shared among the three C files.

Risks: naming remains `sbrmi-i2c` even when I3C support is active, which can obscure transport coverage in logs and module listings. Missing `rmi-hwmon.o` is expected when hwmon is off, so core callers must continue using the stub.

Test signals: build with hwmon enabled and disabled, verify no unresolved symbols, and inspect module contents for expected object inclusion.
