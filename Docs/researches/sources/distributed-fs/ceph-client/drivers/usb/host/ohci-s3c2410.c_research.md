# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-s3c2410.c

## Purpose

`ohci-s3c2410.c` is Samsung S3C2410 OHCI platform glue. It manages host and bus clocks, platform-data port power, platform overcurrent reporting, and overrides root-hub status/control to expose board-specific power and overcurrent state.

## Important APIs, Types, and Functions

Important functions are `s3c2410_start_hc()`, `s3c2410_stop_hc()`, `ohci_s3c2410_hub_status_data()`, `s3c2410_usb_set_power()`, `ohci_s3c2410_hub_control()`, `s3c2410_hcd_oc()`, `ohci_hcd_s3c2410_probe()`, remove, and PM callbacks. It uses platform data `struct s3c2410_hcd_info`.

## Control Flow

Probe powers both possible ports through platform callbacks, creates and maps the HCD, gets `usb-host` and `usb-bus-host` clocks, gets IRQ, starts clocks, installs overcurrent callbacks in platform data, then calls `usb_add_hcd()`. Module init overrides generic hub status/control callbacks. Hub status ORs platform overcurrent change bits into the root-hub bitmap. Hub control intercepts power and overcurrent feature requests and edits hub descriptors and port status to reflect board capabilities. Overcurrent callback records status/change and powers down affected ports.

## State and Persistence Behavior

State is split between global clock pointers, HCD state, and platform data fields `hcd`, `report_oc`, per-port `power`, `oc_status`, and `oc_changed`. Hardware clock and power state persists until stop or platform callbacks reverse it.

## Dependencies and Integration Points

It depends on Samsung platform data, platform callbacks for power and overcurrent enablement, clocks, platform resources, and generic OHCI core callbacks. It registers platform name `s3c2410-ohci`.

## Risks and Test Signals

Risks include global clock pointers limiting multiple instances, platform-data-only design, direct cast of hub status buffer to `u32 *`, overcurrent state not protected by a normal lock, and port numbering limited to 1 and 2. Test signals include port power callbacks from hub requests, overcurrent interrupt simulation, hub descriptor changes for per-port power/OCPM, suspend/resume clock cycling, and enumeration after overcurrent clear.
