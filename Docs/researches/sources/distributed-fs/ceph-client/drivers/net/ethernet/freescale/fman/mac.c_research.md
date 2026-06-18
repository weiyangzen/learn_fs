# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/mac.c

## Purpose
Implements the generic FMan MAC platform driver. It binds FMan MAC DT nodes to the parent FMan device and two FMan ports, dispatches to the selected MAC backend (dTSEC, TGEC, or MEMAC), and creates the child `dpaa-ethernet` platform device consumed by the DPAA Ethernet netdev driver.

## Important APIs, Types, and Functions
Defines `struct mac_priv_s` for FMan pointer, cell index, speed, and child Ethernet device. The OF match table maps `fsl,fman-dtsec`, `fsl,fman-xgec`, and `fsl,fman-memac` to backend initialization functions. Important functions are `mac_probe`, `mac_remove`, `dpaa_eth_add_device`, and `mac_exception`.

## Control Flow and State
Probe allocates `mac_device` and private state, finds and binds the parent FMan, requests and maps the MAC register resource from the FMan memory region, checks node availability, reads MAC `cell-index` and address, resolves exactly two `fsl,fman-ports` phandles, binds each FMan port, reads PHY mode with SGMII fallback, prepares `fman_mac_params`, calls the backend initializer, logs the address, and registers a `dpaa-ethernet` child with `dpaa_eth_data`. Remove drops port/FMan references and unregisters the child. Child device numbering is serialized by `eth_lock`.

## Dependencies and Integration Points
Depends on OF/platform/resource APIs, FMan core binding, `fman_port_bind`, backend initializers from `fman_dtsec`, `fman_tgec`, and `fman_memac`, phylink interface modes, and DPAA Ethernet's `dpaa_eth_data` contract. Exceptions from backends route through `mac_exception`; RX FIFO overflow is masked after first report.

## Risks and Test Signals
Risks include reference imbalance on probe error paths, missing or wrong number of port phandles, backend init failures after resources are bound, child platform device registration failures, and DT compatibility/PHY mode mismatches. Test signals include probe/remove with each MAC compatible, valid child `dpaa-ethernet` creation, correct MAC address reporting, phylink mode propagation, and leak/error-path checks around failed FMan or port binding.
