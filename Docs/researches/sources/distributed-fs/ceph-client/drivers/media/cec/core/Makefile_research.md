# sources/distributed-fs/ceph-client/drivers/media/cec/core/Makefile

Purpose: This Makefile composes the `cec.o` core module/object from the mandatory CEC core sources and optional notifier, pin, and pin error-injection implementation files.

Important APIs, types, and functions: `cec-objs := cec-core.o cec-adap.o cec-api.o` is the mandatory object set. Conditional additions are `cec-notifier.o` for `CONFIG_CEC_NOTIFIER`, `cec-pin.o` for `CONFIG_CEC_PIN`, and `cec-pin-error-inj.o` for `CONFIG_CEC_PIN_ERROR_INJ`. `obj-$(CONFIG_CEC_CORE) += cec.o` gates the composite object.

Control flow and state: Kbuild links optional helpers into the same CEC core object when selected, ensuring exported symbols and internal helpers are available to drivers in one module/built-in unit.

State and persistence behavior: Build-only state. Runtime state is defined in the source files.

Dependencies and integration points: Depends on the symbols selected by CEC drivers in Kconfig. The optional source files use internal headers and are not independent modules.

Risks and edge cases: A driver selecting `CEC_PIN` without `CEC_CORE` would be invalid, but current Kconfig selects the core. Enabling error injection without pin support is blocked by Kconfig; bypassing that would create missing symbols.

Test signals: Build matrix for `CEC_CORE=y/m`, with notifier-only, pin-only, and pin plus error-injection configurations, should catch missing object composition.
