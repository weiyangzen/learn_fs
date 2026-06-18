# sources/distributed-fs/ceph-client/drivers/thermal/renesas/Makefile

Purpose: build mapping for Renesas thermal drivers.

Important entries: `CONFIG_RCAR_GEN3_THERMAL` builds `rcar_gen3_thermal.o`, `CONFIG_RCAR_THERMAL` builds `rcar_thermal.o`, `CONFIG_RZG2L_THERMAL` builds `rzg2l_thermal.o`, `CONFIG_RZG3E_THERMAL` builds `rzg3e_thermal.o`, and `CONFIG_RZG3S_THERMAL` builds `rzg3s_thermal.o`.

Control flow and integration: the file is direct Kbuild glue. It does not aggregate objects or define composite modules; each source becomes its own module or built-in object based on the Kconfig symbol.

State, dependencies, and risks: no runtime state. The risk is simple drift between Kconfig symbols, source filenames, and module names. New Renesas thermal files must be added here and to Kconfig together.

Test signals: compile all five symbols as built-in and as modules; verify module aliases in each source still match DT compatibles.
