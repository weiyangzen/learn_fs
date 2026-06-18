# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-bcm-sr-pcie.c

Purpose: Exposes Stingray PCIe PHY handles and gates host-controller use according to the hardware PIPEMUX strap; also validates the special PAXC PHY power state.

Important APIs and types: `struct sr_pcie_phy_core` stores PCIe SS base, CDRU and MHB syscon regmaps, detected `pipemux`, and nine PHY records. `pipemux_table[]` maps strap settings to root-complex-enabled core bitmaps. Separate `phy_ops` handle regular PAXB cores and the PAXC core.

Control flow: probe maps the PCIe SS block, looks up `brcm,sr-cdru` and `brcm,sr-mhb`, reads PIPEMUX config or hardware strap, validates it, creates nine PHYs, and registers a custom xlate that returns `args[0]`. Regular PHY init returns success only when the core bit is enabled for root complex in the strap table. PAXC init checks MHB power status bits.

State and persistence: The detected PIPEMUX value is immutable after probe. Hardware strap and MHB power state are external platform state; the driver does not change them.

Dependencies and integration: It depends on syscon regmaps, generic PHY, OF phandle args, and platform compatible `brcm,sr-pcie-phy`. PCIe host drivers use PHY init failure to skip unavailable cores.

Risks and test signals: Strap-table correctness defines which controllers enumerate. `WARN_ON` catches out-of-range xlate args. Test all valid strap values, invalid strap rejection, PAXC powered/unpowered cases, xlate index bounds, and PCIe host behavior when init returns `-ENODEV`.
