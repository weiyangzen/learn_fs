# sources/distributed-fs/ceph-client/drivers/acpi/x86/utils.c

### Purpose
`utils.c` collects x86 ACPI platform quirks: overriding broken `_STA` results, forcing NVMe Storage D3 policy on modern AMD systems, skipping bogus Android-tablet I2C/serdev/AC/battery/GPIO enumeration, creating Dell UART backlight glue, and disabling mwait on a known-bad system.

### Important APIs, Types, And Functions
Exported or externally used APIs include `acpi_device_override_status()`, `force_storage_d3()`, `acpi_quirk_skip_i2c_client_enumeration()`, `acpi_quirk_skip_serdev_enumeration()`, `acpi_quirk_skip_gpio_event_handlers()`, `acpi_quirk_skip_acpi_ac_and_battery()`, and `acpi_proc_quirk_mwait_check()`. Key data structures are `override_status_id` and DMI quirk tables.

### Control Flow
Status override checks CPU model, optional DMI, then HID/UID or full ACPI path and returns a replacement status. Storage D3 returns true for Zen systems with FADT Low Power S0. Android-tablet helpers match DMI quirk bitmasks, skip unsafe I2C clients except known-good PMIC/audio/keyboard HIDs, skip or redirect serdev enumeration based on UART UID, skip GPIO event handlers, and suppress ACPI AC/battery when native PMIC drivers are preferable. Dell `DELL0501` causes a `dell-uart-backlight` platform device and skips serdev child enumeration.

### State, Persistence, And Dependencies
The file is mostly stateless policy, but it creates a static platform device for Dell UART backlight and can set global `boot_option_idle_override = IDLE_NOMWAIT`. It depends on DMI, ACPI device matching, CPU model matching, PCI devfn fallback for UART UID, platform-device registration, and optional `CONFIG_X86_ANDROID_TABLETS`.

### Integration Points
ACPI scan uses `_STA` override; I2C, serdev, GPIO, battery/AC, storage, and processor idle paths consume the quirk APIs. It coordinates with `drivers/platform/x86/x86-android-tablets.c` for manual device instantiation on broken Android x86 tablets.

### Risks
Quirks can hide real devices or expose bogus devices, causing resource conflicts, missing input sensors, broken charging, or wrong UART client creation. DMI strings are sometimes generic, so entries add BIOS dates or exact matches. The Storage D3 broad AMD policy intentionally compensates for missing firmware properties but may affect NVMe power behavior.

### Test Signals
Test exact DMI systems for intended device visibility, I2C known-good exceptions, serdev skip/tty fallback behavior, Dell UART backlight platform creation, PMIC AC/battery suppression, NVMe D3 during s2idle on AMD, and mwait disabled on the Acer Extensa quirk.
