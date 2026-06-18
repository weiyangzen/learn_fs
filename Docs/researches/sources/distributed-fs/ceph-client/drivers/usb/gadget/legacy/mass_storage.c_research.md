# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/mass_storage.c

Purpose: legacy `g_mass_storage` composite gadget wrapper for the mass-storage function. It supplies descriptors, module parameters, LUN setup, OTG descriptor handling, and composite registration while leaving SCSI/Bulk-Only transport behavior to `f_mass_storage`.

Important APIs, types, and functions: `msg_device_desc` declares the USB device descriptor; `mod_data` and `FSG_MODULE_PARAMETERS` expose file-backed storage options; `fi_msg` and `f_msg` hold the function instance/function. `msg_bind` obtains the `"mass_storage"` function instance, converts module parameters into `struct fsg_config`, configures common storage buffers, cdev, sysfs, LUNs, inquiry strings, string IDs, and OTG descriptors. `msg_do_config` adds the mass-storage function to the single configuration. `msg_unbind` releases the function, instance, and OTG descriptor.

Control flow: module registration through `module_usb_composite_driver` calls `msg_bind` when a UDC binds. Bind prepares mass-storage common state before calling `usb_add_config`. When the configuration is selected, `msg_do_config` gets a live function from the instance and adds it. Error paths unwind LUNs, buffers, descriptors, and function instances in reverse order.

State and persistence: global static descriptor and function pointers exist for the module lifetime. Runtime LUN/file-backed state lives in the mass-storage common object and is configured from module parameters. No state is persisted by this wrapper.

Dependencies and integration points: depends on libcomposite and `f_mass_storage.h`. The wrapper relies on `fsg_common_set_num_buffers`, `fsg_common_set_cdev`, `fsg_common_create_luns`, `fsg_common_set_sysfs`, and `usb_composite_overwrite_options`. It uses NetChip vendor/product defaults and requires a serial number (`needs_serial = 1`).

Risks: all meaningful media and SCSI risks are in the function core, but this wrapper can leak or double-release if bind partially succeeds and unwind ordering is wrong. Incorrect module parameters can prevent LUN creation. OTG descriptor allocation is global and must be freed on unbind/failure.

Test signals: load with valid backing-file parameters, enumerate `g_mass_storage`, verify descriptors/string overrides, mount/read/write from a host, test missing/invalid LUN parameters, run disconnect/reconnect during I/O, and unload while ensuring LUNs, buffers, and function references are released.
