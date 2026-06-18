# sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/Makefile

## Purpose
This Makefile maps PCI power-control Kconfig symbols to kernel objects and module names. It builds the shared core and the generic, pwrseq, and TC9563 providers.

## Important APIs, types, and functions
`obj-$(CONFIG_PCI_PWRCTRL)` builds `pci-pwrctrl-core.o` from `core.o`. `obj-$(CONFIG_PCI_PWRCTRL_PWRSEQ)` builds `pci-pwrctrl-pwrseq.o`. `obj-$(CONFIG_PCI_PWRCTRL_GENERIC)` builds `pci-pwrctrl-generic.o` from `generic.o`. `obj-$(CONFIG_PCI_PWRCTRL_TC9563)` builds `pci-pwrctrl-tc9563.o`.

## Control flow
There is no runtime logic. During kbuild evaluation, selected config symbols append the appropriate objects to the directory build.

## State and persistence
The file contributes build artifacts only. It does not create runtime state.

## Dependencies and integration points
The Makefile is driven by the sibling Kconfig and by kbuild. The generated module names match the platform driver modules used by devicetree modalias autoloading.

## Risks
Object naming must remain aligned with exported module aliases and Kconfig symbols. A mismatch would result in selected drivers not being built or modules not loading under expected names.

## Test signals
Use `make M=drivers/pci/pwrctrl` or full kernel builds with each symbol enabled as `y` and `m`. Confirm resulting objects/modules include `pci-pwrctrl-core`, `pci-pwrctrl-pwrseq`, `pci-pwrctrl-generic`, and `pci-pwrctrl-tc9563` as configured.
