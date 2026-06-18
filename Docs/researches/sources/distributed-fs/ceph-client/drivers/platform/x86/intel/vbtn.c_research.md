<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/vbtn.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/vbtn.c

Purpose: ACPI platform driver for Intel Virtual Button devices (`INT33D6`). It reports firmware button events and selected convertible/tablet switch events through input devices while avoiding known broken switch reporting on ordinary laptops.

Important APIs/types/functions: `struct intel_vbtn_priv` stores input devices, feature flags, mutex, dual-accelerometer detection result, and wakeup mode. `intel_vbtn_keymap` maps ACPI event scancodes to power, Windows, volume, and rotation keys. `intel_vbtn_switchmap` maps tablet-mode events and intentionally ignores dock events. `notify_handler()` processes ACPI notifications. `detect_tablet_mode()` evaluates `VGBS` and reports `SW_TABLET_MODE` / `SW_DOCK`. PM hooks manage wake events.

Control flow: probe checks `VBDL` for buttons and an allow-listed `VGBS` path for switches, allocates both input devices regardless of registration state, installs the ACPI notify handler, executes `VBDL` when buttons exist, samples tablet state, and enables device wake. Notifications are serialized by `priv->mutex`, looked up in sparse keymaps, lazily register the switches input device only for accepted systems, handle wakeup mode, and report autorelease events when no usable release scancode exists. Resume refreshes switch state.

State/persistence: runtime state is limited to registered input devices, booleans, and current wakeup mode. Switch state is read from ACPI `VGBS`; no persistent configuration is stored by the driver. `acpi_ec_mark_gpe_for_wake()` changes EC GPE wake marking at probe time.

Dependencies/integration: depends on ACPI, platform bus, Linux input/sparse-keymap, PM wakeup, DMI allow list, and `dual_accel_detect()` from platform/x86 helpers. It complements generic ACPI button handling by skipping button evdev reports during wake handling.

Risks: many firmware implementations misuse `SW_DOCK` and `VGBS`, so switch support is DMI-gated to avoid disabling keyboards/touchpads in userspace. Lazy switch device registration can fail during notify handling. Wakeup mode suppresses key reports by design and can look like missing input if misunderstood.

Test signals: ACPI notify scancodes should produce expected input events; allow-listed convertibles should expose tablet switch state and refresh it on resume; non-allow-listed laptops should not register switches; wake from power/volume events should call `pm_wakeup_hard_event()` without duplicate key reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/vbtn.c -->
