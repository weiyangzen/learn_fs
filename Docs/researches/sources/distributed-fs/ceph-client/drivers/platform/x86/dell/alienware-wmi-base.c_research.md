# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/alienware-wmi-base.c

Purpose: Common Alienware WMI core. It selects DMI quirks, chooses legacy or WMAX backend, registers the shared platform driver, and exposes AlienFX global brightness plus RGB zone sysfs.

Important APIs/types/functions: Global `alienfx` and `alienware_interface`; `alienware_wmi_command()` WMI wrapper; zone sysfs handlers; LED class `global_led_set/get`; `alienfx_probe()`; `alienware_alienfx_setup()`.

Control flow/state/persistence: Init loads DMI quirks, registers the platform driver, and initializes WMAX if its GUID exists, otherwise legacy. Backend probes register an `alienware-wmi` platform device with backend-specific update operations. State lives in `alienfx_priv` and is sent to firmware on writes; it is not persisted by the driver.

Dependencies/integration: DMI, ACPI WMI, platform devices, LED class, and WMAX attribute groups when compiled.

Risks/test signals: RGB parsing/repacking and zone visibility are hardware-sensitive. Test DMI fallback, backend selection, each RGB zone, global brightness, lighting state, and cleanup when backend init fails.
