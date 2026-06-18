<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amba/mmci.h -->
# sources/distributed-fs/ceph-client/include/linux/amba/mmci.h

## Purpose
`amba/mmci.h` declares platform data for the ARM PrimeCell MMCI/PL180 MMC controller.

## Important APIs, types, and functions
`struct mmci_platform_data` contains `ocr_mask`, describing supported voltages, and an optional `status(struct device *)` callback to report card presence when no GPIO line is supplied.

## Control flow
The MMCI driver reads platform data during probe, uses voltage masks unless a regulator supersedes them, and calls `status()` to determine card-detect state when needed.

## State and persistence behavior
The header stores no state. Platform data is persistent device configuration.

## Dependencies and integration points
It depends on MMC host voltage definitions and integrates board/platform data with the AMBA MMCI driver.

## Risks and test signals
Risks include wrong voltage mask, card-detect callback sleeping or returning inverted values, and regulator/platform-data conflicts. Test signals include MMCI probe, card insertion/removal, voltage negotiation, and no-GPIO card-detect paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/amba/mmci.h -->
