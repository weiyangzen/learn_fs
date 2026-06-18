# Research: subset-b-005137

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/inspur_platform_profile.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/inspur_platform_profile.c

## Purpose
Implements Inspur WMI integration with the generic Linux platform profile API. It exposes EC power modes as `low-power`, `balanced`, and `performance` platform profiles through a WMI GUID.

## Important APIs, Types, And Functions
The driver matches `WMI_INSPUR_POWERMODE_BIOS_GUID`. `inspur_wmi_perform_query()` wraps `wmidev_evaluate_method()` and validates ACPI buffer replies. `inspur_platform_profile_get()` and `inspur_platform_profile_set()` translate between `enum platform_profile_option` and Inspur EC mode bytes. `inspur_platform_profile_probe()` declares supported choices.

## Control Flow
WMI probe allocates `struct inspur_wmi_priv`, stores the WMI device, then calls `devm_platform_profile_register()`. Reads issue method `0x02`, check return code byte 0, and decode mode byte 1. Writes place the desired mode in byte 0, issue method `0x03`, then treat a nonzero returned byte 0 as EC failure.

## State And Persistence
Driver state is just the device-private WMI pointer and platform-profile device. Persistent state lives in EC RAM/firmware power-mode settings, not in this module.

## Dependencies And Integration Points
Depends on ACPI WMI and `platform_profile`. It integrates with userspace through `/sys/firmware/acpi/platform_profile` style platform profile interfaces managed by the core.

## Risks And Test Signals
Risks are firmware ABI mismatch, unexpected ACPI object type or length, and unsupported EC mode values. Test by loading on matching Inspur hardware, reading/writing all three profile choices, checking error handling for invalid values, and verifying WMI method failures are surfaced as negative errno.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/inspur_platform_profile.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/Makefile

## Purpose
Maps Intel platform-x86 Kconfig symbols to subdirectories and wrapper module objects.

## Important Build Rules
Top-level subdirectories are included for AtomISP2, IFS, INT1092 SAR, INT3472, PMC, PMT, Speed Select, telemetry, WMI, and uncore frequency. Standalone files are collected into `intel-target-*`, then the `INTEL_OBJ_TARGET` macro wraps each object as an `intel-<target>.o` module, producing module names such as `intel-hid`, `intel-bytcrc-pwrsrc`, and `intel-plr-tpmi`.

## Control Flow
This is Kbuild control flow. The basename of each selected target becomes both the inner object and the wrapped object assignment, so `intel-target-$(CONFIG_INTEL_HID_EVENT) += hid.o` expands into `intel-hid-y := hid.o` and `obj-* += intel-hid.o`.

## State And Persistence
No runtime state. The generated object graph is determined by `.config`.

## Dependencies And Integration Points
Must stay synchronized with the Kconfig symbols and source filenames in this directory and child directories.

## Risks And Test Signals
Risks include stale object names, wrapping behavior that surprises module naming, and child directories selected without their provider symbols. Test with `make V=1 drivers/platform/x86/intel/` under built-in and module configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/Kconfig

## Purpose
Defines build options for the Bay Trail/Cherry Trail AtomISP2 platform helper drivers.

## Important Symbols
`INTEL_ATOMISP2_PDX86` is an internal bool selected by the feature drivers. `INTEL_ATOMISP2_LED` builds a DMI-based camera LED helper using GPIOLIB and `LEDS_GPIO`. `INTEL_ATOMISP2_PM` builds the PCI power-management dummy driver and depends on PCI, IOSF MBI, PM, and absence of the real `INTEL_ATOMISP` driver.

## Control Flow
The LED option creates a platform device for `leds-gpio` on known systems. The PM option binds to ISP PCI IDs to put the ISP/IUNIT into D3 and support S0ix.

## State And Persistence
Build-time state only; selected options decide whether the AtomISP2 child directory is entered and which module names exist.

## Dependencies And Integration Points
Connects Intel platform-x86 to LED, GPIO, PCI, PM runtime, and IOSF MBI subsystems.

## Risks And Test Signals
Dependency mistakes can either leave camera LEDs stuck on at boot or prevent power savings. Validate by building both options and testing known Bay Trail/Cherry Trail systems for LED default-off behavior and ISP D3 transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/Makefile

## Purpose
Builds AtomISP2 helper modules.

## Important Build Rules
`intel_atomisp2_led-y := led.o` and `obj-$(CONFIG_INTEL_ATOMISP2_LED)` create the LED helper. `intel_atomisp2_pm-y += pm.o` and `obj-$(CONFIG_INTEL_ATOMISP2_PM)` create the PM helper.

## Control Flow And State
The file has only build-time behavior. Its module object names must match the Kconfig help text and the platform-x86 parent Makefile directory selection.

## Dependencies, Risks, And Test Signals
Depends on the two AtomISP2 Kconfig symbols. A wrong object name drops a helper silently from configured builds. Test with built-in and module builds for each option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/led.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/led.c

## Purpose
Creates a `leds-gpio` platform device for known Bay Trail/Cherry Trail tablets whose AtomISP2 camera LED GPIO is not described by ACPI. The immediate goal is to force LEDs off at boot and expose them via the LED class.

## Important APIs, Types, And Functions
Uses `struct gpio_led`, `gpio_led_platform_data`, DMI matching, and `gpiod_lookup_table`. Lookup tables map ASUS T100TA/T200TA and T100CHI systems to specific `INT33FC` GPIO pins. `atomisp2_led_init()` performs DMI selection, adds the lookup table, and registers the `leds-gpio` device.

## Control Flow
Module init exits with `-ENODEV` unless the DMI table matches. On match it installs the GPIO lookup table, then registers `leds-gpio` with one LED named `atomisp2::camera` and default state off. Exit unregisters the platform device and lookup table.

## State And Persistence
Global pointers track the active lookup table and platform device. Hardware GPIO/LED state persists through the GPIO and LED framework after registration.

## Dependencies And Integration Points
Depends on DMI, GPIO consumer machine lookups, platform devices, and `leds-gpio`. Soft-depends on `asus_nb_wmi` so this driver can turn off LEDs after ASUS WMI firmware methods turn them on.

## Risks And Test Signals
Risks are wrong DMI matches, wrong GPIO controller/pin indexes, and load order. Test on listed ASUS devices by checking that the LED is off after boot, appears under LED sysfs, and toggles only the camera LED.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/pm.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/pm.c

## Purpose
Dummy PCI driver for Intel AtomISP2/IUNIT devices. It exists to runtime-suspend the ISP into D3cold and allow low-power S0ix states when no full camera driver is in use.

## Important APIs, Types, And Functions
`isp_set_power()` writes IOSF PMC register `ISPSSPM0` and polls status bits for power on/off. `isp_probe()` enables runtime PM and immediately suspends. `isp_pci_suspend()` disables interrupts and CSI ports, saves PCI state, marks D3cold, and powers down. `isp_pci_resume()` powers up and restores PCI config space.

## Control Flow
The PCI driver binds Intel device IDs `0x0f38` and `0x22b8`. Probe puts the device into runtime suspend. System suspend executes the custom PM path instead of normal PCI power state changes because the PMCSR does not reflect the actual IUNIT power gate.

