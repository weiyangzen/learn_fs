# sources/distributed-fs/ceph-client/drivers/firmware/google/Kconfig

Purpose: Defines configuration switches for Google/coreboot firmware drivers: GSMI SMI services, coreboot table enumeration, CBMEM sysfs export, firmware memconsole variants, coreboot framebuffer registration, and VPD sysfs export.

Important APIs/types/functions: `GOOGLE_FIRMWARE` gates the submenu. Symbols include `GOOGLE_SMI`, `GOOGLE_CBMEM`, `GOOGLE_COREBOOT_TABLE`, `GOOGLE_MEMCONSOLE`, `GOOGLE_MEMCONSOLE_X86_LEGACY`, `GOOGLE_FRAMEBUFFER_COREBOOT`, `GOOGLE_MEMCONSOLE_COREBOOT`, and `GOOGLE_VPD`.

Control flow: No runtime flow. Kconfig dependencies select which source files are compiled and enforce platform prerequisites such as X86/ACPI/DMI for legacy SMI/EBDA paths or `HAS_IOMEM && (ACPI || OF)` for coreboot table access.

State and persistence behavior: No direct state. Build choices determine whether drivers expose sysfs firmware state, EFI variables through GSMI, or framebuffer/memconsole platform devices.

Dependencies and integration points: Coordinates dependencies among Google firmware drivers. CBMEM, VPD, memconsole-coreboot, and framebuffer-coreboot depend on the coreboot table bus; memconsole variants select the shared memconsole core.

Risks and test signals: Wrong dependencies can create link errors or unusable drivers on unsupported platforms. Test signals are allmodconfig/build coverage, module dependency checks, and boot tests on coreboot ACPI and DT systems.
