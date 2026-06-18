# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/tcm_usb_gadget.c

Purpose: legacy `g_target` USB target gadget wrapper connecting the USB TCM/UAS function with the Linux target fabric attachment model.

Important APIs, types, and functions: `usbg_device_desc`, `usbg_us_strings`, and `usbg_config_driver` define the composite descriptor surface. `fi_tcm` and `f_tcm` track the target function. `usb_target_gadget_init` gets the `"tcm"` function instance, configures dependency callbacks in `struct f_tcm_opts`, names the instance `tcm-legacy`, and defers actual composite registration until the target fabric calls `usbg_attach`. `usb_target_bind` assigns string IDs and adds the TCM function via `tcm_do_config`. `usbg_detach` unregisters the composite driver.

Control flow: module init does not immediately bind a UDC; it prepares callbacks so the TCM fabric can attach/detach the USB gadget. Attach probes the composite driver, bind assigns strings and registers a single self-powered configuration, and config bind adds the TCM function. Detach unregisters the composite driver. Exit releases the function instance.

State and persistence: dependency flags and callbacks live in the TCM function options under `dep_lock`. Function object `f_tcm` is released on composite unbind. Storage target state is owned by target-core and the TCM function, not this wrapper.

Dependencies and integration points: depends on libcomposite, `u_tcm`, target core/fabric headers, SCSI constants, and USB storage/UAS protocol support. It bridges target-core configuration to USB gadget enumeration.

Risks: callback registration under `dep_lock` must match target-core expectations. The wrapper only releases `f_tcm` in unbind and `fi_tcm` in module exit, so attach/detach ordering must remain coherent. Target configuration errors can prevent any UDC registration.

Test signals: configure a USB target fabric endpoint, trigger attach, enumerate as `g_target`, verify UAS/BOT behavior from a host, detach and reattach target configuration, unload after detach, and test error handling when the TCM function instance is unavailable.