## State And Persistence
Persistent hardware state is PCI config space plus IOSF PMC power-gate state. The driver saves PCI state before power-off and restores it after power-on.

## Dependencies And Integration Points
Depends on PCI, PM runtime, delay helpers, and `asm/iosf_mbi.h`. It must not coexist with `INTEL_ATOMISP`.

## Risks And Test Signals
Risks include IOSF power transition timeout, accessing config space after the unit is power-gated, and incomplete CSI shutdown. Test with runtime PM status, S0ix residency, suspend/resume, and repeated bind/unbind on both PCI IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/bxtwc_tmu.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/bxtwc_tmu.c

## Purpose
Adds Broxton Whiskey Cove PMIC Time Management Unit alarm interrupt support, primarily enabling alarm wakeup behavior.

## Important APIs, Types, And Functions
`struct wcove_tmu` stores IRQ and PMIC regmap. `bxt_wcove_tmu_irq_handler()` reads `BXTWC_TMUIRQ`, acknowledges wake/system alarm bits, and returns whether it handled the IRQ. Probe requests a threaded IRQ and unmasks second-level TMU alarm bits. Remove masks TMU interrupts at level 1 and second level.

## Control Flow
The platform driver gets the parent `intel_soc_pmic` regmap, requests IRQ 0, unmasks `BXTWC_TMU_WK_ALRM` and `BXTWC_TMU_SYS_ALRM`, and stores driver data. Suspend enables IRQ wake; resume disables it.

## State And Persistence
State is the PMIC interrupt mask and pending-status registers plus the IRQ wake setting. Device memory is devm-managed.

## Dependencies And Integration Points
Depends on `INTEL_SOC_PMIC_BXTWC`, `MFD_INTEL_PMC_BXT`, regmap, platform IRQs, and PM sleep.

## Risks And Test Signals
Risks are missed alarm acknowledgements, incorrect mask restoration on remove, and unchecked regmap failures. Test by programming PMIC alarms, verifying wake from suspend, checking no IRQ storm, and confirming masks are restored after unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/bxtwc_tmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/bytcrc_pwrsrc.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/bytcrc_pwrsrc.c

## Purpose
Provides Bay Trail Crystal Cove PMIC power-source reporting and reset/wake-source debugfs diagnostics, with optional `power_supply` registration for boards that request it.

## Important APIs, Types, And Functions
`struct crc_pwrsrc_data` stores regmap, debugfs dentries, optional power_supply, and latched reset/wake values. `crc_pwrsrc_read_and_clear()` snapshots and clears sticky source registers. `crc_pwrsrc_psy_get_property()` reports `POWER_SUPPLY_PROP_ONLINE` when USB or DC input is present. Debugfs show handlers decode named bit reasons.

## Control Flow
Probe reads and clears reset source and wake source registers before debugfs is used. If the parent has `linux,register-pwrsrc-power_supply`, probe registers a mains power_supply and IRQ handler; the handler clears PMIC power-source IRQ bits and calls `power_supply_changed()`. Debugfs files `pwrsrc`, `resetsrc`, and `wakesrc` are always created.

## State And Persistence
Resetsrc and wakesrc are sticky hardware registers that are copied into driver state and cleared. Current power-source state is read live. Debugfs state is removed on driver remove.

## Dependencies And Integration Points
Depends on parent `intel_soc_pmic` regmap, POWER_SUPPLY, debugfs, platform IRQs, and device properties.

## Risks And Test Signals
Leaving wakesrc uncleared can affect reboot/poweroff behavior on some tablets. Other risks are optional power_supply property misuse and IRQ acknowledgement failures. Test debugfs decoded output, AC online transitions, IRQ-driven uevents, and reboot behavior after wake-source bit 0 was set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/bytcrc_pwrsrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/chtdc_ti_pwrbtn.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/chtdc_ti_pwrbtn.c

## Purpose
Reports the Cherry Trail Dollar Cove TI PMIC power button as a Linux input `KEY_POWER` device.

## Important APIs, Types, And Functions
The IRQ handler reads `CHTDC_TI_SIRQ_REG` through the parent PMIC regmap and reports press when `SIRQ_PWRBTN_REL` is clear. Probe allocates an input device, registers `KEY_POWER`, requests a threaded IRQ, and configures wake IRQ support.

## Control Flow
Platform probe obtains IRQ 0 and parent `intel_soc_pmic` regmap. Every interrupt reads button state, emits key event plus sync, and returns handled. Remove clears wake IRQ and disables device wakeup.

## State And Persistence
Driver state is devres-managed input and the regmap pointer stored in device drvdata. Wake IRQ state persists while the device is active.

## Dependencies And Integration Points
Depends on the Dollar Cove TI PMIC MFD child, input subsystem, platform IRQs, regmap, and PM wakeirq.

## Risks And Test Signals
Risks include interpreting release polarity incorrectly and failing to wake from suspend. Test press/release with `evtest`, IRQ count, suspend wake, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/chtdc_ti_pwrbtn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/chtwc_int33fe.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/chtwc_int33fe.c

## Purpose
Pseudo-driver for Cherry Trail Whiskey Cove `INT33FE` ACPI devices on specific GPD mini laptops. It creates missing I2C clients and software nodes for MAX17047 fuel gauge, FUSB302 Type-C controller, PI3USB30532 mux, USB connector, and DisplayPort altmode relationships.

## Important APIs, Types, And Functions
`struct cht_int33fe_data` tracks created clients and the DP fwnode. Software nodes describe max17047 supplies, FUSB302 role-switch, connector PDOs, PI3USB30532 orientation/mode switch, and DP altmode. `cht_int33fe_add_nodes()` finds the xHCI role-switch software node, registers the node group, and attaches a secondary fwnode to GPU child `DD04`. `cht_int33fe_register_max17047()` handles duplicate firmware enumeration by adding secondary properties and reprobeing.

## Control Flow
Probe is gated by DMI for GPD Win/Pocket patterns. It waits for the bq24292i VBUS regulator and FUSB302 IRQ, registers software nodes, creates or augments the max17047 fuel gauge from ACPI I2C resource 1, creates FUSB302 from resource 2 with IRQ, and creates PI3USB30532 from resource 3. Failure paths unregister clients and software nodes in reverse order.

## State And Persistence
State is the three I2C client pointers, registered software nodes, and DP secondary fwnode association. These are removed on driver removal. Hardware state is owned by the child drivers.

## Dependencies And Integration Points
Integrates ACPI, DMI, I2C ACPI resource instantiation, regulators, USB Type-C/PD properties, xHCI role-switch software node, PCI GPU child fwnodes, and standard max17047/FUSB302/PI3USB30532 drivers.

## Risks And Test Signals
Risks are fragile DMI gating, probe ordering with the role-switch and regulator, stale global `fusb302_mux_refs`, and duplicate fuel-gauge reprobe side effects. Test on target GPD systems for all child devices binding, Type-C role/orientation changes, DP altmode, charging/fuel-gauge properties, and clean remove/reprobe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/chtwc_int33fe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/crystal_cove_charger.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/crystal_cove_charger.c

