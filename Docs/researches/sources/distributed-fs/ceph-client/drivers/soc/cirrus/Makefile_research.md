# sources/distributed-fs/ceph-client/drivers/soc/cirrus/Makefile

Purpose: Kbuild file for Cirrus SoC support.

Important build behavior: `obj-y += soc-ep93xx.o` always builds the EP93xx SoC driver when the directory is selected by architecture/Kconfig.

Control flow and integration: it relies on parent Kconfig scoping, so the object is included for EP93xx builds without a per-option object expression.

State and persistence: no runtime state.

Risks and test signals: risk is accidental inclusion outside intended architecture if directory selection changes. Test signals are EP93xx build success and absence of missing auxiliary/regmap symbols.
