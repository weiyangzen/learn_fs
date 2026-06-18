<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/Kconfig

## Purpose
Defines the Intel platform-x86 driver build menu and sources submenus for Intel camera, IFS, SAR, INT3472, PMC, PMT, Speed Select, telemetry, WMI, and uncore-frequency drivers.

## Important Symbols
Key visible symbols in this subset include `INTEL_HID_EVENT`, `INTEL_VBTN`, `INTEL_EHL_PSE_IO`, `INTEL_INT0002_VGPIO`, `INTEL_OAKTRAIL`, `INTEL_BXTWC_PMIC_TMU`, `INTEL_BYTCRC_PWRSRC`, `INTEL_CHTDC_TI_PWRBTN`, `INTEL_CHTWC_INT33FE`, `INTEL_ISHTP_ECLITE`, `INTEL_MRFLD_PWRBTN`, `INTEL_PLR_TPMI`, `INTEL_TPMI`, `INTEL_VSEC`, and support options for P-Unit IPC, RST, SDSI, Smart Connect, and Turbo Max 3.0.

## Control Flow
Kconfig has no runtime path, but its dependency graph controls which platform drivers are built and which child directories the sibling Makefile descends into. Several options constrain module linkage against provider drivers, for example INT33FE requires compatible charger, xHCI role-switch, and Type-C mux linkage.

## State And Persistence
State is build-time only and persists in `.config`. It controls module names, object inclusion, and whether platform ACPI IDs can bind at runtime.

## Dependencies And Integration Points
The file depends on ACPI, I2C, PCI, input, GPIOLIB, PM sleep, MFD PMIC, POWER_SUPPLY, REGULATOR, INTEL_VSEC/TPMI, and other subsystem symbols.

## Risks And Test Signals
Main risk is dependency drift causing missing symbols, impossible module combinations, or drivers built without required providers. Validate with `olddefconfig`, `COMPILE_TEST` where available, and targeted builds for each visible symbol and its module form.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/Kconfig -->