## Purpose
Implements the Crystal Cove PMIC external-charger IRQ pass-through. It is not a charger power_supply driver; it creates a nested IRQ domain so an external charger driver can consume the PMIC's single charger IRQ after the PMIC-specific level-2 acknowledgement is handled.

## Important APIs, Types, And Functions
`struct crystal_cove_charger_data` stores regmap, IRQ domain, nested charger IRQ, and mask state. The irqchip implements mask/unmask with bus lock and sync to `MCHGRIRQ_REG`. `crystal_cove_charger_irq()` handles the parent IRQ, dispatches the nested IRQ, then writes `CHGRIRQ_REG` bit 0 to acknowledge.

## Control Flow
Probe creates a one-entry irq_domain on the parent fwnode, marks it `DOMAIN_BUS_WAKEUP`, maps hwirq 0, installs a simple nested irqchip, masks the second-level interrupt, then requests the parent threaded IRQ. Consumers obtain the nested IRQ through the shared firmware node/domain.

## State And Persistence
State includes mask and new_mask software copies and the PMIC mask register. The IRQ domain is removed by a devm action.

## Dependencies And Integration Points
Depends on the Crystal Cove PMIC MFD regmap, IRQ domain APIs, nested threaded IRQs, and external charger child drivers.

## Risks And Test Signals
Risks are domain collision on shared MFD fwnodes, unbalanced masking, and failing to ack the PMIC level-2 source. Test by binding the external charger, verifying nested IRQ delivery, checking charger insertion events, and confirming no interrupt storm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/crystal_cove_charger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ehl_pse_io.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ehl_pse_io.c

## Purpose
PCI parent driver for Intel Elkhart Lake Programmable Service Engine I/O. It enumerates a PCI function and creates auxiliary devices for PSE GPIO and timed I/O.

## Important APIs, Types, And Functions
`ehl_pse_io_dev_create()` allocates `struct ehl_pse_io_data`, slices BAR0 into 4 KiB resources per child, assigns MSI vectors by index, and calls `__devm_auxiliary_device_create()` using names from `linux/ehl_pse_io_aux.h`.

## Control Flow
Probe enables the PCI device with pcim, sets bus mastering, allocates exactly two MSI vectors, creates GPIO child index 0, and creates TIO child index 1. The actual functionality is in auxiliary drivers.

## State And Persistence
Only child-device platform data and PCI MSI allocation are maintained. Devm/pcim clean up on remove.

## Dependencies And Integration Points
Depends on PCI, auxiliary bus, BAR0 resources, MSI, and the public EHL PSE I/O auxiliary header contract.

## Risks And Test Signals
Risks include assuming BAR layout and exactly two vectors, and creating children with invalid IRQ vectors if allocation changes. Test PCI probe on device IDs `0x4b88` and `0x4b89`, child auxiliary driver binding, resource ranges, and interrupt delivery for both children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ehl_pse_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/hid.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/hid.c

## Purpose
ACPI platform driver for Intel HID hotkeys, virtual button arrays, power-button wake behavior, and optional tablet-mode switch reporting.

## Important APIs, Types, And Functions
The driver matches several ACPI IDs including `INT33D5` and `INTC10xx`. It uses sparse keymaps for hotkey events and five-button-array events. `intel_hid_execute_method()` and `intel_hid_evaluate_method()` abstract ACPI DSM calls with fallback to named methods. `notify_handler()` routes ACPI notifies to key, button-array, tablet-mode, or wakeup handling. `button_array_present()` checks HEBC capability bits plus DMI/module-param overrides.

## Control Flow
Probe initializes DSM support, requires simple mode from `HDMM`, allocates private state, decides tablet-mode policy from module parameter, DMI allow list, chassis type, and dual-accelerometer detection, registers input devices, installs an ACPI notify handler, enables hotkeys and button array, calls `BTNL` for HID power button support, marks the device wake-capable, and marks the EC GPE for wake. Notify `0xc0` means a HID event index is fetched via `HDEM`; other notify values are button-array or tablet events. Suspend disables button-array and hotkeys unless platform suspend is skipped; wakeup mode filters events so only relevant button events wake the system.

## State And Persistence
`struct intel_hid_priv` holds input devices and a wakeup-mode flag. Global module parameters tune button array and tablet-mode behavior. Firmware event enable state persists through ACPI method calls and is restored on resume.

## Dependencies And Integration Points
Depends on ACPI, DMI, input sparse-keymap, suspend core, EC wake handling, I2C dependency from Kconfig, and local `dual_accel_detect.h`.

## Risks And Test Signals
Risks are firmware-specific event codes, unreliable VGBS tablet state, wake storms, duplicate power button events, and global DSM mask shared across devices. Test hotkeys with `evtest`, five-button array press/release, tablet mode on allow-listed convertibles, suspend-to-idle wake filtering, hibernate freeze/thaw, and unknown event logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/hid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/Kconfig

## Purpose
Defines `INTEL_IFS`, the Intel In Field Scan driver option.

## Important Symbol
`INTEL_IFS` is a tristate depending on x86, Intel CPU support, 64-bit, and SMP. It builds module `intel_ifs`.

## Control Flow And State
No runtime flow. Build selection determines whether the IFS misc devices can be registered on CPUs advertising the required integrity capability MSRs.

## Dependencies And Integration Points
The dependency set matches IFS runtime assumptions: Intel x86 CPUs, SMP core sibling coordination, and 64-bit MSR paths.

## Risks And Test Signals
Risks are enabling on unsupported CPUs or missing feature-guarded build dependencies. Test with target Intel server CPUs and negative boots on unsupported x86 systems where probe should return `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/Makefile

## Purpose
Builds the Intel In Field Scan module.

## Important Build Rules
`obj-$(CONFIG_INTEL_IFS) += intel_ifs.o` and `intel_ifs-y := core.o load.o runtest.o sysfs.o` link CPU matching, firmware loading, test execution, and sysfs interfaces into one module.

## Dependencies, Risks, And Test Signals
The file depends on the four implementation objects staying in sync with `ifs.h`. Test by building `CONFIG_INTEL_IFS=y` and `m`; missing any object breaks exported symbols such as `ifs_load_firmware()` or `do_core_test()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/core.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/core.c

## Purpose
Top-level Intel IFS module initialization. It detects supported CPU models and integrity capabilities, configures per-test misc devices, and registers sysfs attribute groups.

## Important APIs, Types, And Functions
`ifs_cpu_ids[]` maps supported Sapphire Rapids, Emerald Rapids, Granite Rapids, Crestmont, and Darkmont families to array-test generations. `ifs_devices[]` describes SAF, Array BIST, and SBAF devices with test capability bits, MSR sets, and miscdevice names `intel_ifs_0`, `intel_ifs_1`, and `intel_ifs_2`. `ifs_pkg_auth` tracks per-package firmware authentication during load.

