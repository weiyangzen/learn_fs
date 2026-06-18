
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/tsa.h

## Purpose
Private/local TSA management header for QE/CPM SoC drivers. It declares the opaque TSA serial handle, serial information shape, and exported helper prototypes used by consumers such as QMC.

## Important APIs, Types, and Functions
- Opaque `struct tsa_serial`.
- `struct tsa_serial_info` exposes Rx/Tx frame-sync rates, bit rates, and assigned time-slot counts.
- Lookup/lifetime helpers: `tsa_serial_get_byphandle()`, `tsa_serial_put()`, `devm_tsa_serial_get_byphandle()`.
- Control/query helpers: `tsa_serial_connect()`, `tsa_serial_disconnect()`, `tsa_serial_get_info()`, and `tsa_serial_get_num()`.

## Control Flow
There is no executable control flow. The header defines the contract implemented by `tsa.c`: consumers acquire a serial from a DT phandle, connect it to TSA, query timing/capacity information, optionally get a QE UCC number, and release it.

## State and Persistence
No state is stored here. State lives in `tsa.c` provider objects and consumer-held serial pointers.

## Dependencies and Integration Points
Includes `linux/types.h` and forward declares `struct device_node` and `struct device` to keep consumers lightweight. It is included by `qmc.c` and likely intended only for this local driver family rather than a public UAPI.

## Risks
Because `struct tsa_serial` is opaque, all consumers must respect provider lifetime helpers. Misusing non-devm lookup without `tsa_serial_put()` leaks the platform device reference.

## Test Signals
Compile coverage for all prototypes, consumer use of devm and non-devm lookup paths, and ABI consistency between this header and exported symbols in `tsa.c`.
