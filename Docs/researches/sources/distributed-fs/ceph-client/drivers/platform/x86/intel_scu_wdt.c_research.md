<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_wdt.c

Purpose: platform-device library for Intel Merrifield/Tangier watchdog support. It registers an `intel_mid_wdt` platform device on matching Intel MID CPUs and fills watchdog platform data with an IOAPIC-mapped IRQ.

Important APIs/types/functions: static `wdt_dev` names the platform device. `tangier_probe()` maps GSI `TANGIER_EXT_TIMER0_MSI` to a Linux IRQ using `mp_map_gsi_to_irq()` and stores it in `struct intel_mid_wdt_pdata`. `intel_mid_cpu_ids` matches `INTEL_ATOM_SILVERMONT_MID` and supplies `tangier_pdata`. `register_mid_wdt()` runs at `arch_initcall`.

Control flow: early init matches CPU; if supported, assigns platform data to `wdt_dev` and registers it. The actual watchdog driver later binds `intel_mid_wdt` and calls the pdata probe hook. Exit unregisters the platform device.

State/persistence: static platform device and static platform data live for module/built-in lifetime. The mapped IRQ is stored in pdata after `tangier_probe()`.

Dependencies/integration: depends on x86 CPU matching, IOAPIC/GSI mapping, and `linux/platform_data/x86/intel-mid_wdt.h`. It is a hardware-description bridge, not the watchdog implementation.

Risks: assumes MID IOAPIC identity mapping behavior and GSI 12 for external timer 0. Unsupported CPUs simply return `-ENODEV`. If IOAPIC mapping fails, watchdog probe cannot get an IRQ.

Test signals: on Tangier/Merrifield-class CPU, an `intel_mid_wdt` platform device should appear; calling pdata probe should populate `irq`; unsupported CPUs should not register the device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_wdt.c -->
