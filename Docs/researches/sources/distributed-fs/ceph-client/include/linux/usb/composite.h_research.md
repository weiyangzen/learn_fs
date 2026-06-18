<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/composite.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/composite.h

Purpose: declares the USB gadget composite framework, which lets gadget drivers combine multiple functions and configurations into one USB device.

Important APIs and types: OS descriptor types include `usb_os_desc_ext_prop`, `usb_os_desc`, and `usb_os_desc_table`. `struct usb_function` defines per-function descriptors, OS descriptors, bind/unbind/free hooks, altsetting, setup, suspend/resume, status, and function-suspend callbacks plus endpoint bitmap and instance link. `struct usb_configuration` groups functions and descriptor metadata. `struct usb_composite_driver` wraps device descriptor template, strings, max speed, bind/unbind/disconnect/suspend/resume hooks, and `usb_gadget_driver`. `struct usb_composite_dev` stores the gadget, EP0 requests, active config, OS/WebUSB metadata, descriptor/string state, deactivation and delayed-status counters, and setup-pending flags. Function-driver/configfs APIs include function registration, get/put instance/function, add/remove function/config, string ID allocation, descriptor overwrite options, and module helper macros.

Control flow: a composite driver registers, bind allocates strings/configurations/functions, functions bind and autoconfigure endpoints, the gadget handles EP0 setup by dispatching standard/config/function requests, and host set-configuration/set-interface calls activate or disable functions. Delayed status lets functions pause control completion until ready. Configfs function drivers allocate instances and functions dynamically.

State and persistence: runtime state includes active configuration, function lists, endpoint allocations, string IDs, OS/WebUSB descriptor buffers, deactivation count, delayed status count, and configfs instance objects. Module parameters can override descriptor IDs/strings at load time; no long-term persistent storage is managed.

Dependencies and integration points: depends on USB gadget API, chapter 9 descriptors, WebUSB, configfs, bcd/version helpers, and module infrastructure. It is the main integration layer for gadget functions such as HID, mass storage, CDC, FunctionFS, and configfs-composed gadgets.

Risks and test signals: risks include EP0 delayed-status leaks, function bind/unbind lifetime errors, string/interface ID exhaustion, endpoint autoconfig mismatch across speeds, OS/WebUSB descriptor bounds, configfs reference leaks, and suspend/resume ordering across functions. Test gadget enumeration at full/high/super speeds, multi-function configs, set_alt reset semantics, delayed setup continuation, configfs create/remove, module parameter overrides, and disconnect during active requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/composite.h -->
