# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-ptp.c

## Purpose
`dpaa2-ptp.c` registers the DPAA2 DPRTC real-time counter as a Linux PTP hardware clock using the shared `ptp_qoriq` engine. It provides the PHC and global pointer consumed by the Ethernet driver for RX/TX hardware timestamping and one-step PTP Sync support.

## Important APIs and functions
The driver matches fsl-mc objects of type `dprtc`. `dpaa2_ptp_caps` supplies the `ptp_clock_info` operations, mostly delegated to `ptp_qoriq` (`adjfine`, `adjtime`, `gettime64`, `settime64`) with local `dpaa2_ptp_enable()` for external timestamp/PPS interrupt masking. `dpaa2_ptp_irq_handler_thread()` converts DPRTC PPS and external timestamp events into PTP clock events or `extts_clean_up()` calls. `dpaa2_ptp_probe()` allocates `struct ptp_qoriq`, opens the DPRTC MC object, maps the `"fsl,dpaa2-ptp"` register range, allocates/request IRQs, enables DPRTC IRQs, initializes the qoriq PHC, and sets global `dpaa2_phc_index` and `dpaa2_ptp`. `dpaa2_ptp_remove()` unregisters/free the PHC and MC resources.

## Control flow
On probe, the MC portal and DPRTC handle are acquired first, then the OF node and MMIO base are found, then IRQ resources are allocated and enabled, and finally `ptp_qoriq_init()` publishes the PHC. IRQ handling reads status, reports PPS, cleans external timestamp channels 0/1, and clears handled bits. Enable/disable operations read the current DPRTC IRQ mask, set or clear the requested event bit, and write it back.

## State and persistence behavior
`dpaa2_ptp` and `dpaa2_phc_index` are global exported state shared with `dpaa2-eth.c` and `dpaa2-ethtool.c`. PHC time and adjustment state live in hardware through `ptp_qoriq`. IRQ masks are MC state. The driver does not persist configuration to disk. Remove resets the exported PHC index to `-1`, frees the PTP clock, closes the DPRTC handle, frees IRQs, and releases the MC portal.

## Dependencies and integration points
The file depends on fsl-mc DPRTC APIs, OF address lookup, threaded IRQ support, and `linux/fsl/ptp_qoriq.h`. Ethernet timestamping checks `dpaa2_ptp` before advertising and using timestamp features; ethtool timestamp info reports `dpaa2_phc_index`.

## Risks and edge cases
The compatible node lookup is global (`of_find_compatible_node(NULL, NULL, "fsl,dpaa2-ptp")`), so multiple DPRTC/PTP nodes would need careful review. Error paths must unmap MMIO and release OF node references; remove relies on `ptp_qoriq_free()` to release resources initialized by `ptp_qoriq_init()`. IRQ status errors return `IRQ_NONE`, while enable errors propagate to PTP core. Ethernet code must tolerate `dpaa2_ptp` being absent or removed.

## Test signals
Validate `/dev/ptp*` registration, `ethtool -T` PHC index on DPAA2 Ethernet, `phc2sys`/`ptp4l` adjustment behavior, PPS and external timestamp enable/disable, IRQ delivery and clear behavior, module remove/reload, and Ethernet TX/RX timestamping when the DPRTC driver is loaded before and after the DPNI driver.