## Control Flow
`ifs_init()` first matches CPU family/model and checks `MSR_IA32_CORE_CAPS` for integrity capability exposure. It reads `MSR_INTEGRITY_CAPS`, allocates per-package auth state, then registers only devices whose integrity-cap bit is set. Generation and array generation are stored in each device's runtime data. Error cleanup deregisters any already registered misc devices.

## State And Persistence
Global `ifs_devices[]` holds per-device runtime data for loaded image, status, generation, and last details. `ifs_pkg_auth` is allocated for topology max packages and freed on module exit.

## Dependencies And Integration Points
Depends on x86 CPU matching, MSR access, miscdevice registration, attribute groups exported by `sysfs.c`, and constants/data structures from `ifs.h`.

## Risks And Test Signals
Risks include stale CPU model lists, incorrect capability-bit mapping, and registering devices with missing MSR support. Test on each supported generation by checking misc device creation matches capability bits, sysfs groups differ for array tests, and cleanup unloads all registered devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/ifs.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/ifs.h

## Purpose
Shared IFS documentation and internal ABI. It defines the hardware MSR layouts, test types, runtime data structures, and cross-file function declarations.

## Important APIs, Types, And Data
The header documents firmware file layout and sysfs workflow. It defines MSR addresses for SAF, SBAF, Array BIST, status, copy, and control registers. Bitfield unions include `ifs_scan_hashes_status`, `ifs_chunks_auth_status`, `ifs_scan`, `ifs_status`, `ifs_array`, `ifs_sbaf`, and `ifs_sbaf_status`. `struct ifs_data` stores loaded firmware state and last test result. `struct ifs_device` combines capabilities, MSR selectors, runtime data, and miscdevice.

## Control Flow And Integration
Inline helpers recover `ifs_data`, `ifs_test_caps`, and `ifs_test_msrs` from a miscdevice-backed sysfs device. `load.c` uses the firmware/MSR definitions, `runtest.c` uses activation/status unions, `sysfs.c` exposes `ifs_load_firmware()` and `do_core_test()`, and `core.c` fills generation data.

## State And Persistence
The header owns no storage except declarations. It defines persistent in-memory status fields surfaced through sysfs: loaded batch, image version, pass/fail/untested status, hardware details, chunk count, and SBAF max bundle.

## Dependencies And Integration Points
Depends on Linux device and miscdevice APIs plus x86 MSR constants. Firmware path and sysfs names are part of the user-facing contract.

## Risks And Test Signals
Risks include C bitfield layout assumptions matching hardware MSR encoding, generation-specific field width changes, and user ABI drift. Test with compiler builds, real hardware MSR decode, firmware loads for gen0/gen2, and sysfs documentation consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/ifs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/load.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/load.c

## Purpose
Loads Intel IFS firmware images, validates Intel microcode-style headers and IFS metadata, copies hashes, and authenticates scan/SBAF chunks into secure package memory.

## Important APIs, Types, And Functions
`find_meta_data()` walks microcode metadata blocks. `image_sanity_check()` validates IFS header type, Intel microcode sanity, and CPU signature match. `validate_ifs_metadata()` checks batch number, test type, chunk alignment, and stride metadata. `scan_chunks_sanity_check()` authenticates chunks per socket for gen0 and through gen2 stride-aware flow when supported. `ifs_load_firmware()` constructs `intel/ifs_<test>/<ff>-<mm>-<ss>-<batch>.<suffix>` and drives the full process.

## Control Flow
Firmware is requested with `request_firmware_direct()`, size is checked against header `totalsize`, metadata and CPU signature are validated, and global pointers are set to header/hash/test data. Gen0 schedules `copy_hashes_authenticate_chunks()` on one online CPU per package and waits for completion. Gen2 optionally copies hashes, invalidates stride, then writes chunk-table pointers to copy/authenticate chunks with retry on authentication-interrupted errors.

## State And Persistence
Global pointers reference the currently requested firmware while it is loaded. `ifs_data` is updated with loaded flag, image version, chunk size, valid chunks, loading error, and SBAF max bundle. Authenticated chunks persist in hardware secure memory until invalidated/reloaded or reset.

## Dependencies And Integration Points
Depends on firmware loader, Intel microcode helpers, CPU topology, MSR writes, completions/workqueues, and `ifs_pkg_auth` from `core.c`.

## Risks And Test Signals
Risks are use of firmware data pointers only while firmware is held, metadata corruption, generation-specific chunk status interpretation, and package authentication races. Test good and bad firmware names, size/signature failures, metadata mismatch, multi-socket loading, gen2 stride invalidation, and expected sysfs `current_batch`/`image_version`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/load.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/runtest.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/runtest.c

## Purpose
Executes IFS tests on a selected physical core: SAF scan tests, Array BIST, and SBAF. It synchronizes SMT siblings, writes activation MSRs, interprets status, and records user-visible pass/fail/untested details.

## Important APIs, Types, And Functions
`do_core_test()` is the sysfs entry point. `ifs_test_core()` runs SAF over all valid chunks with retry/forward-progress logic. `ifs_array_test_core()` and `ifs_array_test_gen1()` run Array BIST generations. `ifs_sbaf_test_core()` runs SBAF over bundle/program indexes. Worker callbacks `doscan()`, `do_array_test()`, `do_array_test_gen1()`, and `dosbaf()` execute under `stop_core_cpuslocked()`.

## Control Flow
`do_core_test()` takes `cpus_read_lock()`, rejects offline CPUs, then dispatches by test type. SAF and SBAF require a loaded image. Sibling CPUs rendezvous using atomics and short delay loops, then write activation MSRs together. Status is reported by the first SMT thread. Retry loops restart from the hardware-reported chunk, bundle, or program index until success, non-restartable error, timeout, or no forward progress.

## State And Persistence
Updates `ifs_data.status` and `ifs_data.scan_details` for the last test only. Hardware test execution temporarily takes all threads of the tested core out of normal execution for up to hundreds of milliseconds.

## Dependencies And Integration Points
Depends on CPU hotplug read locks, stop-machine CPU coordination, MSR access, NMI watchdog touch, tracepoints `trace/events/intel_ifs.h`, and generation fields from `ifs_data`.

## Risks And Test Signals
Risks include latency impact, SMT sibling offline cases, forward-progress bugs, status bitfield interpretation, and stale loaded firmware. Test pass/fail/untested paths, offline sibling rejection, repeated interrupted tests, tracepoint output, and latency impact under workload isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/runtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/sysfs.c

## Purpose
Defines the IFS miscdevice sysfs ABI for loading batches, running tests, and reading last-test status/details.

## Important APIs, Types, And Functions
Attributes are `details`, `status`, `run_test`, `current_batch`, and `image_version` for scan/SBAF devices; array devices expose only `details`, `status`, and `run_test`. `ifs_sem` serializes firmware reloads and test execution.

## Control Flow
Writing a CPU number to `run_test` parses and bounds-checks it, takes `ifs_sem`, calls `do_core_test()`, and returns either count or errno. Writing `current_batch` validates `0..0xff`, stores it, then calls `ifs_load_firmware()`. Show handlers format cached state from `ifs_data`.

