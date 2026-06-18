# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/cdc2.c

## Purpose

`cdc2.c` implements the legacy `g_cdc` composite gadget with CDC ECM ethernet and CDC ACM serial in one configuration.

## Important APIs, Types, and Functions

Core functions are `cdc_bind()`, `cdc_do_config()`, and `cdc_unbind()`. It uses `can_support_ecm()`, `usb_get_function_instance("ecm")`, `usb_get_function_instance("acm")`, ethernet option helpers (`gether_set_qmult()`, `gether_set_host_addr()`, `gether_set_dev_addr()`), string ID assignment, and `usb_add_config()`.

## Control Flow

Bind rejects controllers that cannot support ECM, obtains ECM and ACM function instances, applies ethernet module parameters to the ECM network device, allocates string IDs, optionally creates an OTG descriptor, and registers one configuration. The configuration callback adds ECM first and ACM second, unwinding any partially added function on failure. Unbind releases functions, instances, and the OTG descriptor.

## State and Persistence Behavior

Global state includes ECM/ACM function instances and concrete functions, OTG descriptor storage, static descriptors, and ethernet module parameters. Network device state is owned by the ECM/gether layer. No runtime state is persisted by this file.

## Dependencies and Integration Points

It depends on libcomposite, `u_ether`, `u_serial`, `u_ecm`, the networking stack, and gadget OTG support. It exposes a NetChip CDC composite vendor/product ID and integrates with host CDC ECM and ACM drivers.

## Risks and Test Signals

Risks include ECM capability checks differing by UDC, ethernet address parameter validation, cleanup asymmetry on partial config-add failures, and host compatibility when descriptors or class values change. Tests should enumerate on ECM-capable and incapable controllers, verify host sees both network and serial interfaces, pass custom MAC addresses, exercise OTG descriptors, and unload after network traffic and serial I/O.
