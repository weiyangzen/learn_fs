## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-sysman/dell-wmi-sysman.h

Purpose: central shared header for the Dell WMI System Management module. It defines WMI GUIDs, shared data structures, attribute constants, helper macros, and cross-object function prototypes.

Important APIs/types: `struct wmi_sysman_priv` is the module-global state: current admin/system passwords, WMI device pointers, firmware-attributes class device, ksets, per-type attribute arrays/counts, pending-change flag, and mutex. `struct enumeration_data`, `integer_data`, `str_data`, and `po_data` cache firmware metadata. GUID macros identify enumeration, integer, string, password-object, BIOS-attributes, and password-interface WMI blocks. Macros such as `get_instance_id`, `attribute_s_property_show`, `attribute_n_property_show`, and `attribute_property_store` generate repeated sysfs handlers.

Control flow and integration: each attribute implementation includes this header to allocate/populate its metadata array, validate writes, and create sysfs groups. `sysman.c` owns init/exit and WMI object enumeration. `biosattr-interface.c` and `passwordattr-interface.c` implement write methods declared here.

State and persistence: the header declares but does not allocate `wmi_priv`. It documents global password buffers and pending-change state, which persist for the module lifetime and are not scrubbed on exit in the declarations themselves.

Dependencies: Linux WMI, device, module, kernel, and capability headers, plus the local firmware-attributes class in implementation files.

Risks and test signals: generated macros rely on naming conventions such as `wmi_priv.type##_data` and `validate_##type##_input()`. Off-by-one risk exists in generated `get_instance_id()` loops because it uses `<= count`. Build coverage across all objects is essential. Runtime tests should exercise every attribute type, absent GUIDs, duplicate attribute names, long strings bounded by `MAX_BUFF`, and password state.
