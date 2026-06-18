# sources/distributed-fs/ceph-client/drivers/reset/Makefile

Purpose: Kbuild wiring for the reset framework core, subdirectories, and SoC reset driver objects.

Important APIs/types/functions: always builds `core.o` and descends into reset subdirectories. `obj-$(CONFIG_RESET_...)` maps configuration symbols to objects such as `reset-gpio.o`, `reset-imx7.o`, `reset-mpfs.o`, `reset-npcm.o`, and `reset-qcom-aoss.o`.

Control flow: build-time only. Kbuild evaluates `obj-y` and `obj-m` decisions from `.config`; runtime registration is owned by each driver.

State and persistence: no runtime state. The selected object list is build metadata derived from `.config`.

Dependencies and integration: must stay in sync with top-level and subdirectory Kconfig symbols plus source filenames. Subdirectories are always visited so their internal `obj-*` rules decide final objects.

Risks and test signals: stale object names or missing entries break driver builds even when Kconfig is correct. Signals are module and built-in builds for every touched `CONFIG_RESET_*` combination and successful recursive descent into vendor subdirectories.
