# sources/distributed-fs/ceph-client/drivers/ntb/hw/mscc/Kconfig

Purpose: Adds the MicroSemi Switchtec NTB hardware driver configuration option.

Important APIs, types, and functions: Declares `config NTB_SWITCHTEC` as a tristate named "MicroSemi Switchtec Non-Transparent Bridge Support". It selects `PCI_SW_SWITCHTEC` because the NTB driver shares hardware interface access with the Switchtec management driver.

Control flow: Build-time only. Selecting the symbol enables the Switchtec NTB object through the MSCC Makefile and pulls in the management driver dependency.

State and persistence behavior: The Kconfig value persists in kernel configuration and controls whether `ntb_hw_switchtec.o` is built.

Dependencies and integration points: Integrates with the Switchtec PCI switch management subsystem via `select PCI_SW_SWITCHTEC` and with the NTB hardware subtree through the local Makefile.

Risks and edge cases: `select` forces `PCI_SW_SWITCHTEC` without exposing a prompt dependency here, so dependency correctness relies on the selected symbol's own constraints. Misconfiguration can affect both NTB and management-driver interfaces because they share hardware access.

Test signals: Kconfig `m/y/n` builds, verifying `PCI_SW_SWITCHTEC` is selected, and module load testing with Switchtec hardware are the key signals.