## State And Persistence
Sysfs exposes the latest in-memory state. `current_batch` returns `none` until a firmware image is loaded; `image_version` similarly reports `none` until load succeeds.

## Dependencies And Integration Points
Depends on `ifs.h`, sysfs device attributes, semaphore serialization, and the miscdevice groups referenced from `core.c`.

## Risks And Test Signals
Risks are user ABI regressions, insufficient serialization, and returning stale status after failed tests. Test concurrent writes to `run_test`/`current_batch`, invalid CPU/batch values, successful firmware load, array device attribute differences, and readable status strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int0002_vgpio.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int0002_vgpio.c

## Purpose
Models the Bay Trail/Cherry Trail `INT0002` ACPI PME event as a virtual GPIO controller so gpiolib-acpi can invoke firmware `_L02`/`_E02` handlers and clear PME bus 0 status to avoid IRQ storms.

## Important APIs, Types, And Functions
`struct int0002_data` embeds a `gpio_chip`, parent IRQ, and wake-enable count. Dummy GPIO get/set/direction methods reflect that this is not real GPIO hardware. The irqchip ack/mask/unmask functions manipulate I/O ports `GPE0A_STS_PORT` and `GPE0A_EN_PORT`. `int0002_irq()` checks the GPE status bit, handles the virtual GPIO IRQ, and emits a hard wake event.

## Control Flow
Probe is limited to Bay Trail or Cherry Trail SoCs, requests the shared parent IRQ directly, configures a GPIO irqchip with only pin 2 valid, registers the gpiochip, registers an ACPI wake handler, and enables device wakeup. Suspend applies parent IRQ wake only for non-firmware suspend and only if consumers requested wake.

## State And Persistence
State includes GPE enable/status bits, wake enable count, and gpiochip IRQ domain. No real GPIO value state exists.

## Dependencies And Integration Points
Depends on ACPI, gpiolib, shared IRQ handling, x86 I/O port access, platform SoC detection, suspend core, and AML event methods referencing the virtual GPIO.

## Risks And Test Signals
Risks include direct fixed-port assumptions, wake-enable count imbalance, shared IRQ side effects, and incorrect valid-mask setup. Test on BYT/CHT systems for no IRQ9 storm, ACPI event handler execution, PME wake from s2idle, and non-binding on Menlow/other SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int0002_vgpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/Kconfig

## Purpose
Defines the Intel `INTC1092` Specific Absorption Rate driver option.

## Important Symbol
`INTEL_SAR_INT1092` is a tristate depending on ACPI. Its help describes exporting BIOS-provided modem SAR configuration to userspace so a front-end can configure an Intel M.2 modem over MBIM or similar channels.

## Control Flow And State
Build-time only. When enabled, the Makefile builds `intel_sar.o` and the platform driver can bind ACPI HID `INTC1092`.

## Dependencies, Risks, And Test Signals
Risks are exposing an option without the expected userspace modem integration and ACPI DSM ABI. Test module build and ACPI binding on systems with `INTC1092`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/Makefile

## Purpose
Builds the INT1092 SAR driver.

## Important Build Rule
`obj-$(CONFIG_INTEL_SAR_INT1092) += intel_sar.o`.

## Dependencies, Risks, And Test Signals
Depends solely on the matching Kconfig symbol. Test built-in and module builds and verify the module alias from `intel_sar.c` is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/intel_sar.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/intel_sar.c

## Purpose
ACPI DSM-backed SAR data driver for Intel modem platforms. It exposes the current device mode and selected RF table indexes to userspace through sysfs.

## Important APIs, Types, And Functions
`sar_get_data()` retrieves regulatory configuration package data with DSM command 2. `parse_package()` decodes per-device-mode band, antenna, and SAR table indexes into `context->config_data`. `sar_get_device_mode()` uses DSM command 1, updates the selected data, and notifies sysfs. Attributes `intc_data` and `intc_reg` expose current values and allow selecting regulatory mode.

## Control Flow
Probe allocates `wwan_sar_context`, parses the SAR DSM UUID, loads configuration for all three regulatory modes, reads current BIOS device mode, creates sysfs attributes, and installs an ACPI notify handler. Notify event `0x80` refreshes the device mode. Writing `intc_reg` changes the regulatory index and recomputes exposed table indexes.

## State And Persistence
The context stores ACPI handle/GUID, selected regulatory mode, current SAR data, and dynamically allocated device-mode arrays per regulatory table. State is in memory and freed on remove; authoritative sensor/device mode comes from BIOS DSM.

## Dependencies And Integration Points
Depends on ACPI platform devices, DSM, sysfs, and userspace modem control software that consumes `intc_data`.

## Risks And Test Signals
Risks include weak ACPI package validation, partial default-zero entries after parse failures, memory lifetime of per-regulatory arrays, and no locking around notify/sysfs updates. Test malformed DSM packages, regulatory writes outside `0..2`, ACPI event refresh, sysfs notifications, and userspace modem SAR table selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/intel_sar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/intel_sar.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/intel_sar.h

## Purpose
Defines constants and data structures for the Intel INT1092 SAR driver.

## Important APIs And Types
Constants include DSM command IDs, driver name `intc_sar`, maximum device modes and regulatory entries, SAR DSM UUID, ACPI notify event, sysfs data name, and expected tuple size. Structures model one device-mode tuple, one regulatory configuration, userspace-supported info, and the full `wwan_sar_context`.

## Control Flow And State
The header owns no code. It defines the persistent in-memory shape used by `intel_sar.c` for parsed BIOS tables and exposed current SAR data.

## Dependencies And Integration Points
Depends on platform device and ACPI types included by the C file. The field names reflect the sysfs data contract and userspace modem SAR expectations.

## Risks And Test Signals
Risks are fixed maximums not matching future firmware and unused/stale fields such as `supported_data`. Test by compiling with `intel_sar.c` and validating sysfs output tuple order against userspace consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/intel_sar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/Kconfig

## Purpose
Defines the Intel Skylake INT3472 camera power-controller support option.

## Important Symbol
`INTEL_SKL_INT3472` is a tristate depending on ACPI, COMMON_CLK, I2C, GPIOLIB, LEDS_CLASS, and REGULATOR; it selects MFD core and I2C regmap.

## Control Flow And State
Build selection enables both discrete GPIO/power-gate and TPS68470 PMIC implementations plus a shared common library. Runtime behavior depends on ACPI `INT3472` device type and CLDB data.

## Dependencies And Integration Points
Integrates ACPI camera power controllers with clk, regulator, GPIO, LED, MFD, I2C, and sensor driver lookup mechanisms.

## Risks And Test Signals
Risks are incorrect built-in/module choices on ChromeOS-style systems where OpRegion/GPIO support must exist before sensor probing. Test built-in and module builds plus camera probe order on ChromeOS and Windows-designed hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/Makefile

## Purpose
Builds the INT3472 driver family.

## Important Build Rules
`intel_skl_int3472_discrete.o` links `discrete.o`, `discrete_quirks.o`, `clk_and_regulator.o`, and `led.o`. `intel_skl_int3472_tps68470.o` links `tps68470.o` and board data. `intel_skl_int3472_common.o` links `common.o`.

