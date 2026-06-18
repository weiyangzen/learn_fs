# sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/Makefile

Purpose: this Makefile maps Nomadik and ABx500 Kconfig symbols to their pinctrl object files.

Important APIs, types, and functions: it builds `pinctrl-abx500.o` for `CONFIG_PINCTRL_ABX500`, `pinctrl-ab8500.o` for `CONFIG_PINCTRL_AB8500`, `pinctrl-ab8505.o` for `CONFIG_PINCTRL_AB8505`, `pinctrl-nomadik.o` for `CONFIG_PINCTRL_NOMADIK`, `pinctrl-nomadik-stn8815.o` for `CONFIG_PINCTRL_STN8815`, and `pinctrl-nomadik-db8500.o` for `CONFIG_PINCTRL_DB8500`.

Control flow: Kbuild includes objects conditionally via `obj-$(CONFIG_...)`. The common ABx500 core and each selected AB850x data table are compiled as separate objects, matching the header's init-function stubs.

State and persistence behavior: there is no runtime state. Build selection determines whether the core initcall and SoC data providers are present.

Dependencies and integration points: this file integrates with the Linux Kbuild system and the Kconfig symbols in the same directory.

Risks and test signals: if `PINCTRL_ABX500` is enabled without the needed AB8500 or AB8505 table, the core still builds but no supported compatible can supply SoC data except through enabled subdrivers. Test by building each symbol combination and checking undefined references for `abx500_pinctrl_ab8500_init()`/`ab8505_init()` are avoided by header stubs.
