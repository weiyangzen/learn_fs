# sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/Kconfig

## Purpose
This Kconfig file defines the PCI power-control subsystem and the provider drivers that can power PCI slots or endpoints before PCI enumeration. It also keeps deprecated `PWRCTL` compatibility symbols mapped to the newer `PWRCTRL` names.

## Important APIs, types, and functions
The symbols are `HAVE_PWRCTRL`, `PCI_PWRCTRL`, `PCI_PWRCTRL_PWRSEQ`, `PCI_PWRCTRL_GENERIC`, and `PCI_PWRCTRL_TC9563`. Deprecated aliases are `HAVE_PWRCTL` and `PCI_PWRCTL_PWRSEQ`. `PCI_PWRCTRL_GENERIC` and `PCI_PWRCTRL_PWRSEQ` select `POWER_SEQUENCING`; `PCI_PWRCTRL_TC9563` selects the core and depends on `I2C`.

## Control flow
There is no runtime control flow. Build configuration selects whether the core object and provider modules are compiled. Selecting a provider also selects the core where needed. `PCI_PWRCTRL_TC9563` defaults to module builds on Qualcomm architectures while still requiring I2C.

## State and persistence
The file contributes build-time state only through Kconfig symbols. Those symbols persist in kernel configuration and determine which objects and module aliases are available.

## Dependencies and integration points
The Kconfig symbols integrate with the pwrctrl Makefile in this directory and with host-controller drivers that include `<linux/pci-pwrctrl.h>`. The generic and pwrseq providers depend on the power sequencing subsystem; the TC9563 provider depends on I2C and regulator/GPIO support in its C file.

## Risks
Because `PCI_PWRCTRL` itself has no prompt, users typically enable it via providers. Missing `POWER_SEQUENCING` or I2C dependencies would produce build or probe gaps, so the select/depends lines are important. Deprecated aliases should not be extended for new code but may be needed for old configs.

## Test signals
Build matrix checks should cover all providers as built-in and modules where valid, `I2C=n` hiding TC9563, and old configs using `PCI_PWRCTL_PWRSEQ` still selecting the modern pwrseq provider. Kconfig dependency tests should verify that provider selection produces the expected objects.
