# sources/distributed-fs/ceph-client/drivers/net/dsa/ocelot/Kconfig

## Purpose
This Kconfig file declares the build-time configuration entries for the Ocelot/Felix DSA driver family. It separates the shared Felix DSA library from chip/front-end drivers for external SPI-controlled Ocelot switches, PCIe Felix/VSC9959, and platform Seville/VSC9953.

## Important APIs, Types, and Functions
- `NET_DSA_MSCC_FELIX_DSA_LIB` is a hidden tristate library selected by the concrete drivers. It builds the common Felix DSA glue in `felix.c`.
- `NET_DSA_MSCC_OCELOT_EXT` enables the SPI/MFD external Ocelot switch front end and selects `MFD_OCELOT`, `MDIO_MSCC_MIIM`, the Ocelot switch library, both Ocelot DSA taggers, and the Felix DSA library.
- `NET_DSA_MSCC_FELIX` enables the PCI VSC9959/NXP LS1028A Felix driver and depends on PCI, Microsemi and Freescale vendor options, MMIO, optional PTP, and taprio availability. It selects the shared switch library, Felix library, Ocelot taggers, ENETC MDIO, and Lynx PCS.
- `NET_DSA_MSCC_SEVILLE` enables the VSC9953 Seville platform driver and selects MDIO, Ocelot switch library, Felix library, Ocelot taggers, and Lynx PCS.

## Control Flow
Kconfig has no runtime control flow. Its dependency and select graph controls which objects are compiled and which helper libraries are pulled in when a user enables a specific Ocelot-compatible switch driver.

## State and Persistence Behavior
Configuration state is held in the kernel build configuration. There is no runtime state. Built-in versus module behavior follows the tristate choices and selected dependencies.

## Dependencies and Integration Points
The entries integrate with DSA, the Microsemi/Ocelot switch library, Ocelot DSA taggers, optional PTP clock support, MDIO providers, PCS Lynx, PCI, SPI, MFD Ocelot, and vendor menu symbols. The Felix driver specifically constrains `NET_SCH_TAPRIO` to either enabled or absent in a way that avoids unsupported modular dependency combinations.

## Risks and Edge Cases
- `select` bypasses dependency prompts for selected symbols, so the dependency list must remain accurate for each hardware front end.
- `NET_DSA_MSCC_FELIX_DSA_LIB` is hidden; it should not gain direct user-facing hardware assumptions.
- The taprio dependency for `NET_DSA_MSCC_FELIX` is subtle and important for TSN offloads.
- External Ocelot support is described as SPI-controlled and depends on `MFD_OCELOT`; mismatched device tree/MFD setup will prevent runtime probe even if Kconfig succeeds.

## Test Signals
Build tests should cover all three concrete options as built-in and module where supported, with combinations of `PTP_1588_CLOCK_OPTIONAL` and `NET_SCH_TAPRIO`. Runtime smoke tests should verify that enabling each option builds the expected object and pulls in the correct DSA tagger modules.
