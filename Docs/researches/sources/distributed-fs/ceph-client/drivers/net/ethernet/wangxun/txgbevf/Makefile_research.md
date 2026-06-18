# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbevf/Makefile

Purpose: builds the Wangxun TXGBE virtual-function driver object.

Important build rules: `obj-$(CONFIG_TXGBE) += txgbevf.o` ties VF object compilation to `CONFIG_TXGBE`; `txgbevf-objs := txgbevf_main.o` states that the module is currently a single source-file composite object.

Control flow and integration: Kbuild turns this directory rule into `txgbevf.ko` or built-in code depending on the parent Makefile and `CONFIG_TXGBE`. The VF driver shares the same config symbol as the PF driver rather than using a distinct `CONFIG_TXGBEVF`, so enabling TXGBE also selects this object when the directory is descended.

State and persistence: no runtime state. It controls object inclusion only.

Risks and tests: the main risk is configuration coupling: distributions expecting separate PF/VF toggles cannot disable the VF independently from this file. Build tests should verify modular and built-in TXGBE configurations and confirm `txgbevf_main.o` is included exactly once.
