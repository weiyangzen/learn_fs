# sources/distributed-fs/ceph-client/drivers/mfd/Kconfig

Purpose: Kconfig menu for Linux multifunction device drivers under `drivers/mfd`. It declares the selectable symbols, dependencies, and helper selections that decide which MFD core/interface drivers are built and which child subsystems can be reached.

Important APIs, types, and functions: this is declarative build configuration. Relevant symbols in this subset include `MFD_88PM800`, `MFD_88PM805`, `MFD_88PM860X`, `MFD_88PM886_PMIC`, `MFD_AAT2870_CORE`, `ABX500_CORE`, `AB8500_CORE`, and `MFD_AC100`. The file also defines common foundational symbols such as `MFD_CORE`, `MFD_AXP20X`, `MFD_ARIZONA`, and many bus-specific interface variants.

Control flow: the menu is gated by `HAS_IOMEM`. Each `config` block sets type (`bool`/`tristate`), prompts, dependency expressions, selected support libraries (`REGMAP_I2C`, `REGMAP_IRQ`, `IRQ_DOMAIN`, `MFD_CORE`, etc.), defaults, and help text. Downstream Makefiles consume these symbols through `obj-$(CONFIG_...)`.

State and persistence: no runtime state. The persistent effect is the kernel `.config`, which controls compilation, module/builtin form, and whether dependencies are forced through `select`.

Dependencies and integration: integrates with Kbuild and subsystem menus. It expresses hardware/bus constraints such as I2C-only PMICs, OF requirements, platform architecture requirements, and core helper dependencies.

Risks: `select` can force helper symbols without exposing all runtime prerequisites; `bool` choices such as `MFD_88PM860X`/`MFD_88PM886_PMIC` prevent modular builds; menu-wide `HAS_IOMEM` can hide drivers whose implementation is mostly I2C/RSB; Kconfig dependency drift can break builds if Makefile object mappings change without matching symbols.

Test signals: run `olddefconfig`, targeted `allyesconfig`/`allmodconfig`, and compile-test configurations; verify each symbol produces the expected objects; confirm dependency prompts appear/disappear correctly for I2C, OF, SUNXI_RSB, ARCH_U8500, and COMPILE_TEST cases.
