# sources/distributed-fs/ceph-client/drivers/media/cec/platform/Makefile

Purpose: This Kbuild file descends into platform CEC driver subdirectories and keeps platform driver linkage in alphabetical order.

Important APIs, types, and functions: It maps `CONFIG_CEC_CROS_EC` to `cros-ec/`, `CONFIG_CEC_GPIO` to `cec-gpio/`, unconditionally descends into `meson/`, and gates `s5p/`, `seco/`, `sti/`, `stm32/`, and `tegra/` by their config symbols.

Control flow and state: The unconditional Meson descent lets that subdirectory gate multiple Meson variants internally. Other subdirectories are only traversed when selected.

State and persistence behavior: Build-only state.

Dependencies and integration points: Consumed by the parent CEC Makefile and platform Kconfig symbols.

Risks and edge cases: Adding platform drivers out of alphabetic order violates local convention and can complicate review. Missing subdirectory entries cause selected Kconfig options to build nothing.

Test signals: Build each platform symbol as module and built-in, especially Meson variants through the unconditional subdir.
