# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/ncm.c

Purpose: legacy `g_ncm` composite wrapper exporting one CDC NCM Ethernet function.

Important APIs, types, and functions: `device_desc` sets CDC communication class defaults, `strings_dev` supplies dynamic strings, `f_ncm_inst` and `f_ncm` track the NCM function. `gncm_bind` gets the `"ncm"` function instance, programs gether options such as `qmult`, host MAC, and device MAC, assigns string IDs, allocates OTG descriptors, and registers `ncm_config_driver`. `ncm_do_config` gets the function and adds it to the configuration. `gncm_unbind` releases resources.

Control flow: composite bind prepares NCM network options before any configuration is added. When the host selects the single configuration, the NCM function is materialized and attached. OTG-capable gadgets get wakeup attributes and descriptor pointers.

State and persistence: runtime state is global to the module and in the gether network object owned by `struct f_ncm_opts`. MAC/module options are in memory only. No durable state is maintained.

Dependencies and integration points: depends on libcomposite, `u_ether`, and `u_ncm`. It creates a Linux network interface through gether internals and relies on the UDC/composite core for descriptor completion and string override handling.

Risks: failures after function-instance acquisition must release the instance and OTG descriptor. MAC address handling affects host networking identity. Some UDCs or hosts may be sensitive to NCM descriptor correctness and max speed.

Test signals: enumerate as `g_ncm`, inspect CDC NCM descriptors, verify network interface creation, pass traffic in both directions, test configured MAC parameters, exercise disconnect/reconnect, and unload while traffic is active.
