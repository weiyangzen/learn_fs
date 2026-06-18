# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-ptp.h

## Purpose
`dpaa2-ptp.h` is the small shared declaration header for the DPAA2 DPRTC PTP clock driver. It exposes DPRTC command headers and the global PHC state used by DPAA2 Ethernet timestamping.

## Important APIs and types
The header includes `linux/fsl/ptp_qoriq.h`, `dprtc.h`, and `dprtc-cmd.h`. It declares `extern int dpaa2_phc_index` and `extern struct ptp_qoriq *dpaa2_ptp`, both defined/exported by `dpaa2-ptp.c` and also declared in `dpaa2-eth.h` for Ethernet users.

## Control flow and integration
There is no executable logic in this file. It exists so the PTP driver can use DPRTC APIs and so other DPAA2 files can refer to the shared PHC pointer/index. Ethernet code checks `dpaa2_ptp` before enabling timestamping and uses the pointer's `caps.gettime64()` path for one-step timestamp updates.

## State and persistence behavior
The state declared here is global in-kernel runtime state. `dpaa2_phc_index` is set to the registered PHC index or `-1`; `dpaa2_ptp` points at the live qoriq clock object while the DPRTC driver is bound.

## Dependencies
Consumers depend on the qoriq PTP core and DPRTC MC command definitions. The include guard is named `__RTC_H`, which is generic and could collide with another header guard in a larger include context.

## Risks and edge cases
Because the globals are shared without explicit locking in this header, users must handle `NULL` and driver ordering. A future change that supports multiple DPRTC clocks would need to replace these singletons with per-device association.

## Test signals
Build with Ethernet timestamping users, load/unload the DPRTC driver around active DPNI interfaces, and verify timestamp-capability reporting falls back cleanly when `dpaa2_ptp` is absent.
