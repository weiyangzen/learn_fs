# sources/distributed-fs/ceph-client/drivers/pci/controller/plda/pcie-starfive.c

## Purpose
Implements the StarFive JH7110 PCIe host controller by adapting the shared PLDA host layer to JH7110 clocks, resets, PHY, syscon registers, PERST GPIO, optional regulator, root-port quirks, link polling, and suspend/resume.

## Important APIs, Types, And Functions
Main state is `struct starfive_jh7110_pcie`, embedding `struct plda_pcie_rp`. Key functions are `starfive_pcie_probe()`, `starfive_pcie_parse_dt()`, `starfive_pcie_host_init()`, `starfive_pcie_host_deinit()`, `starfive_pcie_enable_phy()`, `starfive_pcie_clk_rst_init()`, `starfive_pcie_host_wait_for_link()`, and config-space wrappers that hide root-complex BAR0/BAR1.

## Control Flow
Probe allocates state, parses DT resources and domain number, enables runtime PM, installs StarFive host ops, configures an event bitmap that masks doorbell events, and calls `plda_pcie_host_init()`. The platform host init powers the PHY, programs syscon root-port/non-endpoint and clock-request fields, enables clocks/resets/regulator, asserts and deasserts PERST with PCIe timing waits, disables physical functions 1-3, enables root-port mode, clears RC BAR, sets class code, disables LTR forwarding, enables 64-bit prefetchable windows, and polls link.

## State And Persistence
Driver state holds syscon base selection from static PCI domain, reset and clock handles, PHY, regulator, PERST GPIO, and PLDA state. Hardware state persists in syscon AR/AW/RP/LNKSTA fields, PLDA bridge registers, ATR windows, interrupt masks, and downstream reset state.

## Dependencies And Integration Points
Depends on device tree, `starfive,stg-syscon`, Linux PHY, reset, clock, regulator, GPIO, runtime PM, PLDA common host helpers, and PCI generic config access. It registers as `starfive,jh7110-pcie`.

## Risks
Domain number is used to choose syscon offsets and must match DTS. `starfive_pcie_host_deinit()` calls PHY disable unconditionally, so optional PHY lifetime assumptions matter. Regulator enable failure is logged but not returned. Suspend/resume only handles PHY and clocks, relying on preserved PLDA/root-port state.

## Test Signals
Useful tests include JH7110 boot on both PCIe domains, endpoint enumeration after PERST timing, hidden RC BAR reads returning zero, MSI/INTx delivery through PLDA, link-down boot, suspend/resume with devices present, and remove path resource cleanup.
