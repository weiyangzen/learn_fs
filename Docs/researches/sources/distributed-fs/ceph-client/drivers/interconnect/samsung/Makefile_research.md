# sources/distributed-fs/ceph-client/drivers/interconnect/samsung/Makefile

## Purpose

This Makefile maps the Exynos interconnect Kconfig symbol to the actual object composition. `exynos-interconnect-objs := exynos.o` creates a composite object from the provider implementation, and `obj-$(CONFIG_INTERCONNECT_EXYNOS) += exynos-interconnect.o` includes it when the symbol is built in or as a module.

## Integration And Control Flow

The file participates only in kbuild. Kconfig determines whether the composite object is omitted, built into vmlinux, or emitted as a module. Its object name determines module naming and must stay in sync with `MODULE_ALIAS("platform:exynos-generic-icc")` in `exynos.c`.

## State, Risks, And Test Signals

There is no runtime state. Risks are limited but direct: a symbol mismatch would silently omit the driver, while object-name churn can affect module packaging and autoload expectations. Test signals are successful `make drivers/interconnect/samsung/` builds across builtin and module configurations and the presence of the expected `exynos-interconnect` module when `CONFIG_INTERCONNECT_EXYNOS=m`.
