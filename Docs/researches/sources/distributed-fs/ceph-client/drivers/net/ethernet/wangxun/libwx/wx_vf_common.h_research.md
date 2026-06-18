# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_vf_common.h

## Purpose
`wx_vf_common.h` declares the shared VF lifecycle, netdev operation helpers, and service hooks implemented by `wx_vf_common.c`.

## Important APIs, Types, and Functions
Declarations cover PCI PM/remove/shutdown (`wxvf_suspend`, `wxvf_shutdown`, `wxvf_resume`, `wxvf_remove`), interrupt setup (`wx_request_msix_irqs_vf`), mailbox/reset/configuration (`wx_negotiate_api_vf`, `wx_reset_vf`, `wx_set_rx_mode_vf`, `wx_configure_vf`), netdev operations (`wx_set_mac_vf`, `wxvf_open`, `wxvf_close`), link service (`wxvf_watchdog_update_link`), and service initialization (`wxvf_init_service`).

## Control Flow
There is no executable flow. Concrete VF drivers wire these helpers into `net_device_ops`, PCI PM ops, shutdown, and remove handlers.

## State and Persistence Behavior
No state is declared here. The functions operate on runtime `struct wx`, `struct pci_dev`, `struct device`, and `struct net_device` state.

## Dependencies and Integration Points
The header integrates concrete VF modules such as `ngbevf` with shared libwx VF behavior. It relies on including files to provide type declarations for kernel PCI, device, and netdevice structures plus `struct wx`.

## Risks and Edge Cases
Any signature mismatch between this header and exported implementation breaks all VF modules. Adding a new VF lifecycle behavior requires keeping concrete driver netdev/PCI hooks synchronized with the shared API.

## Test Signals
Build `ngbevf` with this header and verify all netdev ops and PM hooks resolve. Probe/remove and suspend/resume tests should cover each declared entry point.
