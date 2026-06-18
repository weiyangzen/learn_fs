# sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/Makefile

Purpose: Kbuild rules for Cirrus pinctrl drivers.

Important APIs/types/functions: builds standalone `pinctrl-cs42l43.o` and `pinctrl-lochnagar.o`; builds composite `pinctrl-madera.o` from `pinctrl-madera-core.o` plus conditionally included CS47Lxx table objects.

Control flow: `ifeq` blocks append chip-specific table objects only when hidden bool symbols are `y`; the final composite object is linked when `CONFIG_PINCTRL_MADERA` is enabled.

State and persistence: compile-time only.

Dependencies/integration: must stay synchronized with `pinctrl-madera.h` extern declarations and Madera Kconfig chip selectors.

Risks: if a chip table is omitted from `pinctrl-madera-objs`, the common core can reference an extern not linked under corresponding `IS_ENABLED()` paths or fail to support that codec.

Test signals: inspect `pinctrl-madera.o` composition for each Madera codec config and run compile tests for standalone CS42L43/Lochnagar modules.
