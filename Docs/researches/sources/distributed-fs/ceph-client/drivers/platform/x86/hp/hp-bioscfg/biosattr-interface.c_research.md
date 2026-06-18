# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/biosattr-interface.c

Purpose: implements the HP BIOS WMI command interface used by hp-bioscfg to set BIOS attributes and perform secure/platform queries.

Important APIs/types/functions: `struct bios_args` is the flexible WMI input packet. `hp_set_attribute()` builds a UTF-16 attribute-name/value/security buffer and calls `hp_wmi_set_bios_setting()`. `hp_wmi_perform_query()` wraps `wmi_evaluate_method()` for `HP_WMI_BIOS_GUID`, validates returned ACPI buffers, copies output, and maps firmware return codes. `hp_ascii_to_utf16_unicode()` encodes strings with HP length prefixes. `hp_wmi_set_bios_setting()` invokes `HP_WMI_SET_BIOS_SETTING_GUID`. A small `wmi_driver` binds the BIOS GUID.

Control flow: sysfs stores in typed attribute files eventually call `hp_set_attribute()`. That function selects either SPM auth token or setup password, computes buffer sizes, appends UTF-16 strings plus security data, and sends the set command under `bioscfg_drv.mutex`. Generic secure queries allocate an input packet sized to `insize`, select the WMI method ID by output size, and free ACPI output and packet storage after translating errors.

State and persistence: firmware updates persist in BIOS, while credentials in memory are temporary and usually cleared by callers after store attempts. This file only registers/unregisters a WMI driver and uses the shared global driver state.

Dependencies and integration: depends on ACPI WMI, NLS UTF conversion, `spmobj-attributes.c` for security buffer helpers, and password data for setup credentials.

Risks: buffer sizing is security-sensitive; `kmalloc(buffer_size + 1)` allocates byte count for a `u16 *` buffer plus one odd byte, so reviewers should confirm all sizes are byte sizes. Test signals include mocked WMI return-code mapping, UTF-16 conversion of empty/nonempty strings, credential selection, and failure cleanup on malformed ACPI objects.
