<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_aux_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_aux_regs.h

## Purpose
`pcie_aux_regs.h` defines the Gaudi2 PCIe auxiliary control/status register map. It covers APB timeout, scratch registers, PHY initialization, BAR windows, PCIe command attributes, link/power management, FLR, interrupt controls, diagnostic buses, RAS descriptors, and low-level reset/PHY state.

## Important APIs, types, and functions
The file exports `mmPCIE_AUX_*` address macros only. Notable groups include `SW_GENERAL_PURPOSE_*`, `PHY_INIT`, BAR start/limit registers for BAR0-BAR5, bus-master/memory-space enables, max read request and payload sizing, extended tags, RCB, no-snoop and relaxed-order enables, FLR active/done/interrupt/control registers, LTR and LTSSM controls, system interrupt disable/status, link-up and PM state registers, DBI access registers, diagnostic status buses, CDM/RAS descriptor registers, D-state/PME/L0s/L1/L2 state, PERST, DBI read-only write disable, PHY reset hold, SRIS mode, and bus-master clear interrupt controls.

## Control flow
There is no C flow. Probe and PCIe init code uses these addresses to configure endpoint behavior, BAR decode, link features, and interrupts. Reset and FLR flows poll active/done/status registers. Diagnostic paths read link, PM, APB, and RAS state to explain PCIe failures.

## State and persistence
The hardware persists PCIe endpoint configuration and link/power state until conventional reset, FLR, hot reset, or driver reprogramming. Some fields mirror PCI configuration space while others are Gaudi2-side auxiliary state. Scratch registers may be used by firmware/driver handshakes depending on platform policy.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this map complements `pcie_dbi_regs.h` and `pcie_wrap_regs.h`. It integrates with Linux PCI probe, reset, power management, MSI/MSI-X setup, BAR resource management, and firmware-managed PHY/link sequences.

## Risks and test signals
BAR or command-register mistakes can make MMIO inaccessible or allow unintended host access. FLR/PM sequencing bugs can leave outstanding transactions or stale DBI state. Test signals include stable PCI enumeration, BAR sizing/mapping, link-up checks, FLR completion, MSI/MSI-X delivery, no APB timeout events, and diagnostic status that matches expected link speed/state after suspend/resume or reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pcie_aux_regs.h -->