## Control Flow And State
Kbuild assembles three modules from the one Kconfig symbol. The common module exports namespaced helpers used by both implementation modules.

## Dependencies, Risks, And Test Signals
Risks include missing namespace imports or object split drift. Test by building as modules and verifying symbol resolution for `INTEL_INT3472` and `INTEL_INT3472_DISCRETE` exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/clk_and_regulator.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/clk_and_regulator.c

## Purpose
Provides clock and GPIO-backed regulator registration helpers for INT3472 discrete camera power controllers.

## Important APIs, Types, And Functions
`skl_int3472_enable_clk()` toggles either a GPIO or an ACPI DSM image-clock control. `skl_int3472_register_clock()` registers a clock with clkdev lookup for the sensor device, deriving frequency from the sensor `SSDB` buffer. `skl_int3472_register_dsm_clock()` and `skl_int3472_register_gpio_clock()` select DSM or GPIO control. `skl_int3472_register_regulator()` creates GPIO-enabled regulators with lower/upper-case supply aliases and optional second sensor consumer.

## Control Flow
GPIO resources parsed by `discrete.c` call into this file when a GPIO is a clock enable or power rail. Clocks toggle in `.prepare/.unprepare` because GPIO operations can sleep. Regulators use empty ops with `ena_gpiod` and status-change constraints.

## State And Persistence
State is embedded in `int3472_discrete_device`: clock handle, clkdev lookup, enable GPIO, regulator descriptors, supply maps, and registered regulator devices. Hardware GPIO/DSM state follows framework enable counts.

## Dependencies And Integration Points
Depends on ACPI DSM, clk provider/clkdev, GPIO descriptors, regulator core, and INT3472 platform data definitions.

## Risks And Test Signals
Risks include incorrect sensor name lookups, clock frequency read failures returning zero, supply-name length limits, duplicate clock registration, and GPIO ownership cleanup. Test sensor driver `clk_get()`, regulator consumer lookup with case variants, power sequencing delays, and cleanup after probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/clk_and_regulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/common.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/common.c

## Purpose
Shared INT3472 helper library for reading ACPI buffers and discovering dependent camera sensors.

## Important APIs, Types, And Functions
`skl_int3472_get_acpi_buffer()` evaluates an ACPI object such as `CLDB` or `SSDB` and verifies it is a buffer. `skl_int3472_fill_cldb()` copies the CLDB buffer into `struct int3472_cldb` with size validation. `skl_int3472_get_sensor_adev_and_name()` finds the next ACPI consumer device and formats its I2C device name.

## Control Flow
Both discrete and TPS68470 paths use CLDB to decide control logic type. Discrete probe uses the sensor discovery helper to build GPIO/clock/regulator lookup names.

## State And Persistence
The helpers allocate returned ACPI buffers that callers must free. Sensor ACPI references are passed to callers, which must release them when no longer needed.

## Dependencies And Integration Points
Depends on ACPI companion/consumer APIs, device-managed string allocation, and exported symbol namespace `INTEL_INT3472`.

## Risks And Test Signals
Risks include CLDB truncation semantics, missing dependents, and leaked ACPI references on failure paths. Test with absent CLDB, malformed CLDB, multiple consumers, and module namespace resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/discrete.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/discrete.c

## Purpose
Implements INT3472 devices whose camera power control is a set of discrete GPIOs and optional DSM-controlled clocks. It translates firmware GPIO descriptions into Linux sensor GPIO lookups, clocks, regulators, and LEDs.

## Important APIs, Types, And Functions
The file uses a GPIO DSM GUID to decode GPIO type, pin, and active value. `int3472_get_con_id_and_polarity()` maps firmware types and sensor-specific quirks to consumer names and polarity. `skl_int3472_handle_gpio_resources()` handles each ACPI GPIO resource, either mapping it to the sensor lookup table or consuming it to register a clock, regulator, privacy LED, or strobe LED. `int3472_discrete_parse_crs()` walks `_CRS`, registers DSM clock fallback, and adds the lookup table.

## Control Flow
Probe checks ACPI companion, applies DMI quirks, reads CLDB and requires `control_logic_type == 1`, allocates a flexible `int3472_discrete_device`, records clock source, discovers the sensor dependent device/name, initializes lookup-table state, parses GPIO resources, then clears ACPI dependencies so the sensor can probe.

## State And Persistence
State includes sensor ACPI reference/name, GPIO lookup table entries, registered clocks/regulators/LEDs, counted GPIOs, and quirks. Cleanup removes lookup tables and unregisters all framework objects.

## Dependencies And Integration Points
Depends on ACPI resource parsing, DMI quirks, gpiod machine lookups, GPIO descriptors, clk/regulator/LED helpers, and INT3472 common helpers.

## Risks And Test Signals
Risks include firmware DSM/resource mismatches, incorrect polarity inversion from sensor-on value, too many GPIOs, temporary lookup races, and missing cleanup on partial failures. Test representative sensors for reset/powerdown GPIO lookup, regulator enables, privacy LED registration, DSM and GPIO clocks, DMI quirk second-sensor supply, and sensor probe after dependencies are cleared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/discrete.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/discrete_quirks.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/discrete_quirks.c

## Purpose
Holds DMI quirks for INT3472 discrete devices.

## Important Data
Currently defines a Lenovo Miix 510-12IKB quirk that maps AVDD to a second sensor device name `i2c-OVTI2680:00`.

## Control Flow And State
`skl_int3472_discrete_quirks[]` is consulted by `discrete.c` probe. If matched, quirk data is copied into the runtime discrete device and later used when registering regulators.

## Dependencies And Integration Points
Depends on DMI matching and `struct int3472_discrete_quirks` from platform data headers.

## Risks And Test Signals
Risks are overly broad DMI matches or stale sensor names. Test on Lenovo Miix 510 to confirm both sensors receive the expected AVDD consumer supply and non-matching systems are unaffected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/discrete_quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/led.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/led.c

## Purpose
Registers GPIO-backed LED class devices for INT3472 privacy/strobe GPIOs and links them to camera sensor consumers.

## Important APIs, Types, And Functions
`int3472_led_set()` writes the brightness value to the GPIO. `skl_int3472_register_led()` creates a stable LED name from the sensor ACPI name and connection ID, registers an `led_classdev`, and adds an LED lookup for the sensor device. `skl_int3472_unregister_leds()` removes lookups, unregisters class devices, and releases GPIOs.

## Control Flow
`discrete.c` calls register for GPIO types privacy LED and strobe. The LED class callback controls the GPIO directly.

## State And Persistence
LED state is held in `int3472->leds[]` and the GPIO output state. Registered lookup entries persist until cleanup.

## Dependencies And Integration Points
Depends on LED class, GPIO descriptors, ACPI device names, and sensor driver LED lookup use.

## Risks And Test Signals
Risks are LED naming collisions, GPIO polarity mistakes, and missing lookup removal. Test LED sysfs brightness, sensor privacy LED lookup, and cleanup on module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/tps68470.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/tps68470.c

