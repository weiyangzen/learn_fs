<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/Kconfig

Purpose: defines Lenovo platform/x86 driver configuration options for IdeaPad, ThinkPad, Yoga, and Lenovo WMI extras. It gates each driver on the required kernel subsystems and selects shared support such as sparse keymaps, LEDs, platform profile, hwmon, firmware attributes, and WMI helper modules.

Important symbols: `IDEAPAD_LAPTOP` depends on ACPI, ACPI battery, rfkill/input, i8042, backlight, and optional ACPI video/WMI compatibility. ThinkPad options include `THINKPAD_ACPI` plus debug, ALSA, unsafe LED, video, and hotkey polling suboptions. Lenovo WMI options include hotkey utilities, camera, YMC tablet mode, GameZone, tuning, capdata/events/helpers, YogaBook, and Yoga Tablet fast charge.

Control flow/build behavior: no runtime logic. Kconfig resolution controls which modules are visible and guarantees required frameworks are present before drivers compile.

State/persistence: no runtime state. Choices affect module availability and which sysfs/input/platform-profile features can be present on Lenovo hardware.

Dependencies/integration: integrates with ACPI, ACPI_WMI, DMI, input, rfkill, backlight, LEDs, DRM, hwmon, firmware-attributes, extcon, serial device bus, and platform-profile frameworks.

Risks: dependency expressions like `ACPI_WMI || ACPI_WMI = n` permit building without WMI but avoid impossible combinations. User-visible help text for ThinkPad video includes old cautionary language but documents real interaction risks.

Test signals: configuration should expose only valid combinations; enabling each symbol should produce the Makefile module names and satisfy selected helper dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/Kconfig -->
