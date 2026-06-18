# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_port.h

## Purpose
Defines the public FMan port API and frame-error constants used by DPAA Ethernet MAC/netdev code to configure and operate FMan Rx and Tx ports.

## Important APIs, Types, and Functions
The header maps FMan frame descriptor error bits to `FM_PORT_FRM_ERR_*` constants, forward declares `struct fman_port`, and defines `fman_port_rx_params`, `fman_port_non_rx_params`, `fman_port_specific_params`, and `fman_port_params`. It declares the exported lifecycle and utility APIs implemented in `fman_port.c`: config, init, buffer-prefix configuration, enable/disable, hash/timestamp accessors, QMan channel lookup, device lookup, KeyGen hash selection, and device binding.

## Control Flow and State
There is no runtime control flow in this header. Its state model is the contract between consumers and `fman_port.c`: callers supply queue IDs and external buffer pools through `fman_port_params`, then call config/init before runtime enable/disable or metadata offset access. Error constants describe persistent status bits reported by hardware frame descriptors.

## Dependencies and Integration Points
Includes `fman.h` for FMan types, frame descriptor error definitions, buffer pool structures, and prefix content structures. It is consumed by `mac.h`, DPAA Ethernet code, FMan MAC initialization code, and any module binding platform FMan port devices.

## Risks and Test Signals
Risks are ABI-style: changing error masks, parameter structure layout, or function prototypes breaks DPAA users or misclassifies hardware frame errors. Test signals are build coverage of FMan MAC and Ethernet modules, compile checks for all exported prototypes, and runtime validation that Rx error queue/discard behavior matches descriptor status bits.