## Purpose
I2C driver for INT3472 devices backed by a TI TPS68470 camera PMIC. It initializes the PMIC regmap and creates MFD child devices appropriate for ChromeOS-style or Windows-style firmware.

## Important APIs, Types, And Functions
`tps68470_chip_init()` software-resets the chip and logs revision. `skl_int3472_tps68470_calc_type()` uses CLDB presence/control logic type to distinguish ChromeOS from Windows. `skl_int3472_fill_clk_pdata()` enumerates ACPI consumers and creates clock platform data. Probe adds MFD cells for either `tps68470-gpio` plus PMIC OpRegion or Windows clock/regulator/GPIO cells with board data.

## Control Flow
Probe requires an ACPI companion, builds clock consumer data, initializes an 8-bit regmap, resets the PMIC, determines device type, and then adds MFD children. Windows systems must match DMI/device-name board data; lookup tables are added before MFD child creation and removed if adding children fails. Remove removes board lookup tables if present.

## State And Persistence
Regmap is client data. MFD child devices own GPIO/regulator/clock runtime. Board-specific GPIO lookup tables are global objects installed while the driver is bound.

## Dependencies And Integration Points
Depends on I2C, ACPI, regmap, MFD core, TPS68470 subdrivers, INT3472 common helpers, board data, and gpiod lookup tables.

## Risks And Test Signals
Risks include CLDB misclassification, PMIC reset side effects, missing board data on Windows-designed systems, lookup-table lifetime, and MFD cell ordering. Test Surface Go, Dell 7212, MSI board data, ChromeOS OpRegion creation, child probe ordering, and camera power-up sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/tps68470.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/tps68470.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/tps68470.h

## Purpose
Declares board-data structures for INT3472 TPS68470 Windows-style platforms.

## Important APIs And Types
`struct int3472_tps68470_board_data` records the I2C device name to match, regulator platform data, optional GPIO software node, number of GPIO lookup tables, and a flexible array of lookup-table pointers. `int3472_tps68470_get_board_data()` returns matching board data for a device name.

## Control Flow And State
The header owns no storage. `tps68470.c` uses the lookup function to retrieve static data from `tps68470_board_data.c`.

## Dependencies And Integration Points
Depends on gpiod lookup tables, TPS68470 regulator platform data, and software nodes.

## Risks And Test Signals
Risks are ABI drift between board data and TPS68470 probe expectations. Test compile-time agreement and runtime board lookup on each DMI-supported device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/tps68470.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/tps68470_board_data.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/tps68470_board_data.c

## Purpose
Provides static regulator constraints, consumer supplies, GPIO lookup tables, software-node properties, and DMI mappings for Windows-designed TPS68470 INT3472 boards.

## Important APIs, Types, And Data
Defines board data for Microsoft Surface Go/Go 2, Surface Go 3, Dell Latitude 7212 Rugged Extreme Tablet, and MSI Prestige 14 AI+ Evo C2VMG. Regulator init data maps TPS68470 rails to camera sensor supplies with fixed voltage constraints. GPIO lookup tables map `tps68470-gpio` pins to sensor reset/powerdown/enable signals. MSI adds a GPIO software node property `daisy-chain-enable`.

## Control Flow
`int3472_tps68470_get_board_data()` iterates all DMI matches, compares each candidate `dev_name` to the active I2C client name, and returns the first exact match. `tps68470.c` then installs the lookup tables and passes regulator data to MFD cells.

## State And Persistence
All data is static. Lookup tables are registered and unregistered by `tps68470.c`.

## Dependencies And Integration Points
Depends on DMI, regulator machine constraints, GPIO machine lookups, TPS68470 platform data, and exact I2C ACPI device names.

## Risks And Test Signals
Risks include exact DMI/device-name mismatches, wrong rail voltages, missing always-on constraints, and GPIO pin drift between board revisions. Test each listed product for board-data selection, regulator voltage/consumer mapping, GPIO reset/powerdown behavior, and camera sensor probe success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/tps68470_board_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ishtp_eclite.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ishtp_eclite.c

## Purpose
ISHTP client driver that exposes ACPI OpRegion handlers for ECLite firmware running on Intel ISH/PSE. It lets AML read/write ECLite data and invoke DSM events for battery, thermal, fan, UCSI, and related platform functions.

## Important APIs, Types, And Functions
`struct ishtp_opregion_dev` stores opregion buffers, ISHTP client handles, ACPI device reference, flags, waitqueue, work items, and lock. `ecl_opregion_cmd_handler()` triggers ISH read/write commands from ACPI command-region writes. `ecl_opregion_data_handler()` reads/writes the shared 384-byte data region. `ecl_ish_cl_read()` sends a read header and waits up to 2 seconds for firmware response. RX callbacks distinguish data responses from event messages; events schedule `_DSM` calls.

## Control Flow
Late init registers an ISHTP client for ECLite UUID. Probe allocates and connects an ISHTP client, finds ACPI device `INTC1035`, registers event callback, installs command and data OpRegion handlers, then clears ACPI dependencies. ACPI writes command fields; writing the command offset sends ISHTP messages. Firmware data responses fill the opregion buffer and wake waiters. Firmware events schedule `ecl_acpi_invoke_dsm()`. Reset work tears down/recreates the ISHTP client and reinstalls opregions if needed.

## State And Persistence
State includes opregion command/data buffers, link readiness, read completion flag, installed-handler flag, DSM event id, and pending work. Suspend to Sx removes opregions and disables firmware events; resume relies on a later reset path.

## Dependencies And Integration Points
Depends on ISHTP client APIs, ACPI address-space handlers, ACPI DSM GUID, waitqueues, workqueues, and suspend state. Firmware and AML must agree on opregion IDs `0x9e` and `0x9f`.

## Risks And Test Signals
Risks include ISHTP reset races, blocking ACPI reads waiting on firmware, missing event disable errors, bitfield message layout, and handler removal during suspend. Test ACPI OpRegion read/write methods, firmware event-to-DSM path, reset recovery, suspend/resume, dependency reprobe of ECLite consumers, and malformed offsets/lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ishtp_eclite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/mrfld_pwrbtn.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/mrfld_pwrbtn.c

## Purpose
Reports the Merrifield Basin Cove PMIC power button through the Linux input subsystem.

## Important APIs, Types, And Functions
`mrfld_pwrbtn_interrupt()` reads `BCOVE_PBSTATUS`, reports `KEY_POWER` pressed when `BCOVE_PBSTATUS_PBLVL` is clear, syncs input, and unmasks the level-1 power-button interrupt. Probe registers an input device, requests a shared threaded IRQ, unmasks PMIC interrupt bits, and sets wake IRQ.

## Control Flow
Platform child `mrfld_bcove_pwrbtn` binds, obtains IRQ 0 and parent regmap, registers input, requests IRQ with `IRQF_ONESHOT | IRQF_SHARED`, unmasks PMIC interrupt levels, and enables wake.

## State And Persistence
Driver state is the input device and regmap pointer. PMIC interrupt masks and wake IRQ state persist while bound.

