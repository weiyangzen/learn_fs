## sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/tsnep_ptp.c

## Purpose
Provides PTP hardware clock registration and timestamp configuration for TSNEP. It exposes the MAC system time/counter to the kernel PTP layer and stores netdev hardware timestamp policy used by the main TX/RX paths.

## Important APIs, Types, and Functions
Exports `tsnep_get_system_time`, `tsnep_ptp_hwtstamp_get`, `tsnep_ptp_hwtstamp_set`, `tsnep_ptp_init`, and `tsnep_ptp_cleanup`. Internal PTP ops are `tsnep_ptp_adjfine`, `tsnep_ptp_adjtime`, `tsnep_ptp_gettimex64`, `tsnep_ptp_settime64`, and `tsnep_ptp_getcyclesx64`. State lives in `adapter->hwtstamp_config`, `ptp_clock_info`, `ptp_clock`, and `ptp_lock`.

## Control Flow and State
`tsnep_get_system_time` reads the high 32-bit register before and after the low register to avoid rollover tearing. HWTSTAMP set accepts TX off/on and normalizes every supported RX timestamping request to `HWTSTAMP_FILTER_ALL`, rejecting unsupported modes with `-ERANGE`. PTP init initializes default timestamping off, fills `ptp_clock_info`, initializes the spinlock, and registers the PHC. Time adjustment and setting write high then low so hardware commits synchronously when the low word is written.

## Dependencies and Integration Points
Depends on TSNEP MMIO time registers, kernel PTP clock APIs, net timestamp config APIs, and `tsnep_main.c` for TX/RX timestamp consumption. RX timestamps are passed through inline metadata in SKBs, and TX completion reads descriptor writeback timestamp/counter based on socket timestamp flags.

## Risks and Test Signals
Risks include assuming an 8 ns clock cycle in `adjfine`, lack of validation for hardware clock period, unsynchronized `hwtstamp_config` reads from data paths, and missed rollover if register semantics differ from the high-low-high pattern. Test with `ethtool -T`, `phc2sys`, `ptp4l`, `hwstamp_ctl`, TX timestamp sockets with and without bound PHC, RX timestamp filters, adjfine/adjtime stress, and remove/unregister cleanup.
