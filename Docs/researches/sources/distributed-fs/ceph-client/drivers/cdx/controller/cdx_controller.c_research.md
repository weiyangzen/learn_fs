# sources/distributed-fs/ceph-client/drivers/cdx/controller/cdx_controller.c

## Purpose
This file is the AMD/Xilinx Versal-Net CDX platform controller driver. It connects the CDX bus core to firmware operations implemented through the MCDI RPC engine over RPMsg.

## Important APIs, Types, and Functions
The platform driver is `cdx_pdriver`, matching `xlnx,versal-net-cdx`. CDX controller callbacks are `cdx_bus_enable()`, `cdx_bus_disable()`, `cdx_scan_devices()`, and `cdx_configure_device()`, collected in `cdx_ops`. RPMsg lifecycle hooks exposed to `cdx_rpmsg.c` are `cdx_rpmsg_post_probe()` and `cdx_rpmsg_pre_remove()`.

## Control Flow
`xlnx_cdx_probe()` allocates `struct cdx_mcdi`, initializes MCDI state, allocates `struct cdx_controller`, attaches CDX ops and private MCDI state, creates an MSI domain, then calls `cdx_setup_rpmsg()`. Once the RPMsg endpoint appears, `cdx_rpmsg_post_probe()` registers the controller with the bus core, which triggers scanning.

Scanning asks firmware for the number of CDX buses, adds each bus with `cdx_bus_add()`, asks firmware for each bus's device count, fetches each device config, fills `cdx_dev_params`, and calls `cdx_device_add()`. Device configuration requests from the bus are switched by type into MCDI helpers for MSI writes, device reset, bus mastering, or MSI enable.

## State and Persistence Behavior
The controller stores MCDI state in `cdx->priv`, the platform device in `cdx->dev`, ops in `cdx->ops`, and optionally `msi_domain`. Firmware topology is not cached here beyond bus/device objects created by the bus layer.

## Dependencies and Integration Points
It depends on platform devices, OF matching, irq domains, the CDX bus core, RPMsg setup/teardown, and MCDI helper functions. It imports `CDX_BUS_CONTROLLER` namespace symbols.

## Risks
Probe treats missing MSI domain as fatal even though some bus code has conditional MSI handling; this is correct only if hardware requires MSI. `cdx_scan_devices()` continues on per-bus/per-device failures, producing partial topology. RPMsg post-probe is asynchronous, so remove must unregister the controller and wait for MCDI quiescence before tearing down transport. Firmware RPC errors directly affect sysfs reset/enable/MSI operations.

## Test Signals
Probe on a device-tree node with valid `xlnx,rproc` and `msi-map`, verify RPMsg channel creation, controller registration, bus/device enumeration, partial failure logging, reset/bus-master/MSI sysfs actions, and clean remove with no outstanding MCDI commands.
