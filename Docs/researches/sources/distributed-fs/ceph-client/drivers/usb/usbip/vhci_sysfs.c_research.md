# sources/distributed-fs/ceph-client/drivers/usb/usbip/vhci_sysfs.c

## Purpose

`vhci_sysfs.c` exposes the userspace control plane for the virtual host controller. It reports port status, number of ports, and accepts attach/detach requests that bind established sockets to virtual root-hub ports.

## Important APIs, Types, and Functions

`status_show_vhci()` prints HS and SS port rows with status, speed, remote device ID, socket fd, and local busid. `nports_show()` reports total configured ports. `detach_store()` parses a global port number and queues a down event. `attach_store()` parses `port sockfd devid speed`, validates port/speed, looks up a stream socket, creates VHCI RX/TX kthreads, sets `vhci_device` fields, initializes KCOV, wakes threads, and calls `rh_port_connect()`. `vhci_init_attr_group()` dynamically builds attributes for all controllers.

## Control Flow

VHCI start creates the sysfs group for controller 0. Userspace opens a TCP connection to a USB/IP server, then writes attach arguments. The driver chooses the HS or SS HCD by speed, rejects occupied ports, starts transport threads before publishing state, and triggers root-hub connect. Detach validates and queues event-driven teardown.

## State and Persistence Behavior

Sysfs state reflects runtime `vhci_device` fields. Attached sockets, task pointers, remote IDs, speeds, and port status are in memory only. Dynamic status attribute allocation is tied to module lifetime.

## Dependencies and Integration Points

It depends on platform devices, USB HCD private state, common USB/IP debug attribute, socket fd lookup, kthreads, Spectre-safe `array_index_nospec()`, root-hub connection helper, and VHCI RX/TX loops.

## Risks and Test Signals

Risks include invalid port calculations with multiple controllers, socket fd lifetime, failure after one kthread is created, status output consistency while state changes, and HS/SS port selection mismatch. Test signals include attach with every supported speed, invalid port/speed/fd handling, occupied-port `-EBUSY`, detach active and inactive ports, status output before/after attach, and multi-controller status attributes.
