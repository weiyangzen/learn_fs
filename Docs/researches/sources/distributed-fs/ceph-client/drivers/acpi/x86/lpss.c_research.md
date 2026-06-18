# sources/distributed-fs/ceph-client/drivers/acpi/x86/lpss.c

### Purpose
`lpss.c` enumerates and manages Intel Low Power Subsystem ACPI devices on x86. It creates platform devices, registers per-device clocks, applies PWM/UART/I2C/SPI quirks, exposes LTR diagnostics, and provides a custom PM domain for LPSS context save/restore and power sequencing.

### Important APIs, Types, And Functions
Core types are `struct lpss_device_desc`, `struct lpss_private_data`, and `struct lpss_device_links`. Entry point `acpi_lpss_init()` registers an ACPI scan handler and platform bus notifier. Key helpers are `acpi_lpss_create_device()`, `register_device_clock()`, `acpi_lpss_save_ctx()`, `acpi_lpss_restore_ctx()`, `acpi_lpss_suspend()`, `acpi_lpss_resume()`, `acpi_lpss_set_ltr()`, and IOSF D3 helpers for Atom LPSS DMA power quirks.

### Control Flow
ACPI IDs map to descriptors for Lynxpoint, BayTrail, Braswell, Broadwell, DMA, PWM, UART, I2C, SPI, and SDIO devices. Attach maps the first memory resource, runs descriptor setup, registers clocks if required, fixes up ACPI power state, creates a platform device, and creates selected device links from `_DEP`/DMI data. Platform bus notifications install/remove the LPSS PM domain and LTR sysfs group. PM callbacks save private registers, call ACPI power transitions, add D3-to-D0 delay where needed, restore context, and handle late/noirq sequencing for devices that must resume early.

### State, Persistence, And Dependencies
Each ACPI device stores `lpss_private_data` in `adev->driver_data`, including MMIO mapping, clock pointer, fixed clock rate, descriptor, and saved private-register context. Global state includes the LPSS clock platform device, Atom D3 mask, LPSS quirks, IOSF mutex, and D3-entered flag. Dependencies span ACPI scan/power, PCI, platform devices, clk framework, PWM lookup tables, runtime PM, DMI, IOSF MBI, PMC Atom registers, and property entries for child drivers.

### Integration Points
It is the platform glue for downstream drivers such as DesignWare UART/I2C, PXA2xx SPI, PWM LPSS, SDIO, and LPSS DMA. Device links keep GPU/SD card dependencies ordered against PMIC I2C controllers. LTR sysfs and `set_latency_tolerance` integrate with PM QoS-style latency tolerance.

### Risks
LPSS devices can hang the system if accessed while unpowered, so PM ordering and the always-power-on DMA quirk are critical. MMIO size checks protect LTR access, but descriptor offsets must match hardware. Context save after firmware has powered off a block can save `0xffffffff`, hence `SAVE_CTX_ONCE`. Device-link DMI exceptions can alter suspend behavior on specific tablets.

### Test Signals
Test enumeration on Lynxpoint/BayTrail/Braswell/Broadwell systems, per-device clock registration and rates, UART RTS override behavior, I2C reset and shared-host handling, PWM lookup consumers, LTR sysfs reads, runtime suspend/resume, S0ix suspend cycles, context retention, and absence of DMA island hangs.
