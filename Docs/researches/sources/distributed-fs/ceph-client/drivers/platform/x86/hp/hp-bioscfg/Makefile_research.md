# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/Makefile

Purpose: defines the `hp-bioscfg` module composition.

Important APIs/types/functions: `obj-$(CONFIG_HP_BIOSCFG) := hp-bioscfg.o` and `hp-bioscfg-y := ...` link the common core, WMI set interface, typed attribute handlers, password/SPM handlers, and Sure Start support into one module.

Control flow: Kbuild links `bioscfg.o`, `biosattr-interface.o`, `enum-attributes.o`, `int-attributes.o`, `order-list-attributes.o`, `passwdobj-attributes.o`, `spmobj-attributes.o`, `string-attributes.o`, and `surestart-attributes.o` into the composite object. Runtime init is provided by `bioscfg.c`.

State and persistence: no runtime state in this file; build state is controlled by `CONFIG_HP_BIOSCFG`.

Dependencies and integration: all listed sources share `bioscfg.h` and the global `bioscfg_drv`. Missing an object here breaks cross-file symbol resolution, for example `hp_set_attribute()`, typed populate functions, or cleanup hooks.

Risks and test signals: object-list drift is the main risk. Compile/link testing with `CONFIG_HP_BIOSCFG=m` verifies all prototypes and exported internal helpers remain aligned.
