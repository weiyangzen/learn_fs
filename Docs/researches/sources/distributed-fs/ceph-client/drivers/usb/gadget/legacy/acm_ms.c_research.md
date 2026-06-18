# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/acm_ms.c

## Purpose

`acm_ms.c` implements the legacy `g_acm_ms` composite gadget: one configuration containing CDC ACM serial and mass storage functions.

## Important APIs, Types, and Functions

Key functions are `acm_ms_bind()`, `acm_ms_do_config()`, and `acm_ms_unbind()`. The driver uses `usb_get_function_instance("acm")`, `usb_get_function_instance("mass_storage")`, `usb_get_function()`, `usb_add_function()`, and mass-storage helpers such as `fsg_config_from_params()`, `fsg_common_set_num_buffers()`, `fsg_common_set_cdev()`, `fsg_common_create_luns()`, and `fsg_common_set_inquiry_string()`.

## Control Flow

Bind obtains ACM and mass-storage function instances, configures mass-storage options from module parameters, allocates string IDs, optionally allocates an OTG descriptor, and registers one USB configuration. The configuration callback obtains concrete ACM and mass-storage functions and adds them in order, unwinding on failures. Unbind drops functions and instances and frees the OTG descriptor.

## State and Persistence Behavior

Global state includes `f_acm_inst`, `f_acm`, `fi_msg`, `f_msg`, `otg_desc`, device descriptor strings, and mass-storage module parameters. LUN and backing-storage state is owned by the mass-storage common layer. Runtime state is not persisted by this file.

## Dependencies and Integration Points

The file depends on libcomposite, `u_serial`, `f_mass_storage`, module parameters from `FSG_MODULE_PARAMETERS`, gadget OTG helpers, and composite overwrite options. Host-visible integration is through Linux Foundation ACM+MS vendor/product IDs, dynamic strings, and a self-powered configuration.

## Risks and Test Signals

Risks include incomplete error unwind for partially created mass-storage resources, stale global function pointers across bind failure, OTG descriptor lifetime, and module parameters producing invalid LUN setup. Tests should load with valid and invalid backing files, enumerate at full/high/super speed, verify both ACM and storage interfaces, test OTG-capable controllers, and unload after failed bind paths.
