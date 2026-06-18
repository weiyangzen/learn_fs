## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-privacy.h

Purpose: declares the integration contract between Dell WMI hotkey/event handling and the optional Dell privacy driver.

Important APIs: when `CONFIG_DELL_WMI_PRIVACY` is enabled, the header declares `dell_privacy_has_mic_mute()`, `dell_privacy_process_event(int type, int code, int status)`, `dell_privacy_register_driver()`, and `dell_privacy_unregister_driver()`. When disabled, inline stubs make privacy support compile away: the query and process helpers return `false`, registration returns `0`, and unregister is a no-op.

Control flow and integration: `dell-wmi-base` can unconditionally include this header, register/unregister privacy support, and offer privacy event payloads to `dell_privacy_process_event()` without surrounding all call sites in Kconfig conditionals. Event type/code/status semantics are implemented in the `.c` file.

State and persistence: no state is defined here. The enabled implementation owns runtime WMI device state, supported-feature bits, input devices, and LED class devices.

Dependencies: deliberately minimal; it is a small Kconfig-aware header. The enabled implementation depends on WMI/input/LED/ACPI EC, but consumers only need this declaration layer.

Risks and test signals: disabled builds should still register `dell-wmi-base` and process non-privacy events because stubs are harmless. Enabled builds should verify symbol availability and ordering with `dell-wmi-base`. Build tests should cover `CONFIG_DELL_WMI_PRIVACY=y/m/n`, and runtime tests should verify that privacy events fall through to generic key processing when the privacy driver is absent or declines an event.
