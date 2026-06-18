# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/dev.c

Purpose: manages each downstream vHub port as an independent `usb_gadget` UDC.

Important APIs, types, and functions: `ast_vhub_init_dev` creates a port device, initializes EP0, allocates per-port endpoint pointer array, populates `usb_gadget`, and calls `usb_add_gadget_udc`. `ast_vhub_del_dev` unregisters it. `ast_vhub_dev_irq`, `ast_vhub_dev_enable`, and `ast_vhub_dev_disable` handle per-port hardware interrupts and enable state. `ast_vhub_std_dev_request` handles standard device/endpoint requests before delegating to the gadget driver. UDC ops include `ast_vhub_udc_start`, `ast_vhub_udc_stop`, `ast_vhub_udc_pullup`, `ast_vhub_udc_wakeup`, `ast_vhub_udc_get_frame`, and `ast_vhub_udc_match_ep`.

Control flow: init registers each port as a separate UDC under a unique child device. A gadget driver start only stores the driver and self-powered flag; the virtual hub later enables the port on reset/connect. Standard requests handle address, status, remote wakeup, test mode, and endpoint halt state; unknown requests return `std_req_driver` for EP0 forwarding. Reset either enables a disabled port or calls `usb_gadget_udc_reset`, disables hardware, and re-enables it. Endpoint matching first reuses existing endpoints, then allocates a generic endpoint from the shared pool with a unique address.

State and persistence: `struct ast_vhub_dev` tracks driver, enabled/registered flags, wakeup enable, speed, per-port EP0, and endpoint mappings. State is protected by `vhub->lock`. No persistent data exists.

Dependencies and integration points: integrates with gadget UDC core, hub emulation (`ast_vhub_device_connect`, wake functions), EP0 handling, and generic endpoint allocation from `epn.c`. It uses USB standard request constants and HCD-visible frame register state.

Risks: endpoint allocation must avoid overlapping IN/OUT numbers because hardware cannot support generic duplicate addresses. Standard request handling must not incorrectly stall class/vendor traffic. Pullup disables hardware and nukes requests, so active gadget drivers must tolerate shutdown callbacks. Lock dropping around gadget driver callbacks must preserve object lifetime.

Test signals: register multiple gadgets on vHub ports, connect/disconnect via pullup, issue standard GET_STATUS/SET_ADDRESS/FEATURE requests, allocate endpoints of all supported types, test endpoint halt clear/set, suspend/resume callbacks, remote wakeup enable and trigger, reset during active transfers, and unregister ports during driver removal.
