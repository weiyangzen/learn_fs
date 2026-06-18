# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/Makefile

Purpose: Defines how the UCSI core and transport modules are built.

Important APIs/types/functions: `typec_ucsi-y := ucsi.o` is the core object. Conditional additions include `debugfs.o` for `CONFIG_DEBUG_FS`, `trace.o` for `CONFIG_TRACING`, `psy.o` when `CONFIG_POWER_SUPPLY` is non-empty, `displayport.o` when `CONFIG_TYPEC_DP_ALTMODE` is enabled, and `thunderbolt.o` when `CONFIG_TYPEC_TBT_ALTMODE` is enabled. Separate module objects are listed for ACPI, CCG, STM32G0, PMIC GLINK, ChromeOS EC, Lenovo Yoga C630, and Huawei Gaokun transports.

Control flow and state: no runtime behavior. It shapes which code paths exist in the final kernel or modules and sets `CFLAGS_trace.o := -I$(src)` so generated trace headers can be found.

Persistence behavior: none beyond build outputs.

Dependencies/integration points: mirrors `Kconfig` options and the conditional declarations in `ucsi.h` for debugfs, power supply, DisplayPort, and Thunderbolt support.

Risks: mismatch between Kconfig and Makefile can create unresolved symbols or missing functionality. The `ifneq ($(CONFIG_*),)` style includes helper objects for both built-in and module states, which is intentional but should be kept consistent with header stubs.

Test signals: build with minimal `TYPEC_UCSI`, with all helpers enabled, with helpers disabled but core enabled, and with each transport as module/built-in. Trace builds should confirm include path correctness.
