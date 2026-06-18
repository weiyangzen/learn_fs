# sources/distributed-fs/ceph-client/drivers/usb/usbip/vhci_hcd.c

## Purpose

`vhci_hcd.c` implements the USB/IP virtual host controller. It registers paired USB2/USB3 HCDs, emulates root-hub status/control, queues local URBs for remote submission, handles local unlink requests, and owns virtual-device teardown/reset state.

## Important APIs, Types, and Functions

Root-hub functions are `rh_port_connect()`, `rh_port_disconnect()`, `vhci_hub_status()`, and `vhci_hub_control()`. HCD operations include `vhci_urb_enqueue()`, `vhci_urb_dequeue()`, `vhci_setup()`, `vhci_start()`, `vhci_stop()`, suspend/resume callbacks, and stream stubs. Connection event callbacks are `vhci_shutdown_connection()`, `vhci_device_reset()`, and `vhci_device_unusable()`. Platform lifecycle is managed by `vhci_hcd_probe()`, `vhci_hcd_remove()`, `vhci_hcd_init()`, and `vhci_hcd_exit()`.

## Control Flow

Module init registers a platform driver and creates one platform device per configured controller. Probe creates a primary USB2 HCD and shared USB3 HCD. Sysfs attach later sets `vhci_device` state and calls `rh_port_connect()`, causing USB enumeration. Enqueued URBs are linked to the HCD endpoint, assigned a sequence in `vhci_tx_urb()`, and sent by `vhci_tx.c`. Local dequeue either gives back immediately if disconnected or queues a remote unlink request. Event shutdown kills transport threads, closes socket, cleans unlink lists, and disconnects the root-hub port.

## State and Persistence Behavior

Port status arrays emulate hardware root-hub registers. Each virtual device tracks remote ID, speed, socket/tasks, URB lists, and status. This is runtime-only; attach state is lost on module unload or detach.

## Dependencies and Integration Points

It integrates with USB HCD core, platform bus, USB/IP common/event helpers, VHCI sysfs/RX/TX files, PM callbacks, root-hub polling, and kernel sockets via event teardown.

## Risks and Test Signals

Risks include root-hub feature emulation gaps, invalid port indexes, set-address/get-descriptor enumeration assumptions, URB/unlink races, sequence wrap, suspend with active remote devices, and cleanup ordering between HCD removal and event work. Test signals include HS/SS attach enumeration, hub control requests, URB enqueue/dequeue, remote disconnect, local unlink races, suspend refusal with active ports, and multi-controller startup/shutdown.
