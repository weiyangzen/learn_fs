<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio/mdio-mscc-miim.h -->
# sources/distributed-fs/ceph-client/include/linux/mdio/mdio-mscc-miim.h

## Purpose
This header exposes a setup helper for the Microsemi/Vitesse MIIM MDIO controller used in network switches.

## Important APIs, types, and functions
`mscc_miim_setup()` takes a parent device, output `mii_bus **`, bus name, MIIM regmap, status register offset, and an `ignore_read_errors` policy flag.

## Control flow
Switch or platform drivers call the helper to allocate/configure a `mii_bus` over a regmap-backed MIIM block, then use the returned bus for PHY discovery and MDIO transactions.

## State and persistence
State lives in the returned bus and MIIM hardware registers. The header stores none.

## Dependencies and integration points
It depends on device, phylib, and regmap APIs. It integrates regmap-backed switch management blocks with the MDIO subsystem.

## Risks and test signals
Risks include wrong status offset, suppressed real read errors when `ignore_read_errors` is set, regmap endianness/access-width mismatches, and bus lifetime leaks. Test setup failure, read/write transactions, status polling, ignored-read-error mode, and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio/mdio-mscc-miim.h -->