## Dependencies And Integration Points
Depends on Basin Cove PMIC MFD/regmap, input subsystem, PM wakeirq, and platform IRQ resources.

## Risks And Test Signals
Risks are polarity mismatch, failure to unmask nested PMIC interrupt bits, and shared IRQ noise. Test press/release events, suspend wake, IRQ sharing, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/mrfld_pwrbtn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/oaktrail.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/oaktrail.c

## Purpose
Legacy Intel OakTrail platform extras driver. It exposes EC-backed rfkill controls for WiFi, Bluetooth, GPS, and WWAN, and optionally a vendor backlight device.

## Important APIs, Types, And Functions
`oaktrail_rfkill_set()` reads EC device-state byte `0xd6`, toggles a radio bit, and writes it back. `oaktrail_rfkill_new()` allocates and registers rfkill devices. Backlight callbacks read/write EC brightness address `0x44` and control address `0x3a`. Module parameter `force` bypasses DMI gating.

## Control Flow
Module init requires ACPI and either DMI match `OakTrail platform` or `force=1`. It registers a platform driver/device, registers vendor backlight only when ACPI video selected vendor backlight type, then creates four rfkill devices. Cleanup unregisters backlight, rfkills, device, and driver.

## State And Persistence
Global pointers track the platform device, backlight, and rfkill devices. Hardware state persists in EC registers and is directly modified by callbacks.

## Dependencies And Integration Points
Depends on ACPI EC read/write helpers, DMI, rfkill, backlight, ACPI video backlight policy, platform device APIs, and module parameters.

## Risks And Test Signals
Risks include fixed EC offsets, weak rfkill initial-state expression, unconditional backlight cleanup even if not registered, and broad `force` usage. Test on OakTrail hardware for radio toggles, backlight brightness 0-100, DMI gating, unload paths, and ACPI video backlight coexistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/oaktrail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/plr_tpmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/plr_tpmi.c

## Purpose
Auxiliary driver for Intel TPMI Performance Limit Reasons. It exposes die-level and CPU-level throttling reason bits through debugfs and allows clearing them.

## Important APIs, Types, And Functions
`struct tpmi_plr` tracks debugfs root, die array, auxiliary device, notifier, and lock. `struct tpmi_plr_die` stores an MMIO base, package/die IDs, and mailbox lock. `plr_read_cpu_status()` and `plr_clear_cpu_status()` use the PLR mailbox with punit core numbers and poll `PLR_RUN_BUSY`. `plr_status_show()` prints die-level and per-CPU reason names. `plr_status_write()` accepts only boolean false/0 to clear status.

## Control Flow
Probe obtains TPMI platform data, TPMI debugfs parent, and MMIO resources, registers a TPMI notifier, maps each resource as one die/domain, creates `plr/domainN/status` for valid headers, and stores drvdata. Reads list die-level `cpus` reasons, then iterate `nr_cpu_ids` filtering by package and power-domain ID before mailbox reads. Writes clear die-level and all matching CPU statuses.

## State And Persistence
State includes debugfs dentries, mapped MMIO resources, mailbox locks, package/die IDs, and notifier registration. Hardware status bits persist until cleared through debugfs.

## Dependencies And Integration Points
Depends on auxiliary bus, Intel VSEC/TPMI APIs, TPMI power-domain helpers, debugfs, MMIO polling, topology, and notifier callbacks for `TPMI_CORE_EXIT`.

## Risks And Test Signals
Risks include mailbox timeout, stale debugfs during TPMI core teardown, CPU iteration over offline/unmapped CPUs, and write ABI accepting only zero. Test debugfs output per domain, clearing behavior, timeout handling, hotplug/power-domain mappings, and TPMI core unload notifier behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/plr_tpmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/Kconfig

## Purpose
Defines Intel PMC core and SSRAM telemetry support.

## Important Symbols
`INTEL_PMC_CORE` is a tristate depending on PCI, ACPI, and Intel PMT telemetry; it selects `INTEL_PMC_SSRAM_TELEMETRY`. `INTEL_PMC_SSRAM_TELEMETRY` is hidden and builds the SSRAM telemetry helper.

## Control Flow And State
Build selection enables the PMC core and a platform driver for accessing Intel Power Management Controller registers, S0ix residency, IP power-gating, LTR, low-power-mode, and platform-specific quirks.

## Dependencies And Integration Points
Depends on PCI, ACPI, PMT telemetry, and platform-specific register maps in the sibling Makefile.

## Risks And Test Signals
Risks are missing telemetry dependency or unintentional disabling of PMC diagnostics. Test with supported Intel platforms and verify debugfs/telemetry features are present when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/Makefile

## Purpose
Builds the Intel PMC core, platform driver, and SSRAM telemetry helper.

## Important Build Rules
`intel_pmc_core-y` links common core plus platform maps `spt.o`, `cnp.o`, `icl.o`, `tgl.o`, `adl.o`, `mtl.o`, `arl.o`, `lnl.o`, `ptl.o`, and `wcl.o`. `intel_pmc_core_pltdrv-y := pltdrv.o` builds the platform driver. `intel_pmc_ssram_telemetry-y += ssram_telemetry.o` builds telemetry support.

## Control Flow And State
Kbuild links all platform map tables into the core module so runtime ID matching can select the appropriate register map.

## Dependencies, Risks, And Test Signals
Risks are missing object additions for new SoCs or stale object names. Test targeted builds and ensure `adl_reg_map` and other map symbols resolve from `core.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/adl.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/adl.c

## Purpose
Provides Alder Lake PMC register maps and bit-name tables consumed by the shared Intel PMC core.

## Important APIs, Types, And Data
Static `pmc_bit_map` tables name PFET acknowledge bits, LTR sources, clock-source status, power-gating status groups, D3 status groups, VNN request status groups, and miscellaneous low-power-mode status bits. `adl_lpm_maps[]` orders the LPM status maps. `adl_reg_map` supplies offsets, counter steps, LTR ignore limits, map pointers, LPM register offsets, residency offsets, and read-disable metadata. `adl_pmc_dev` selects `adl_reg_map` with Cannon Lake suspend/resume hooks.

## Control Flow
There are no functions in this file. The PMC core selects `adl_pmc_dev` for Alder Lake class IDs, then uses the map tables to decode debugfs/status output, read residency counters, manage LTR ignore/show, and perform suspend/resume quirk handling.

## State And Persistence
All structures are static const except the exported `adl_pmc_dev` descriptor. Runtime state is held by the PMC core; hardware state lives in PMC MMIO/MSR registers described by these offsets and bit masks.

## Dependencies And Integration Points
Depends on `core.h` for register-offset constants, shared maps such as `msr_map` and `tgl_signal_status_map`, and shared suspend/resume functions `cnl_suspend`/`cnl_resume`.

## Risks And Test Signals
Risks are incorrect bit names, wrong offsets/counter steps, LPM map order mismatches, and inherited CNP/TGL constants that may not fit all Alder Lake variants. Test PMC debugfs decoding, S0ix and PSON residency counters, LTR ignore/show, LPM live/latch status, suspend/resume on Alder Lake systems, and compare against hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/adl.c -->
