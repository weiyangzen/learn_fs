# sources/distributed-fs/ceph-client/drivers/ntb/hw/mscc/Makefile

Purpose: Defines the Kbuild rule for the MicroSemi Switchtec NTB hardware driver.

Important APIs, types, and functions: `obj-$(CONFIG_NTB_SWITCHTEC) += ntb_hw_switchtec.o` compiles and links the Switchtec NTB driver when the Kconfig option is enabled.

Control flow: Build-system only; no runtime logic.

State and persistence behavior: No runtime state. The build artifact presence follows the persistent kernel `.config`.

Dependencies and integration points: Connects `CONFIG_NTB_SWITCHTEC` from MSCC Kconfig to the Switchtec NTB implementation source elsewhere in the same directory/subtree.

Risks and edge cases: If the implementation object is renamed or split, this Makefile must be updated. Because Kconfig selects the Switchtec management driver, build failures may surface in either NTB or management-driver dependencies.

Test signals: Subtree build with `CONFIG_NTB_SWITCHTEC=m/y` should emit `ntb_hw_switchtec.o`; disabled configs should omit it.
