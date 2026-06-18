## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/Makefile

Purpose: defines the object composition for the Dell WMI System Management driver under `CONFIG_DELL_WMI_SYSMAN`.

Important build entries: `obj-$(CONFIG_DELL_WMI_SYSMAN) += dell-wmi-sysman.o` makes the composite module conditional. `dell-wmi-sysman-y` links `sysman.o`, `enum-attributes.o`, `int-attributes.o`, `string-attributes.o`, `passobj-attributes.o`, `biosattr-interface.o`, and `passwordattr-interface.o` into one module.

Control flow: this file has build-time control flow only. It ensures the shared global `wmi_priv`, sysfs population code, attribute validators, and both WMI setter/password interface drivers are linked into one module so symbols remain local to the composite object unless exported elsewhere.

State and persistence: no runtime state. The link composition matters because `wmi_priv` is global across all included objects and the module init/exit lives in `sysman.c`.

Dependencies and integration: participates in the kernel Kbuild system and depends on Kconfig selection of the sysman feature plus the source files' dependencies on WMI and `firmware_attributes_class`.

Risks and test signals: omitting one object breaks unresolved symbols for populate/exit helpers or WMI interface init/exit functions. Build tests should compile `CONFIG_DELL_WMI_SYSMAN=m` and `=y`. Runtime tests are indirect through successful sysman module load and sysfs creation. Because file order is explicit, adding a new attribute type requires updating this Makefile and header prototypes together.
