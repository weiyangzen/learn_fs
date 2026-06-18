# sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/Kconfig

Purpose: this Kconfig file exposes configuration switches for ST-Ericsson ABx500 mixed-signal chip pinctrl/GPIO support and Nomadik/U8500 SoC pinctrl support.

Important APIs, types, and functions: it defines `PINCTRL_ABX500`, `PINCTRL_AB8500`, `PINCTRL_AB8505`, `PINCTRL_NOMADIK`, `PINCTRL_STN8815`, and `PINCTRL_DB8500`. `PINCTRL_ABX500` depends on `AB8500_CORE` and selects `GENERIC_PINCONF`. `PINCTRL_NOMADIK` depends on OF and selects `PINMUX`, `PINCONF`, `GPIOLIB`, and `GPIO_NOMADIK`.

Control flow: Kconfig visibility is split by architecture guards. ABx500 options are visible for `ARCH_U8500` or `COMPILE_TEST`. Nomadik options are visible for `ARCH_U8500`, `ARCH_NOMADIK`, or `COMPILE_TEST`. The AB8500 and AB8505 table drivers depend on the common ABx500 core option.

State and persistence behavior: Kconfig has no runtime state, but it controls which object files and init functions are built into the kernel. Because these are bool options, enabled drivers are built-in rather than modules in this configuration fragment.

Dependencies and integration points: this file integrates the pinctrl drivers with architecture selection, the AB8500 MFD core, generic pinconf, gpiolib, and Nomadik GPIO support.

Risks and test signals: `PINCTRL_ABX500` selects generic pinconf but not `PINMUX` explicitly, relying on broader pinctrl dependencies. COMPILE_TEST coverage can expose missing includes or MFD stubs. Test with U8500, Nomadik, and COMPILE_TEST builds, including AB8500-only, AB8505-only, and both table-driver combinations.
