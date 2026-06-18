# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/thunder/thunder_xcv.c

## Purpose
`thunder_xcv.c` is the Thunder RGX/XCV companion PCI driver. It owns a small global XCV register block used by RGX LMAC support to initialize the XCV hardware and to adjust link datapath state when RGMII/RGX link status changes.

## Important APIs, Types, and Functions
The file defines XCV register offsets and bit masks, `struct xcv`, a single global `static struct xcv *xcv`, and exports `xcv_init_hw` and `xcv_setup_link`. PCI lifecycle functions are `xcv_probe`, `xcv_remove`, `xcv_init_module`, and `xcv_cleanup_module`.

## Control Flow and Integration
`xcv_probe` allocates the global XCV state, enables the PCI device, requests regions, maps the config BAR, and leaves the block ready for BGX/RGX code. `xcv_init_hw` takes DLL and clock trees out of reset, configures DLL bypass, enables the compensation controller, waits for lock, enables the port, and finally manipulates clock reset. `xcv_setup_link` maps link speed to hardware speed encoding, programs `XCV_CTL`, resets TX/RX datapaths, enables packet flow and returns credits on link up, or disables packet flow on link down. `thunder_bgx.c` calls these APIs for RGX devices.

## State and Persistence
The only software state is the global `xcv` pointer containing mapped MMIO base and PCI device. Hardware state is held in XCV reset/control/credit registers until reset or driver removal. There is no disk persistence.

## Dependencies and Risks
The file depends on PCI, MMIO accessors, sleeps during hardware bring-up, and `thunder_bgx.h` for exported prototypes. Risks include the singleton design, no locking around exported calls, `xcv_init_hw` assuming `xcv` is non-NULL when called by RGX probe, probe/remove lifetime ordering between BGX and XCV modules, and limited validation of link speeds outside 10/100/1000 defaults.

## Test Signals
Test signals include successful XCV PCI probe/remove, RGX BGX probe calling `xcv_init_hw`, link up/down transitions at 10/100/1000 Mbps, packet credit return behavior, module unload ordering, and fault injection where `pcim_iomap` or region requests fail.
