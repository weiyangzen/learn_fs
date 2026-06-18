# sources/distributed-fs/ceph-client/drivers/acpi/x86/cmos_rtc.c

### Purpose
`cmos_rtc.c` installs an ACPI CMOS address-space handler and creates platform devices for ACPI RTC/TAD devices so AML can access CMOS RTC fields through `ACPI_ADR_SPACE_CMOS`.

### Important APIs, Types, And Functions
The entry point is `acpi_cmos_rtc_init()`, registering `cmos_rtc_handler`. The attach path calls `acpi_install_cmos_rtc_space_handler()` and `acpi_create_platform_device()`. `acpi_cmos_rtc_space_handler()` performs byte reads/writes through `CMOS_READ()` and `CMOS_WRITE()`.

### Control Flow
Matching HIDs include `ACPI000E` and standard CMOS RTC IDs. The first attached device installs the address-space handler once. Each attach attempts platform-device creation; for non-TAD RTC IDs it sets `cmos_rtc_platform_device_present` when the platform device was created.

### State, Persistence, And Dependencies
State includes the global `cmos_rtc_platform_device_present` flag and the static once-only handler-installed flag. CMOS hardware state persists outside the driver. Access is serialized by `rtc_lock` with IRQ-safe spin locking.

### Integration Points
This bridges ACPI AML operation regions to the mc146818 RTC implementation and ACPI scan platform-device creation. Other x86 ACPI code can check whether a CMOS RTC platform device exists.

### Risks
The handler rejects base addresses above 0xff but does not explicitly reject multi-byte accesses that cross 0xff after the first byte. Incorrect AML writes can modify persistent RTC/CMOS registers. Handler installation failure logs but blocks attach with `-ENODEV`.

### Test Signals
Signals include successful ACPI scan attachment for RTC/TAD devices, AML CMOS region reads/writes matching hardware registers, platform device creation, correct locking under concurrent RTC access, and graceful behavior if the handler is already installed.
