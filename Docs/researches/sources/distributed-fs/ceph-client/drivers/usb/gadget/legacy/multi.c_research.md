# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/multi.c

Purpose: legacy `g_multi` composite gadget combining serial ACM, Ethernet (`ecm` and/or `rndis` depending on Kconfig), and mass-storage functions in one or two configurations.

Important APIs, types, and functions: `device_desc`, `strings_dev`, `fsg_mod_data`, and Ethernet module parameters define the exported USB personality. `multi_bind` obtains and configures function instances for ECM, RNDIS, ACM, and mass storage. `rndis_do_config` and `cdc_do_config` add functions in per-configuration order. `rndis_config_register` and `cdc_config_register` register configurations conditionally. `multi_unbind` releases every function/function-instance and frees OTG descriptors.

Control flow: bind first validates ECM support, sets Ethernet queue multiplier and MAC addresses, optionally shares one netdev between ECM and RNDIS, then initializes ACM and mass storage. It allocates string IDs, optional OTG descriptor, and registers RNDIS and/or CDC configurations. At configuration bind time functions are acquired and added in network, serial, storage order. Error labels unwind each completed stage.

State and persistence: module globals track function instances and per-configuration function objects. Mass-storage LUN state is created during bind from module parameters; Ethernet addresses come from module parameters or generated defaults in `u_ether`. No persistent data is stored here.

Dependencies and integration points: depends on libcomposite, `u_serial`, `u_ecm`, `u_rndis`/`rndis` when enabled, `u_ether`, and `f_mass_storage`. It integrates with the Linux network stack through gether helpers and with storage through fsg common helpers. `CONFIG_USB_G_MULTI_CDC` and `CONFIG_USB_G_MULTI_RNDIS` shape the descriptor surface.

Risks: mixed function lifetimes are the main risk. The dual ECM/RNDIS path borrows a net interface, so registration and teardown ordering must be exact. Some hosts are sensitive to function ordering and IAD/device class choices. Partial failure after adding one configuration can leave function references unless all unwind labels remain correct.

Test signals: build all Kconfig variants, enumerate with RNDIS-only, CDC-only, and dual configurations, verify MAC address module parameters, run network traffic and serial console while copying to mass storage, switch configurations on the host, test bind failure injection around LUN and OTG allocation, and unload after active network/storage use.
