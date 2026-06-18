<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/quirks.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/efi/quirks.c

## Purpose
Implements x86-specific EFI firmware workarounds for variable-store safety, boot-services memory lifetime, kexec configuration table reuse, reduced-hardware reset/poweroff selection, Quark capsule headers, and runtime-service fault containment.

## Important APIs, Types, And Functions
`efi_query_variable_store()` and `efivar_reserved_space()` protect nonvolatile EFI variable storage; `efi_arch_mem_reserve()`, `efi_reserve_boot_services()`, `efi_unmap_boot_services()`, and `efi_free_boot_services()` manage EFI boot-services memory; `efi_reuse_config()` repairs kexec configuration tables; `efi_reboot_required()` and `efi_poweroff_required()` select EFI reset/poweroff fallbacks; `efi_capsule_setup_info()` handles Quark security headers when enabled; `efi_crash_gracefully_on_page_fault()` disables broken runtime services after firmware page faults.

## Control Flow
Early parameters can disable storage paranoia. Variable writes first query firmware free space, optionally force garbage collection through a dummy variable, and return EFI errors before callers write. EFI boot-services descriptors are reserved during init, runtime-tagged if not safely owned, unmapped after virtual mapping setup, queued in `ranges_to_free`, and finally released by an `arch_initcall`. Runtime faults in the EFI workqueue either redirect reset to BIOS or abort the waiting caller and park the worker forever.

## State And Persistence
The file touches persistent EFI NVRAM variables through `set_variable*`. It rewrites the in-kernel EFI memory map and E820 reservations during boot and stores freeable ranges until `efi_free_boot_services()`. Quark capsule setup mutates `capsule_info` metadata, and runtime-service fault handling clears `EFI_RUNTIME_SERVICES`.

## Dependencies And Integration Points
Depends on EFI core services, x86 E820/memblock, ACPI reduced-hardware state, DMI, UV headers, real-mode trampoline allocation, kexec setup data, capsule update code, and the EFI runtime workqueue. Drivers needing boot-services data integrate through `efi_mem_reserve()`, which this file supports by splitting descriptors.

## Risks And Edge Cases
Incorrect descriptor splitting or ownership tagging can free firmware, kernel, crash-kernel, or driver-owned memory. Variable-store arithmetic is sensitive to firmware reporting bugs and underflow-style cases around `remaining_size - size`. Runtime page-fault recovery is intentionally drastic and must avoid running in interrupt/NMI context. Quark capsule pointer adjustments assume the first buffer contains enough signed-header bytes.

## Test Signals
Boot logs for EFI boot-services freeing, NVRAM write failures, kexec boot across EFI, capsule update on Quark, and fault-injection around EFI runtime calls are the main signals. Memory-map regressions show up as early boot crashes, missing SMBIOS after kexec, or firmware reset/poweroff failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/runtime-map.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/efi/runtime-map.c

## Purpose
Exports the active EFI runtime memory map through sysfs and provides helper APIs for copying the map to other kernel consumers.

## Important APIs, Types, And Functions
`struct efi_runtime_map_entry` wraps an `efi_memory_desc_t` in a kobject. `map_attribute` and the generated show functions expose `type`, `phys_addr`, `virt_addr`, `num_pages`, and `attribute`. `efi_get_runtime_map_size()`, `efi_get_runtime_map_desc_size()`, and `efi_runtime_map_copy()` are programmatic accessors.

## Control Flow
At `subsys_initcall_sync`, the initializer exits if EFI memory maps or `efi_kobj` are absent. It allocates a pointer array, creates the `runtime-map` kset under the EFI kobject, and adds numbered child kobjects for each descriptor. Attribute reads format descriptor fields as hexadecimal strings.

## State And Persistence
The sysfs hierarchy persists until shutdown and holds heap copies of EFI descriptors. The source of truth remains `efi.memmap`; `efi_runtime_map_copy()` copies from that live map, not the per-kobject snapshots.

## Dependencies And Integration Points
Integrates with EFI core, sysfs/kobject lifecycle, and `/sys/firmware/efi/runtime-map`. Kexec and diagnostic users can use the exported copy helpers.

## Risks And Edge Cases
Partial sysfs creation unwinds only created kobjects; kset lifetime errors can leak or remove the whole map. The copy helper silently truncates to caller buffer size. Descriptor values are read-only and not synchronized against later EFI memory-map replacement.

## Test Signals
Presence of `/sys/firmware/efi/runtime-map/N/*` with sane descriptor values, successful boot without kobject warnings, and consumers receiving a descriptor-size-aligned map validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/runtime-map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/geode/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/geode/Makefile

## Purpose
Builds AMD Geode board support helpers and board detectors for ALIX, net5501, and GEOS platforms.

## Important APIs, Types, And Functions
Build targets are `geode-common.o`, `alix.o`, `net5501.o`, and `geos.o`, each gated by its Kconfig symbol.

## Control Flow
Kbuild links only selected board files into the kernel. `geode-common.o` supplies shared platform-device helpers used by the board-specific initcalls.

## State And Persistence
No runtime state is stored here; the file controls object inclusion.

## Dependencies And Integration Points
Depends on `CONFIG_GEODE_COMMON`, `CONFIG_ALIX`, `CONFIG_NET5501`, and `CONFIG_GEOS`, plus the broader x86 platform build.

## Risks And Edge Cases
Missing `GEODE_COMMON` with a selected board file would break symbol resolution. Over-selecting board files only adds detection initcalls, which self-filter on Geode hardware and board identity.

## Test Signals
Build coverage for each config combination and successful link of board objects are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/geode/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/geode/alix.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/geode/alix.c

## Purpose
Detects PC Engines ALIX Geode boards and registers GPIO-backed LEDs and restart key support.

## Important APIs, Types, And Functions
`alix_present()` scans TinyBIOS/coreboot physical BIOS regions for ALIX signatures, `alix_present_dmi()` recognizes DMI identifiers, and `register_alix()` calls `geode_create_restart_key(24)` plus `geode_create_leds()` for pins 6, 25, and 27. The `force` module parameter bypasses BIOS matching.

## Control Flow
The `device_initcall` exits on non-Geode CPUs. Otherwise it checks TinyBIOS, coreboot, then DMI signatures; any match registers platform devices through the shared Geode helpers.

## State And Persistence
State consists of boot-time software nodes and platform devices for `gpio-keys-polled` and `leds-gpio`. The `force` parameter is read-only after boot.

## Dependencies And Integration Points
Uses `is_geode()`, DMI, physical BIOS mapping via `phys_to_virt()`, and `geode-common` software-node registration. It relies on the cs5535 GPIO provider to satisfy named GPIO references.

## Risks And Edge Cases
Signature scanning assumes accessible low BIOS mappings and can miss Award BIOS without `force`. False positives could register controls on the wrong machine. GPIO pin assumptions are board-model-specific.

## Test Signals
Boot log recognition messages, visible ALIX LEDs in the LED class, and a working restart key through input events validate the path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/geode/alix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/geode/geode-common.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/geode/geode-common.c

## Purpose
Provides shared Geode board helpers that describe GPIO keys and LEDs using software nodes and create platform devices for generic `gpio-keys-polled` and `leds-gpio` drivers.

## Important APIs, Types, And Functions
`geode_create_restart_key()` registers the cs5535 GPIO chip node, a `gpio-keys` parent, and a restart-key child with `KEY_RESTART`. `geode_create_leds()` builds per-LED software nodes with `gpios` and `linux,default-trigger` properties. `struct geode_led` is declared in the companion header.

## Control Flow
Board files call the restart-key helper first so the shared GPIO chip software node exists, then call LED creation. Allocation builds node arrays, property arrays, and GPIO references; registration creates platform devices; error paths unregister nodes and free allocated names/properties.

## State And Persistence
Software-node groups and platform devices remain registered after boot. LED node names are allocated dynamically and intentionally retained on success because the software-node/device lifetime needs them.

## Dependencies And Integration Points
Integrates Linux software nodes, GPIO lookup by fwnode, input key codes, LED class triggers, and platform-device registration. Consumers are ALIX, GEOS, and net5501 board files.

## Risks And Edge Cases
The helper supports only `MAX_LEDS` of 3; exceeding it returns `-EINVAL`. Success paths do not provide teardown because callers are built-in init code. Ordering matters for shared GPIO node registration.

## Test Signals
Successful creation of `gpio-keys-polled` and `leds-gpio` devices, absence of software-node registration errors, and functioning LED triggers/key events indicate correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/geode/geode-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/geode/geode-common.h -->
# sources/distributed-fs/ceph-client/arch/x86/platform/geode/geode-common.h

## Purpose
Declares the shared API used by Geode board-specific setup files to create GPIO LEDs and restart keys.

## Important APIs, Types, And Functions
`struct geode_led` carries a GPIO pin and default-on flag. `geode_create_restart_key()` and `geode_create_leds()` are exported to sibling compilation units.

## Control Flow
The header has no runtime flow; it defines the compile-time contract between board detectors and `geode-common.c`.

## State And Persistence
No state is stored in the header. Callers pass static `__initconst` LED arrays.

## Dependencies And Integration Points
Includes Linux property definitions and is included by ALIX, GEOS, net5501, and the common implementation.

## Risks And Edge Cases
Signature drift between declarations and implementation would break builds. The small API deliberately hides software-node details from board files.

## Test Signals
Successful compilation of all Geode board objects is the direct validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/geode/geode-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/geode/geos.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/geode/geos.c

## Purpose
Detects Traverse Technologies GEOS Geode systems and registers their GPIO LEDs and restart key.

## Important APIs, Types, And Functions
`geos_init()` checks `is_geode()`, DMI vendor `Traverse Technologies`, and product `Geos`. `register_geos()` registers restart GPIO pin 3 and LEDs on pins 6, 25, and 27.

## Control Flow
The `device_initcall` self-filters by CPU and DMI, logs recognition, and delegates all device creation to `geode-common`.

## State And Persistence
Runtime state is the created software-node/platform-device graph for GPIO keys and LEDs.

## Dependencies And Integration Points
Uses DMI, `asm/geode.h`, and the shared Geode helper. Downstream integration is through generic GPIO, input, and LED subsystems.

## Risks And Edge Cases
Requires exact DMI strings, so firmware changes can prevent detection. Incorrect pin mapping would expose nonfunctional or wrong controls.

## Test Signals
Boot log recognition, LED class entries named with `geos`, and an input restart key are expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/geode/geos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/geode/net5501.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/geode/net5501.c

## Purpose
Detects Soekris net5501 boards and registers their GPIO LED and restart key.

## Important APIs, Types, And Functions
`net5501_present()` maps the top BIOS region, validates the `comBIOS` signature, and checks known model offsets. `register_net5501()` creates restart key pin 24 and one default-on LED on pin 6.

## Control Flow
The `device_initcall` exits on non-Geode systems, scans BIOS strings, then creates generic GPIO input/LED platform devices on match.

## State And Persistence
The BIOS mapping is temporary. Registered platform devices and software nodes persist after boot.

## Dependencies And Integration Points
Uses `ioremap()` for firmware ROM inspection, `is_geode()`, and `geode-common`. It integrates with cs5535 GPIO, input, and LED subsystems.

## Risks And Edge Cases
Firmware signature offsets are version-specific and may miss unknown BIOS versions. Mapping size uses `BIOS_REGION_SIZE - 1`, so changes around region boundary assumptions should be treated carefully.

## Test Signals
Recognition logs, `net5501` LED registration, and restart-key input events are the practical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/geode/net5501.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-mid/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/intel-mid/Makefile

## Purpose
Builds Intel MID platform setup and PWRMU support when `CONFIG_X86_INTEL_MID` is enabled.

## Important APIs, Types, And Functions
The object list is `intel-mid.o pwr.o`.

## Control Flow
Kbuild includes both early platform override code and PCI PWRMU code as a unit for Intel MID kernels.

## State And Persistence
No runtime state exists in the Makefile.

## Dependencies And Integration Points
Depends on x86 platform selection and the Intel MID PCI/power-management code that consumes symbols from these objects.

## Risks And Edge Cases
Splitting the two objects under different symbols would risk missing power-off or PCI platform PM hooks. Current coupling keeps the platform coherent.

## Test Signals
Successful build with `CONFIG_X86_INTEL_MID=y` and link resolution for Intel MID PM symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-mid/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-mid/intel-mid.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/intel-mid/intel-mid.c

## Purpose
Overrides generic x86 initialization for Intel MID/Moorestown-style systems and installs platform-specific reboot and poweroff paths.

## Important APIs, Types, And Functions
`x86_intel_mid_early_setup()` rewires `x86_init`, `x86_platform`, `legacy_pic`, PCI init hooks, and reboot/poweroff handlers. `intel_mid_power_off()` combines PWRMU S5 command with SCU IPC cold-off, and `intel_mid_reboot()` sends SCU cold-reset.

## Control Flow
Early setup disables ROM/resource probing, MP table parsing, legacy PIC use, IO-APIC IRQ fixups, and generic ACPI reduced-hardware init. It selects LAPIC clockevent setup and marks the ISA bus as not PCI. Later shutdown paths call PWRMU/SCU helpers.

## State And Persistence
Mutates global x86 platform operation tables, `pm_power_off`, `machine_ops.emergency_restart`, and legacy PIC selection for the life of the boot.

## Dependencies And Integration Points
Depends on Intel SCU IPC, APIC clock setup, Intel MID PCI initialization, regulator constraints, and PWRMU exports from `pwr.c`.

## Risks And Edge Cases
These global overrides are only safe on true Intel MID platforms. Incorrect detection would disable standard discovery and interrupt paths. Poweroff assumes PWRMU is available before falling through to SCU IPC command handling.

## Test Signals
Boot on Intel MID without MP table probing failures, LAPIC timer operation, PCI enumeration through Intel MID arch init, and working SCU reset/poweroff are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-mid/intel-mid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-mid/pwr.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/intel-mid/pwr.c

## Purpose
Implements the Intel MID Power Management Unit driver used to set South Complex PCI device power states and trigger system S5 poweroff.

## Important APIs, Types, And Functions
`struct mid_pwr` holds MMIO registers, IRQ, mutex, availability flag, and Logical SubSystem cache. Exports include `intel_mid_pci_set_power_state()`, `intel_mid_pci_get_power_state()`, `intel_mid_pwr_power_off()`, and `intel_mid_pwr_get_lss_id()`. Probe supports Penwell and Tangier IDs with SoC-specific initial state tables.

## Control Flow
PCI probe enables the PWRMU device, maps BAR0, disables interrupts, initializes all wake/power state registers, requests an IRQ, and publishes the singleton `midpwr`. Power-state changes map PCI vendor capability LSS IDs to 2-bit PM state fields, compute the weakest shared-device state, write SSC registers, issue `CMD_SET_CFG`, and poll PM busy clear.

## State And Persistence
The singleton `midpwr` and `lss` cache persist after probe. Hardware PM registers store current wake and power settings. The mutex serializes all register updates.

## Dependencies And Integration Points
Integrates with `drivers/pci/pci-mid.c` platform PM hooks, PCI config vendor capabilities, MMIO PWRMU registers, IRQ subsystem, and Intel MID platform poweroff code.

## Risks And Edge Cases
`intel_mid_pci_set_power_state()` logs failures but returns 0, matching PCI hook expectations but hiding hardware errors from callers. Shared LSS cache has only four device slots. Busy polling can stall for 500 ms. Poweroff dereferences `midpwr` and assumes probe completed.

## Test Signals
PCI runtime suspend/resume on South Complex devices, correct PM_SSS bit transitions, no unexpected IRQ storms, and successful S5 on MID hardware validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-mid/pwr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-quark/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/intel-quark/Makefile

## Purpose
Builds Intel Quark Isolated Memory Region support and optional debug selftests.

## Important APIs, Types, And Functions
`imr.o` is selected by `CONFIG_INTEL_IMR`; `imr_selftest.o` is selected by `CONFIG_DEBUG_IMR_SELFTEST`.

## Control Flow
Kbuild includes the IMR driver and, optionally, the selftest initcall.

## State And Persistence
No runtime state is stored here.

## Dependencies And Integration Points
Depends on the Intel Quark platform and IOSF MBI driver that the IMR implementation uses.

## Risks And Edge Cases
Enabling selftests on production hardware can temporarily create and remove IMRs, so the debug symbol should stay opt-in.

## Test Signals
Builds with and without `CONFIG_DEBUG_IMR_SELFTEST` should link cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-quark/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-quark/imr.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/intel-quark/imr.c

## Purpose
Provides Intel Quark X1000 Isolated Memory Region management, protecting selected physical ranges from non-CPU system-agent access.

## Important APIs, Types, And Functions
`struct imr_device` stores init state, lock, register base, and count. `struct imr_regs` mirrors address/mask registers. Exported APIs are `imr_add_range()` and `imr_remove_range()`. Internal helpers read/write IOSF MBI registers, validate 1 KiB alignment, detect overlaps, clear entries, expose debugfs state, and build a kernel text/rodata IMR at init.

## Control Flow
`device_initcall` matches Quark and IOSF availability, initializes the device, registers debugfs, clears unlocked firmware/grub IMRs, and protects kernel `.text` through `__end_rodata`. Adding a range validates alignment/nonzero size, converts size to IMR raw encoding, rejects disabled all-access zero ranges and overlaps, chooses a free register, then writes address and masks. Removal finds by index or exact address range and writes the disabled encoding.

## State And Persistence
IMR state is persistent hardware register state until firmware reset or later writes. The driver keeps only lock/init metadata in RAM. Debugfs reads live hardware state.

## Dependencies And Integration Points
Requires `iosf_mbi_read/write()`, Quark CPU matching, `asm/imr.h` mask constants, kernel section boundaries, and debugfs.

## Risks And Edge Cases
Failed IOSF writes can leave partial IMR state and cause system resets on later memory access. Overlap detection checks base/end inside existing ranges but not all possible containment forms. Locked firmware IMRs cannot be removed. Alignment and raw-size handling must preserve the hardware's inclusive high-address encoding.

## Test Signals
Debugfs `imr_state`, boot log showing kernel text protection, selftest pass/fail output, and absence of random resets under DMA-heavy IO are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-quark/imr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-quark/imr_selftest.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/intel-quark/imr_selftest.c

## Purpose
Runs boot-time sanity tests for the Quark IMR public API when debug selftesting is enabled.

## Important APIs, Types, And Functions
`imr_self_test()` calls `imr_add_range()` and `imr_remove_range()` across invalid, overlapping, CPU-only, and all-access cases. `imr_self_test_result()` logs pass/fail and warns on failures.

## Control Flow
The `device_initcall` runs only on Quark X1000. Tests verify zero-size rejection, overlap rejection around the protected kernel range, disabled reserved encoding rejection, valid 1 KiB CPU-only add/remove, and valid 2 KiB all-access add/remove.

## State And Persistence
The selftest temporarily mutates IMR hardware registers for test ranges and removes successful test ranges before returning.

## Dependencies And Integration Points
Depends on `imr.c` having initialized successfully, kernel section boundaries, Quark CPU matching, and IMR mask definitions.

## Risks And Edge Cases
Running tests against live hardware protection is intrusive. A failing teardown can leave an IMR installed. Tests assume the kernel text IMR already exists so overlap checks fail.

## Test Signals
Boot logs prefixed with the module name show pass/fail lines; warnings indicate API regressions or hardware/IOSF failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-quark/imr_selftest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/intel/Makefile

## Purpose
Builds Intel IOSF sideband mailbox support.

## Important APIs, Types, And Functions
`iosf_mbi.o` is selected by `CONFIG_IOSF_MBI`.

## Control Flow
Kbuild adds the mailbox accessor driver to the x86 Intel platform directory when configured.

## State And Persistence
No runtime state exists in this Makefile.

## Dependencies And Integration Points
The resulting object provides exported IOSF MBI symbols used by Quark IMR and other Atom/SoC drivers.

## Risks And Edge Cases
Consumers that depend on IOSF MBI need this symbol selected or loaded; otherwise platform features fail at runtime.

## Test Signals
Kernel link coverage and module/object build with `CONFIG_IOSF_MBI` enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel/iosf_mbi.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/intel/iosf_mbi.c

## Purpose
Implements PCI-enumerated Intel IOSF sideband mailbox access and PMIC I2C bus arbitration between the kernel and P-Unit.

## Important APIs, Types, And Functions
Exports `iosf_mbi_read()`, `iosf_mbi_write()`, `iosf_mbi_modify()`, `iosf_mbi_available()`, `iosf_mbi_punit_acquire/release()`, `iosf_mbi_block_punit_i2c_access()`, notifier registration helpers, and `iosf_mbi_assert_punit_acquired()`. The PCI probe stores the singleton `mbi_pdev` and SoC semaphore address.

## Control Flow
Mailbox calls form MCR/MCRX values, serialize PCI config transactions with a spinlock, and reject GFX port access. PMIC arbitration waits for P-Unit users, notifies atomic-context users, blocks deep CPU idle via latency QoS, requests the P-Unit semaphore, polls for acknowledgement, and resets state on error. Unblock releases the semaphore and wakes waiters.

## State And Persistence
Global state includes `mbi_pdev`, the spinlock, PMIC access counts, semaphore address/acquired timestamp, notifier chain, waitqueue, and PM QoS request. Debugfs state exists only under `CONFIG_IOSF_MBI_DEBUG`.

## Dependencies And Integration Points
Uses PCI config-space offsets from `asm/iosf_mbi.h`, PCI IDs for Bay Trail/Braswell/Quark/Tangier, CPU latency QoS, blocking notifiers, debugfs, and CAP_SYS_RAWIO for raw debug transactions.

## Risks And Edge Cases
Misbalanced P-Unit/I2C acquire counts can deadlock PMIC access. Semaphore timeout resets the hardware semaphore and may leave callers surprised. MBI is not hot-pluggable and has no PCI remove path. Debugfs raw access can alter sideband registers and is permission-sensitive.

## Test Signals
Successful PCI probe, IOSF consumers returning non-`-ENODEV`, PMIC I2C transactions without SoC hangs under idle load, and debugfs access under debug builds validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel/iosf_mbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/iris/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/iris/Makefile

## Purpose
Builds Eurobraille Iris platform poweroff support.

## Important APIs, Types, And Functions
`iris.o` is selected by `CONFIG_X86_RDC321X`.

## Control Flow
Kbuild links the Iris platform driver only for the configured x86 platform.

## State And Persistence
No runtime state exists in the Makefile.

## Dependencies And Integration Points
Integrates with platform driver/module infrastructure through `iris.c`.

## Risks And Edge Cases
The Kconfig dependency must match the rare hardware needing this handler; otherwise the module is unavailable or unnecessarily built.

## Test Signals
Build and module load coverage for the selected config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/iris/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/iris/iris.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/iris/iris.c

## Purpose
Installs a custom `pm_power_off` handler for Eurobraille Iris machines that lack APM/ACPI shutdown.

## Important APIs, Types, And Functions
`iris_power_off()` writes a two-step pulse/rest sequence to I/O ports `0x341`. `iris_probe()` validates input port `0x340` unless `force` already allowed device creation, saves `old_pm_power_off`, and installs the handler. Module init registers a platform driver and synthetic platform device only when `force=1`.

## Control Flow
Module init requires `force` and then creates the platform device. Probe reads the GIO input port; `0xff` means likely absent and aborts. Remove restores the previous poweroff function and unregisters device/driver state.

## State And Persistence
Stores the previous global poweroff hook and the registered platform device pointer. The poweroff operation itself is hardware I/O and does not persist in memory.

## Dependencies And Integration Points
Uses platform-device infrastructure, legacy x86 I/O port access, sleep delays, and the global `pm_power_off` hook.

## Risks And Edge Cases
The module is intentionally force-gated because probing is weak and I/O writes are board-specific. It overwrites a global poweroff hook and restore ordering matters if another handler changes it concurrently.

## Test Signals
Module load with `force=1`, log messages for handler install/uninstall, and physical poweroff sequencing on Iris hardware validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/iris/iris.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/olpc/Makefile

## Purpose
Builds OLPC platform core, OpenFirmware/device-tree support, XO-1 power/RTC/SCI support, XO-1.5 SCI support, and low-level wakeup assembly.

## Important APIs, Types, And Functions
Objects include `olpc.o`, `olpc_ofw.o`, `olpc_dt.o`, `olpc-xo1-pm.o`, `xo1-wakeup.o`, `olpc-xo1-rtc.o`, `olpc-xo1-sci.o`, and `olpc-xo15-sci.o`, controlled by the corresponding OLPC Kconfig symbols.

## Control Flow
Kbuild includes platform-core objects for `CONFIG_OLPC` and then adds model-specific features by config.

## State And Persistence
No runtime state is in the Makefile; object selection determines which initcalls and platform drivers exist.

## Dependencies And Integration Points
Integrates OLPC code with x86 platform, PM, RTC, ACPI, input, EC, and OpenFirmware paths.

## Risks And Edge Cases
Model-specific object selection affects wake capability. For example XO-1 EC wakeups depend on XO-1 SCI support, and XO-1 suspend depends on wakeup assembly being linked.

## Test Signals
Config matrix builds for base OLPC, XO-1 PM/RTC/SCI, and XO-1.5 SCI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo1-pm.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo1-pm.c

## Purpose
Implements XO-1 suspend-to-RAM wake mask programming and CS5536-based poweroff.

## Important APIs, Types, And Functions
Exports `olpc_xo1_pm_wakeup_set()` and `olpc_xo1_pm_wakeup_clear()` to let RTC/SCI code alter `wakeup_mask`. `xo1_power_state_enter()` invokes `do_olpc_suspend_lowlevel()`. `xo1_do_sleep()` programs wake enables and calls the OpenFirmware BIOS entry. `xo1_power_off()` writes CS5536 PM registers.

## Control Flow
Two platform drivers collect PMS and ACPI base I/O resources. Once both bases are known on an OLPC machine, the driver installs suspend ops and `pm_power_off`. Suspend saves SCI mask, enters low-level assembly, resumes, and restores the mask.

## State And Persistence
Stores `acpi_base`, `pms_base`, and `wakeup_mask`. Hardware PM registers hold wake configuration across sleep entry.

## Dependencies And Integration Points
Depends on CS5536 register definitions, OLPC machine detection, OLPC OpenFirmware entry, generic suspend ops, and sibling XO-1 SCI/RTC wake-mask users.

## Risks And Edge Cases
Only `PM_SUSPEND_MEM` is valid. Calling firmware with inline assembly is fragile and 32-bit-specific. Remove sets `pm_power_off = NULL` rather than restoring a prior handler.

## Test Signals
XO-1 suspend/resume, wake by power button/RTC/lid as configured, and poweroff register sequencing are key validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo1-pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo1-rtc.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo1-rtc.c

## Purpose
Registers the XO-1 CMOS RTC platform device with OLPC-specific alarm register offsets and wake hooks.

## Important APIs, Types, And Functions
`rtc_wake_on()` and `rtc_wake_off()` manipulate XO-1 PM wake mask bit `CS5536_PM_RTC`. `xo1_rtc_init()` checks for an `olpc,xo1-rtc` device-tree node, reads MSR alarm offsets into `cmos_rtc_board_info`, registers `rtc_cmos`, disables legacy RTC probing, and marks wakeup enabled.

## Control Flow
At `arch_initcall`, the driver exits unless the OF device node exists. It then populates resources for RTC ports and IRQ8, registers the device, and updates x86 legacy RTC state.

## State And Persistence
Stores RTC board info in static data and creates a persistent platform device. Wake state is reflected in XO-1 PM wake mask.

## Dependencies And Integration Points
Depends on OF device-tree fixups, CMOS RTC driver, OLPC XO-1 PM exports, MSR alarm-offset registers, and x86 legacy RTC flags.

## Risks And Edge Cases
Missing device-tree compatibility prevents registration. Incorrect MSR values can break alarm fields. Wake hooks require XO-1 PM support to be linked.

## Test Signals
`rtc_cmos` platform device, `/dev/rtc*`, alarm wake from suspend, and `x86_platform.legacy.rtc=0` behavior validate the file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo1-rtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo1-sci.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo1-sci.c

## Purpose
Handles XO-1 System Control Interrupts, EC event queues, lid/ebook/power input devices, and suspend wake policy.

## Important APIs, Types, And Functions
Key paths are `process_sci_queue()`, `xo1_sci_intr()`, `xo1_sci_suspend/resume()`, `setup_sci_interrupt()`, `setup_ec_sci()`, `setup_lid_events()`, and input setup/free helpers. The `lid_wake_mode` sysfs attribute selects always/open/close wake behavior.

## Control Flow
Probe validates OLPC hardware, records ACPI base, creates three input devices, configures lid and EC GPIO/PME routing, clears pending status, synchronizes switch state, requests the SCI IRQ, and enables EC events. IRQ handling clears PM/GPE status, reports power/RTC wake, schedules EC queue work, and updates lid state. Suspend adjusts PM/EC/GPIO wake sources; resume reinitializes lid/EC state and notifies battery/AC supplies.

## State And Persistence
Static state tracks ACPI base, input device pointers, SCI IRQ, lid state/inversion, and lid wake mode. EC wake masks and CS5536 GPIO/PM registers persist in hardware.

## Dependencies And Integration Points
Integrates OLPC EC commands, CS5535 GPIO/PIC helpers, power-supply notifications, input subsystem, platform driver PM callbacks, and XO-1 PM wake-mask exports.

## Risks And Edge Cases
The lid edge workaround depends on GPIO input inversion and must not lose transitions. EC commands can time out in workqueue context. Error unwinding must unregister only initialized devices. Suspend wake policy can miss desired close/open events if `lid_wake_mode` and current lid state are miscomputed.

## Test Signals
Input events for power, lid, and tablet mode; battery/AC refresh on SCI; wake from configured sources; and no stuck SCI/GPIO status bits validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo1-sci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo15-sci.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo15-sci.c

## Purpose
Implements XO-1.5 ACPI-backed SCI handling for EC events and custom lid wake-on-close behavior.

## Important APIs, Types, And Functions
`set_lid_wake_behavior()` calls ACPI method `\_SB.PCI0.LID.LIDW`. `xo15_sci_add()` evaluates `_GPE`, installs a GPE handler, creates `lid_wake_on_close` sysfs, drains EC events, enables EC masks and GPE wake. `process_sci_queue()` updates OLPC battery/AC power supplies.

## Control Flow
The ACPI driver binds HID `XO15EC`. Add installs the edge-triggered GPE handler, creates sysfs, drains pending SCI data, enables all EC events, enables the GPE, and marks wake capability. GPE handler schedules work and reenables the GPE. Remove disables GPE, removes handler/sysfs, and cancels work. Resume re-enables EC masks and refreshes power supplies.

## State And Persistence
Stores the GPE number and current lid-wake-on-close flag. The sysfs attribute persists with the ACPI device. ACPI firmware stores the actual wake behavior.

## Dependencies And Integration Points
Depends on ACPI device enumeration, OLPC EC query/mask APIs, power-supply class, and the XO-1.5 DSDT custom method.

## Risks And Edge Cases
Failure to remove a GPE handler can leave callbacks after device removal. `set_lid_wake_behavior()` returns 1 on ACPI failure rather than a negative errno. The custom ACPI method is firmware-specific.

## Test Signals
ACPI driver binding to `XO15EC`, functioning `lid_wake_on_close` sysfs, EC battery/AC updates, and wake from EC GPE validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc-xo15-sci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc.c

## Purpose
Provides OLPC platform detection, EC command transport, EC suspend/resume behavior, and registration of OLPC platform devices.

## Important APIs, Types, And Functions
Exports `olpc_platform_info`. `olpc_xo1_ec_cmd()` implements port `0x6c/0x68` EC command protocol with IBF/OBF waits and OBF restart retries. `platform_detect()` checks OF root architecture and board revision. `olpc_init()` registers model-specific EC drivers, `olpc-ec`, XO-1 devices, DCON flags, and optional PCI init override.

## Control Flow
Boot parameter `olpc_ec_timeout=` adjusts command timeouts. `postcore_initcall` requires OFW presence and OLPC architecture, then chooses XO-1 vs XO-1.5 EC driver based on board revision. XO-1 EC suspend inhibits SCIs; resume releases inhibition and wakes WLAN twice.

## State And Persistence
Global `olpc_platform_info` records board revision and feature flags. `ec_timeout` persists from boot parameter. EC command effects and registered platform devices persist across runtime.

## Dependencies And Integration Points
Depends on OpenFirmware/device-tree availability, OLPC EC core, Geode/VSA PCI support, DCON users, platform devices, and x86 PCI init hooks.

## Risks And Edge Cases
The EC protocol is timing-sensitive and uses busy millisecond waits. OBF timeouts can restart commands up to ten times. Board revision gates many downstream devices, so incorrect DT properties misconfigure the platform.

## Test Signals
OLPC board revision logs, successful `olpc-ec` registration, EC command success, XO-1 rfkill/platform devices, and suspend/resume EC behavior are main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc_dt.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc_dt.c

## Purpose
Builds a Linux OpenFirmware-style device tree from OLPC OFW callbacks and applies compatibility fixups for older firmware.

## Important APIs, Types, And Functions
`prom_olpc_ops` supplies `of_pdt` callbacks for sibling/child/property/path traversal. `prom_early_alloc()` allocates boot memory for the tree. `olpc_dt_fixup()` adds battery, DCON, and RTC compatible nodes via OFW `interpret`. `olpc_dt_build_devicetree()` performs fixups and calls `of_pdt_build_devicetree()`.

## Control Flow
The builder exits if OFW is absent. It fixes the live firmware tree based on board revision and existing compatible markers, gets the root node, then recursively builds the Linux device tree through OFW client interface calls.

## State And Persistence
Tracks bytes allocated during boot in `prom_early_allocated`. Fixups mutate the firmware device tree before Linux imports it. The resulting Linux OF tree persists after init.

## Dependencies And Integration Points
Uses OLPC OFW client calls, memblock, `of_pdt`, OLPC board revision helpers, and later OLPC drivers that match compatible strings such as `olpc,xo1-rtc`.

## Risks And Edge Cases
OFW callback failures can produce incomplete DTs. Property buffers are small for compatibility strings. Firmware tree mutation via interpreted Forth words is brittle and board-revision-specific.

## Test Signals
Boot log reporting PROM DT memory use, presence of expected OF nodes/compatibles, and successful binding of RTC/DCON/battery drivers validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc_dt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc_ofw.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc_ofw.c

## Purpose
Detects and calls OLPC OpenFirmware from x86 Linux, including preserving its page-directory mapping.

## Important APIs, Types, And Functions
`olpc_ofw_detect()` validates the boot header and records the client interface pointer. `setup_olpc_ofw_pgd()` copies OFW's PDE into `swapper_pg_dir`. `__olpc_ofw()` serializes client-interface calls. `olpc_ofw_present()` and `olpc_ofw_is_installed()` expose availability.

## Control Flow
Early detection checks the `OFW ` signature and rejects too-low CIF addresses, then reserves top memory containing OFW. Page-table setup maps OFW's PGD and installs the relevant PDE permanently. Calls pack name, argument count, result count, and arguments into an array, call the CIF under a spinlock, then unpack results.

## State And Persistence
Stores `olpc_ofw_cif` and boot-time `olpc_ofw_pgd`. The OFW memory reservation and kernel page-table entry persist to allow later callbacks.

## Dependencies And Integration Points
Depends on x86 boot parameters, early ioremap, page tables, `reserve_top_address()`, and OLPC DT/EC code using `olpc_ofw()`.

## Risks And Edge Cases
The CIF uses 32-bit integer argument packing, so pointer assumptions are x86/OLPC-specific. Bad OFW PGD mapping disables OFW. Calls are serialized but still execute firmware code with interrupts disabled by the spinlock.

## Test Signals
OFW detection logs, successful DT build callbacks, and absence of page faults during OFW calls validate this support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/olpc_ofw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/xo1-wakeup.S -->
# sources/distributed-fs/ceph-client/arch/x86/platform/olpc/xo1-wakeup.S

## Purpose
Provides low-level 32-bit XO-1 suspend/resume assembly around the OpenFirmware sleep call.

## Important APIs, Types, And Functions
Exports `do_olpc_suspend_lowlevel`. Internal labels save/restore GDT, IDT, LDT, CR0/CR4, callee-saved registers, EFLAGS, and ESP; `wakeup_start` reestablishes page tables and jumps back after firmware wake.

## Control Flow
Suspend calls `save_processor_state`, saves assembly context, stores ESP, calls `xo1_do_sleep(3)`, and on wake enters `wakeup_start`. Wake code clears flags, restores CR3/CR4/CR0, segment registers, descriptor tables, flushes caches/TLB context, restores saved stack/registers, calls `restore_processor_state`, and returns to C.

## State And Persistence
Stores CPU descriptor/control/register state in `.data` symbols across the firmware sleep transition. POST codes are written to CMOS ports for diagnostics.

## Dependencies And Integration Points
Depends on `olpc-xo1-pm.c`, generic x86 `save_processor_state()`/`restore_processor_state()`, initial page tables, and 32-bit segment definitions.

## Risks And Edge Cases
Extremely sensitive to CPU mode, descriptor, and page-table expectations. Any mismatch with firmware resume state can crash before C code runs. It is not generic x86 suspend code.

## Test Signals
Reliable XO-1 suspend/resume with preserved CPU state, diagnostic POST values, and no descriptor/page faults during resume validate the assembly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/olpc/xo1-wakeup.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/pvh/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/pvh/Makefile

## Purpose
Builds x86 PVH guest entry and initialization support.

## Important APIs, Types, And Functions
`head.o` is marked non-standard and KASAN is disabled. `enlighten.o` and `head.o` are selected by `CONFIG_PVH`.

## Control Flow
Kbuild links the assembly entry and C boot-parameter setup only when PVH support is configured.

## State And Persistence
No runtime state is stored in the Makefile.

## Dependencies And Integration Points
Integrates with Xen/HVM PVH boot ABI and x86 early boot.

## Risks And Edge Cases
Instrumentation must be disabled for early entry code because it runs before normal runtime setup.

## Test Signals
PVH config builds and boots under Xen PVH are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/pvh/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/pvh/enlighten.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/pvh/enlighten.c

## Purpose
Converts PVH `hvm_start_info` into normal x86 `boot_params` and delegates hypervisor-specific initialization.

## Important APIs, Types, And Functions
`pvh_bootparams` and `pvh_start_info` are initdata preserved across early assembly. `xen_prepare_pvh()` validates magic, clears boot params, calls `xen_pvh_init()` for Xen guests, and initializes memory map, command line, ramdisk, loader type, and ACPI RSDP. Weak hooks `mem_map_via_hcall()` and `xen_pvh_init()` must be overridden for Xen.

## Control Flow
The C entry determines Xen by CPUID base. It uses start-info memory-map entries for versioned starts, falls back to a Xen hypercall for version 0, appends ISA reserved range when possible, and fills Linux boot header fields before assembly jumps to `startup_32/64`.

## State And Persistence
Writes the `pvh_bootparams` structure consumed by generic x86 startup. No long-lived state remains after initdata is freed.

## Dependencies And Integration Points
Depends on Xen HVM start-info ABI, x86 E820, bootparam layout, ACPI RSDP field, and Xen-specific overrides.

## Risks And Edge Cases
Missing weak overrides deliberately BUG. Too many E820 entries prevent adding ISA reservation. Code must avoid BSS assumptions because early startup clears BSS later.

## Test Signals
PVH boot with correct memory map, cmdline, ramdisk, ACPI discovery, and no weak-hook BUGs validates behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/pvh/enlighten.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/pvh/head.S -->
# sources/distributed-fs/ceph-client/arch/x86/platform/pvh/head.S

## Purpose
Implements the Xen PVH 32-bit physical entry point that sets up minimal CPU state, page tables, and handoff to generic x86 startup.

## Important APIs, Types, And Functions
Defines `pvh_start_xen`, PVH GDT entries/selectors, early stack, 64-bit PVH identity/kernel page tables, and Xen ELF notes for physical entry/relocation.

## Control Flow
Entry starts with Xen-specified registers, obtains a position-independent base without a normal stack, loads a private GDT, copies `hvm_start_info`, sets up stack, enables PAE/long mode as needed, applies relocation fixups to prebuilt page tables on x86_64, calls `xen_prepare_pvh()` through the high mapping, passes `pvh_bootparams`, and jumps to `startup_64` or resets paging state before `startup_32`.

## State And Persistence
Populates `pvh_start_info`, `phys_base` on relocation, temporary page tables, GDT, and stack in init sections. These are early boot artifacts.

## Dependencies And Integration Points
Depends on Xen PVH ABI, x86 paging constants, startup entry points, `enlighten.c`, and linker support for ELF notes.

## Risks And Edge Cases
No normal stack exists at entry; relocation arithmetic must avoid unsupported absolute relocations. Incorrect page-table fixups break PIE/KASLR PVH boot. Instrumentation is disabled by the Makefile for this reason.

## Test Signals
Booting PVH kernels in 32-bit, 64-bit, relocated, and non-relocated configurations is the meaningful validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/pvh/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/scx200/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/scx200/Makefile

## Purpose
Builds National Semiconductor SCx200 support.

## Important APIs, Types, And Functions
`scx200.o` is selected by `CONFIG_SCx200` and currently consists of `scx200_32.o`.

## Control Flow
Kbuild aggregates the 32-bit implementation into the platform object.

## State And Persistence
No runtime state is stored in this file.

## Dependencies And Integration Points
Integrates with PCI and SCx200 GPIO/configuration-block users through symbols exported by `scx200_32.c`.

## Risks And Edge Cases
The implementation is 32-bit-oriented; build selection must match supported architectures.

## Test Signals
SCx200 config build and module load coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/scx200/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/scx200/scx200_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/scx200/scx200_32.c

## Purpose
Detects National Semiconductor SCx200/SC1100 PCI devices, exposes GPIO and configuration-block base addresses, and provides a serialized GPIO configuration helper.

## Important APIs, Types, And Functions
Exports `scx200_gpio_base`, `scx200_gpio_shadow`, `scx200_cb_base`, and `scx200_gpio_configure()`. PCI probe handles bridge devices for GPIO base and XBUS devices for configuration block detection.

## Control Flow
Module init registers a PCI driver. Probe requests the GPIO I/O region for bridge devices and initializes shadow output state, or probes the fixed/scratch configuration-block base for XBUS devices. `scx200_gpio_configure()` selects a GPIO index, reads config, applies mask/bits, writes new config, and returns the previous value under a mutex.

## State And Persistence
Global base addresses and GPIO shadow arrays persist while the module is loaded. GPIO configuration writes persist in hardware registers.

## Dependencies And Integration Points
Depends on PCI IDs, `linux/scx200*.h`, I/O port access, and downstream SCx200 GPIO users.

## Risks And Edge Cases
The driver has no remove cleanup for requested regions. Global base values assume one platform instance. GPIO configuration requires valid prior probe and correct index selection.

## Test Signals
PCI probe logs for GPIO/config block bases, exported symbols used by GPIO drivers, and working GPIO configuration on SCx200 hardware validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/scx200/scx200_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/ts5500/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/ts5500/Makefile

## Purpose
Builds Technologic Systems TS-5500 platform support.

## Important APIs, Types, And Functions
`ts5500.o` is selected by `CONFIG_TS5500`.

## Control Flow
Kbuild includes the platform detector and device registration code when configured.

## State And Persistence
No runtime state exists here.

## Dependencies And Integration Points
The object integrates with platform devices, GPIO lookup, and DMI/BIOS detection in `ts5500.c`.

## Risks And Edge Cases
Incorrect config selection can add legacy board probing to unrelated kernels, though runtime detection self-filters.

## Test Signals
Config build and TS-5500 boot probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/ts5500/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/ts5500/ts5500.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/ts5500/ts5500.c

## Purpose
Registers platform devices and GPIO lookups for Technologic Systems TS-5500 single-board computers after BIOS identity detection.

## Important APIs, Types, And Functions
The file defines board resources and lookup tables for GPIO DIO lines, LEDs, keys, ADC, watchdog, and related platform devices. Its init path detects TS-5500 BIOS signatures before registration.

## Control Flow
Boot-time init probes legacy board identity, then registers GPIO chips and dependent platform devices with static resources/lookups. Device creation is ordered so providers exist before consumers.

## State And Persistence
Static platform-device/resource tables and registered lookup tables persist for the boot. Hardware state lives in I/O regions described by the resources.

## Dependencies And Integration Points
Integrates with gpiolib machine lookups, platform bus, input/LED/watchdog/ADC-style consumers, and x86 legacy I/O resources.

## Risks And Edge Cases
Legacy BIOS detection can miss variants or false-match. Static I/O resources can conflict if firmware or another driver owns the same ranges. Device ordering is important for GPIO consumers.

## Test Signals
Boot logs identifying TS-5500, registered platform devices, GPIO line visibility, LED/key function, and absence of I/O resource conflicts validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/ts5500/ts5500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/uv/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/uv/Makefile

## Purpose
Builds SGI/HPE UV platform BIOS, IRQ, RTC, and NMI support.

## Important APIs, Types, And Functions
`bios_uv.o`, `uv_irq.o`, `uv_time.o`, and `uv_nmi.o` are selected by `CONFIG_X86_UV`.

## Control Flow
Kbuild links all core UV platform support as a unit.

## State And Persistence
No runtime state is stored here.

## Dependencies And Integration Points
These objects integrate with EFI runtime, x86 IRQ domains, clocksource/events, APIC, NMI, kdump, kgdb/kdb, and UV hub MMR infrastructure.

## Risks And Edge Cases
The objects are tightly platform-specific; building them without the right Kconfig guards would add unavailable hardware paths.

## Test Signals
UV config builds and boots on hubbed and hubless UV systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/uv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/uv/bios_uv.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/uv/bios_uv.c

## Purpose
Wraps UV firmware runtime services exposed through the EFI UV system table.

## Important APIs, Types, And Functions
Exports UV BIOS calls for partition/coherency info, message-queue watchlists, memory protection, reserved pages, frequency base, legacy VGA target, master NASID, heap operations, object/port/geoinfo/PCI topology enumeration, and `uv_bios_init()`. `uv_systab_phys`, `uv_systab`, and SN info globals hold firmware state.

## Control Flow
`uv_bios_init()` validates and maps the EFI UV systab, remapping variable-size UV4+ tables. Calls acquire `__efi_uv_runtime_lock`, optionally disable IRQs, invoke the table function through `efi_call_virt_pointer()`, and return BIOS status codes.

## State And Persistence
The mapped `uv_systab` and exported partition globals persist after init. Firmware calls can alter UV BIOS-managed state such as heaps, memory protection, and watchlists.

## Dependencies And Integration Points
Depends on EFI runtime support, UV hub headers, x86 EFI locking, ioremap, and platform drivers needing UV firmware services.

## Risks And Edge Cases
Missing or disabled EFI runtime makes the systab unavailable. Firmware status codes must be preserved. Calls under IRQ-save are required for some low-level contexts but can still depend on EFI runtime correctness.

## Test Signals
UV systab revision logs, successful SN info retrieval, UV feature drivers using exported calls, and clean behavior with missing systab validate the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/uv/bios_uv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/uv/uv_irq.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/uv/uv_irq.c

## Purpose
Provides a UV-specific IRQ domain that programs UV hub MMR route entries for platform interrupts.

## Important APIs, Types, And Functions
`struct uv_irq_2_mmr_pnode` stores MMR offset and pnode. `uv_setup_irq()` allocates an IRQ/vector for a target CPU and programs the hub route; `uv_teardown_irq()` frees it. `uv_set_irq_affinity()` retargets parent vector affinity and updates the MMR.

## Control Flow
The domain is created lazily under a mutex as a child of `x86_vector_domain`. Allocation validates UV type, allocates chip data, allocates a parent vector, sets `IRQ_NO_BALANCING` if requested, and installs `uv_irq_chip`. Activation and affinity changes call `uv_program_mmr()` to write vector/destination fields into the hub MMR.

## State And Persistence
Per-IRQ chip data persists until domain free. Hardware MMR route entries persist until deactivation/teardown masks them.

## Dependencies And Integration Points
Integrates x86 vector IRQ domain, APIC destination mode, UV blade-to-pnode mapping, global MMR writes, and UV platform users needing MSI-like interrupts.

## Risks And Edge Cases
Route programming must match vector allocation exactly. Deactivation constructs a masked entry but relies on `uv_program_mmr()` semantics. CPU affinity changes need vector cleanup scheduling to avoid stale delivery.

## Test Signals
Successful `uv_setup_irq()` users, correct interrupt delivery to requested CPUs, affinity retargeting, and no leaked vectors after teardown validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/uv/uv_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/uv/uv_nmi.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/uv/uv_nmi.c

## Purpose
Implements UV system-wide NMI handling for dump, instruction-pointer summaries, health checks, kdump, kdb, and kgdb actions on very large systems.

## Important APIs, Types, And Functions
Important state includes per-CPU `uv_cpu_nmi`, hub `uv_hub_nmi_s` lists, global atomics, cpumasks, module parameters for action/timing/statistics, and hubless PCH registers. Entry points are `uv_nmi_setup()`, `uv_nmi_setup_hubless()`, `uv_nmi_init()`, `uv_handle_nmi()`, and `uv_handle_nmi_ping()`.

## Control Flow
Setup selects hub MMRs or hubless PCH GPIO routing, allocates per-node hub state, and registers NMI handlers. Primary NMI checks UV source, elects a master CPU, optionally attempts kdump, waits for CPUs while pinging missing ones with local NMIs, performs the selected action, clears hub/PCH NMI state, resets global atomics, and touches watchdogs. Ping handler catches CPUs whose first NMI was consumed by perf/local sources.

## State And Persistence
Module parameters expose counters and runtime action selection. Atomic/cpumask state coordinates each NMI episode. MMR/PCH register configuration persists while the system runs.

## Dependencies And Integration Points
Depends on APIC/NMI notifiers, UV hub MMR definitions, PCH memory mapping for hubless systems, kexec/kdump, kgdb/kdb, scheduler debug dumps, clocksource watchdog handling, and CPU topology.

## Risks And Edge Cases
NMI context forbids sleeping and makes locking/counter ordering fragile. Large CPU counts require careful timeouts and ping retries. Kdump can fail and must fall back. Hubless PCH register programming is hardware-revision-sensitive.

## Test Signals
Manual UV NMI action tests, module counters (`nmi_count`, misses, ping counts), stack/IP dumps from all CPUs, successful kdump/kdb/kgdb action where configured, and no NMI lockups validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/uv/uv_nmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/uv/uv_time.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/uv/uv_time.c

## Purpose
Registers the UV real-time clock as a clocksource and optional per-CPU clock-event device backed by UV RTC MMRs.

## Important APIs, Types, And Functions
Defines `clocksource_uv`, per-CPU `clock_event_device`, `struct uv_rtc_timer_head`, `uv_rtc_next_event()`, `uv_rtc_shutdown()`, `uv_rtc_interrupt()`, `uv_rtc_setup_clock()`, and the `uvrtcevt` early parameter.

## Control Flow
Init exits on non-UV or missing clock frequency, registers the RTC clocksource, and optionally allocates per-blade timer heads, sets up IRQs through `uv_setup_irq()`, and registers per-CPU clockevents. Timer programming tracks each CPU's expiry in a per-blade sorted list and programs the hub for the earliest event; interrupt dispatch sends IPIs to CPUs with expired timers.

## State And Persistence
Per-CPU clock-event devices and per-blade timer lists persist after init. Hardware RTC compare registers hold next expiry. `uv_rtc_evt_enable` is boot-parameter state.

## Dependencies And Integration Points
Depends on UV hub RTC registers, `uv_setup_irq()`, clocksource/clockevents core, CPU work scheduling, IPIs, and UV frequency discovery.

## Risks And Edge Cases
Per-blade list locking and next-event recalculation must avoid missed deadlines. Optional event mode can fail partway through allocation/IRQ setup and must deallocate. RTC frequency assumptions affect timekeeping accuracy.

## Test Signals
Clocksource registration, stable timekeeping, timer interrupt delivery on UV systems, `uvrtcevt` clockevent activation, and no missed timer warnings validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/uv/uv_time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/power/Makefile

## Purpose
Builds x86 suspend CPU-state support and architecture-specific hibernation restore code with compiler flags suited for low-level restore paths.

## Important APIs, Types, And Functions
`cpu.o` is built for `CONFIG_PM_SLEEP`; hibernation includes `hibernate_$(BITS).o`, `hibernate_asm_$(BITS).o`, and `hibernate.o`. `CFLAGS_cpu.o` disables stack protector, and LTO flags are removed from `cpu.o`.

## Control Flow
Kbuild selects bitness-specific hibernation C and assembly files and removes compiler features that can break `__restore_processor_state()`.

## State And Persistence
No runtime state exists in this file.

## Dependencies And Integration Points
Integrates with PM sleep, hibernation core, compiler hardening options, and x86 32/64-bit build variants.

## Risks And Edge Cases
Instrumentation or stack protector in restore code can corrupt `%gs`/stack assumptions during resume. The explicit flag removal is part of correctness.

## Test Signals
Builds under GCC/Clang, LTO, stack protector, PM sleep, and hibernation configs, plus successful suspend/hibernate resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/cpu.c -->
# sources/distributed-fs/ceph-client/arch/x86/power/cpu.c

## Purpose
Saves and restores x86 processor state across suspend/hibernate, handles hibernate CPU hotplug constraints, and registers quirks for MSRs that must survive firmware sleep.

## Important APIs, Types, And Functions
Exports `save_processor_state()` and `restore_processor_state()` on 32-bit. `__save_processor_state()` records descriptor tables, segments, control registers, MSRs, MTRRs, FPU state, and scheduler clock state. `__restore_processor_state()` restores CRs/segments/MSRs/FRED/TSS/LDT/FPU/debug/perf/cache/microcode state. `hibernate_resume_nonboot_cpu_disable()` forces nonboot CPUs into safe halt paths.

## Control Flow
Save enters kernel FPU context, records architectural state, and calls platform clock save. Restore reverses control-register and descriptor setup, restores percpu access before complex exception/FRED work, reloads TSS/LDT, restores user segment bases, ends FPU context, verifies TSC adjust, restores platform/debug/perf/cache state, updates microcode, then restores saved MSRs. Init registers a PM notifier requiring CPU0 online and builds MSR save lists from DMI, CPU family, and speculation-control features.

## State And Persistence
Global `saved_context` holds the resume image. Dynamic saved-MSR arrays persist after device init. PM notifier state persists for sleep transitions.

## Dependencies And Integration Points
Depends on x86 descriptor/MSR/FPU/MTRR/microcode/FRED/TLB APIs, PM notifier core, CPU hotplug, tboot, DMI, and platform clock hooks.

## Risks And Edge Cases
Restore ordering is critical, especially `%gs`, FRED, CR3/CR4, and MSRs emulated by microcode. CPU0 must be online. Nonboot SMT siblings must not resume from stale page tables via MWAIT.

## Test Signals
Suspend/resume and hibernate/resume on 32/64-bit systems, DMI/CPU MSR quirk logs, CPU0-offline rejection, and no segment/percpu faults after resume validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/hibernate.c -->
# sources/distributed-fs/ceph-client/arch/x86/power/hibernate.c

## Purpose
Provides common x86 hibernation header, image integrity checks, relocated restore-code setup, and SMT resume handling.

## Important APIs, Types, And Functions
`pfn_is_nosave()` identifies nosave pages. `struct restore_data_record` stores magic, restore jump addresses, CR3, and E820 checksum. `arch_hibernation_header_save/restore()` serialize and validate this data. `relocate_restore_code()` copies `core_restore_code` to a safe executable page. `arch_resume_nosmt()` rescans hlt-sleeping SMT siblings.

## Control Flow
Save writes architecture header values, masking PCID bits from CR3. Restore verifies magic and E820 CRC before accepting jump/CR3 values. Resume allocates a safe page, copies restore code, clears NX on the page mapping, flushes TLBs, and later bitness-specific code jumps into `restore_image()`.

## State And Persistence
Global visible symbols carry restore jump address, physical jump address, restore CR3, temporary page-table address, and relocated restore-code address between C and assembly. The hibernation image persists the header on disk/swap.

## Dependencies And Integration Points
Depends on hibernation core, E820 firmware table, safe-page allocator, page-table APIs, TLB flush, bitness-specific hibernate code, and CPU hotplug SMT helpers.

## Risks And Edge Cases
E820 changes between hibernate and resume reject the image. Executability changes must handle leaf mappings at several levels. PCID bits in CR3 must be cleared to avoid illegal CR4/CR3 transitions.

## Test Signals
Successful hibernate image save/restore, rejection of mismatched headers/maps, and SMT sibling recovery after resume validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/hibernate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/hibernate_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/power/hibernate_32.c

## Purpose
Builds temporary 32-bit page tables needed to restore a hibernated image.

## Important APIs, Types, And Functions
`resume_pg_dir` stores the temporary PGD. Helpers allocate resume-safe PMD/PTE pages, map all low physical memory at `PAGE_OFFSET`, map the image kernel restore text at its original virtual address, and `swsusp_arch_resume()` orchestrates the transition.

## Control Flow
Resume allocates a safe PGD, initializes PAE entries if needed, maps `restore_jump_address` to `jump_address_phys`, builds a physical/direct mapping up to `max_low_pfn` using PSE large pages where possible, publishes `temp_pgt`, relocates restore code, and calls assembly `restore_image()`.

## State And Persistence
Temporary page tables live on safe pages and are referenced by `temp_pgt` for assembly. They exist only for the no-return restore phase.

## Dependencies And Integration Points
Depends on x86 32-bit paging, PAE/PSE support, safe-page allocator, common hibernate globals, and `hibernate_asm_32.S`.

## Risks And Edge Cases
Failure after the final no-recover point cannot unwind. PAE first-level initialization must point unused entries to the zero page. Incorrect text mapping prevents jumping into the restored image kernel.

## Test Signals
32-bit hibernate resume with and without PAE/PSE and correct no-memory error handling before `restore_image()` validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/hibernate_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/hibernate_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/power/hibernate_64.c

## Purpose
Builds temporary 64-bit page tables for hibernation restore, including five-level paging support.

## Important APIs, Types, And Functions
`set_up_temporary_text_mapping()` maps the image kernel entry virtual address to its physical page. `set_up_temporary_mappings()` allocates a fresh PGD, maps restore text, identity-maps all `pfn_mapped` ranges through `kernel_ident_mapping_init()`, and stores `temp_pgt`. `swsusp_arch_resume()` calls setup, relocation, and assembly restore.

## Control Flow
The code allocates safe pages for required page-table levels, filters page protections through the default kernel mask, installs a large executable PMD for restore text, creates direct identity mappings for every mapped physical range, relocates restore code, and enters `restore_image()`.

## State And Persistence
Temporary page tables and relocated restore code are safe-page state consumed during the no-return restore sequence.

## Dependencies And Integration Points
Depends on x86_64 page-table APIs, LA57 detection, `kernel_ident_mapping_init()`, common hibernation globals, and `hibernate_asm_64.S`.

## Risks And Edge Cases
Five-level paging requires an extra P4D page. Page protection must avoid unsupported bits. Mapping only the final text page assumes relocated code handles the switch until the last jump.

## Test Signals
64-bit hibernate resume under 4-level and 5-level paging, with KASLR/large mappings, validates the page-table setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/hibernate_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/hibernate_asm_32.S -->
# sources/distributed-fs/ceph-client/arch/x86/power/hibernate_asm_32.S

## Purpose
Contains 32-bit assembly for saving suspend registers, copying the hibernation image back to original pages, and jumping into restored kernel state.

## Important APIs, Types, And Functions
Defines `swsusp_arch_suspend`, `restore_image`, `core_restore_code`, and `restore_registers`. Uses saved context symbols from `cpu.c` and hibernation globals such as `temp_pgt`, `restore_cr3`, and `restore_jump_address`.

## Control Flow
Suspend saves callee-saved registers and stack return context before returning to the hibernation core. Restore switches to temporary page tables, copies memory pages from the snapshot list to original locations, switches to the restored CR3, and jumps to `restore_registers`, which restores saved registers and returns to the image kernel.

## State And Persistence
Assembly stores register values in global saved-context symbols and consumes the relocated restore code copied by C.

## Dependencies And Integration Points
Depends on common hibernate C, 32-bit paging/control register conventions, and `restore_processor_state()` after control returns to C.

## Risks And Edge Cases
Copying over live memory is irreversible. Register and stack restoration must match the C save side exactly. Interrupts and page tables must remain controlled until the restored kernel resumes.

## Test Signals
32-bit hibernate suspend/resume and stress tests with varied memory layouts exercise this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/hibernate_asm_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/hibernate_asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/power/hibernate_asm_64.S

## Purpose
Contains 64-bit hibernation assembly for register restoration, suspend checkpointing, image copyback, and final jump to the restored kernel.

## Important APIs, Types, And Functions
Defines `restore_registers`, `swsusp_arch_suspend`, `restore_image`, and `core_restore_code`. It coordinates with `saved_context`, `restore_cr3`, `temp_pgt`, `restore_jump_address`, and `restore_processor_state()`.

## Control Flow
Suspend saves nonvolatile registers around the hibernation snapshot. Restore code runs from the relocated page, switches to temporary page tables and current CR4 feature mask, copies image pages back, switches to the image kernel CR3, updates CR4 again for the image kernel, and jumps to `restore_registers` to restore processor state and return to the saved control point.

## State And Persistence
Uses global hibernation symbols as handoff state between C and assembly. The copied image overwrites current kernel memory during restore.

## Dependencies And Integration Points
Depends on x86_64 calling convention, hibernation C setup, page-table globals, and CPU state restoration in `cpu.c`.

## Risks And Edge Cases
The CR3/CR4 ordering must avoid illegal PCID transitions and match comments in `hibernate.c`. Any compiler instrumentation or relocation assumption would be unsafe in this path.

## Test Signals
64-bit hibernate resume, especially with PCID, KASLR, and varied CR4 feature sets, validates the assembly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/power/hibernate_asm_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/purgatory/Makefile

## Purpose
Builds the standalone x86 kexec purgatory object and checks it for unresolved symbols.

## Important APIs, Types, And Functions
`purgatory-y` includes `purgatory.o`, stack/setup/entry assembly, `sha256.o`, and `string.o`. It builds `purgatory.ro`, `purgatory.chk`, and embeds them through `kexec-purgatory.o`.

## Control Flow
Kbuild compiles freestanding objects with flags that remove profiling, LTO, stack protector, CFI, retpoline, and other kernel instrumentation. It links a relocatable purgatory object and a non-relocatable check binary to catch unresolved symbols.

## State And Persistence
No runtime state here; it defines the embedded purgatory payload used during kexec.

## Dependencies And Integration Points
Pulls SHA-256 from `lib/crypto/sha256.c` and string routines from compressed boot code. Integrates with kexec file loading.

## Risks And Edge Cases
Purgatory cannot tolerate normal kernel instrumentation, extra sections, unresolved symbols, or unsupported relocation patterns. Build flags are security/correctness-critical for a freestanding blob.

## Test Signals
Successful `purgatory.chk` link, kexec file load, and digest verification in purgatory validate the build rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/entry64.S -->
# sources/distributed-fs/ceph-client/arch/x86/purgatory/entry64.S

## Purpose
Provides a 64-bit entry trampoline that loads a controlled GDT, stack, register set, and jumps to the final kexec kernel entry point.

## Important APIs, Types, And Functions
Defines `entry64`, `entry64_regs`, a local GDT, and a small stack. `entry64_regs` contains slots for all general-purpose registers and final RIP.

## Control Flow
The entry loads the local GDT, sets data segments, switches to the local stack, performs a far return to load CS, loads register values from `entry64_regs`, then jumps through the stored `rip`.

## State And Persistence
`entry64_regs` is patched by kexec setup before execution. The GDT/stack are static purgatory data.

## Dependencies And Integration Points
Used by x86 kexec purgatory and final kernel handoff. Relies on 64-bit flat segment descriptors.

## Risks And Edge Cases
Every register slot must match kexec loader expectations. A bad stack, GDT, or RIP value hangs before the new kernel starts.

## Test Signals
Successful kexec into 64-bit kernels with expected register state validates this trampoline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/entry64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/kexec-purgatory.S -->
# sources/distributed-fs/ceph-client/arch/x86/purgatory/kexec-purgatory.S

## Purpose
Includes the linked purgatory binary as data in a kernel object for kexec.

## Important APIs, Types, And Functions
The assembly places purgatory blob contents in a read-only section using symbols consumed by kexec file loading.

## Control Flow
There is no runtime control flow in this wrapper; build rules generate the blob and this object embeds it.

## State And Persistence
The embedded purgatory image becomes kernel data used when preparing a kexec image.

## Dependencies And Integration Points
Depends on the `purgatory.ro` build target and kexec file loader relocation code.

## Risks And Edge Cases
Symbol naming and section placement must match loader expectations. If the blob is stale or missing, kexec file loading fails.

## Test Signals
Successful build of `kexec-purgatory.o` and kexec file load using the embedded blob validate the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/kexec-purgatory.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/purgatory.c -->
# sources/distributed-fs/ceph-client/arch/x86/purgatory/purgatory.c

## Purpose
Verifies the SHA-256 digest of kexec image segments before transferring control to the next kernel.

## Important APIs, Types, And Functions
`purgatory_sha256_digest` and `purgatory_sha_regions` are patched by the kexec loader. `verify_sha256_digest()` computes SHA-256 over each listed region. `purgatory()` loops forever if verification fails. `warn()` is a stub for freestanding code.

## Control Flow
At purgatory runtime, the code hashes every nonzero region, compares against the expected digest, and returns only on success. On mismatch it spins, preventing execution of a corrupted image.

## State And Persistence
Digest and region arrays are in the `.kexec-purgatory` section and patched per kexec image. No OS services are available.

## Dependencies And Integration Points
Uses freestanding SHA-256 and string/memcmp support built into purgatory. Integrated with kexec file loading and relocation.

## Risks And Edge Cases
No logging is available because `warn()` is empty. Region list termination and digest patching must be exact. A false mismatch hangs the kexec transition.

## Test Signals
Successful kexec with valid image, deliberate digest-corruption tests that halt, and correct SHA region patching validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/purgatory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/setup-x86_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/purgatory/setup-x86_64.S

## Purpose
Provides the 64-bit purgatory start entry that establishes a known stack/GDT and calls the C purgatory verifier.

## Important APIs, Types, And Functions
Defines `purgatory_start`, local GDT, and local stack. Calls `purgatory` and then jumps to `entry64` for final handoff.

## Control Flow
Entry loads a controlled GDT, switches to a local stack, calls the digest-verification C function, and only if it returns branches to the register-loading `entry64` trampoline.

## State And Persistence
Uses static stack/GDT data inside the purgatory image.

## Dependencies And Integration Points
Depends on `purgatory.c` and `entry64.S`, and serves as the linked entry point selected by the purgatory Makefile.

## Risks And Edge Cases
If the verifier hangs, handoff never occurs by design. The setup code must remain freestanding and relocation-friendly.

## Test Signals
Kexec handoff through purgatory with digest verification and correct final entry state validates the setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/setup-x86_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/stack.S -->
# sources/distributed-fs/ceph-client/arch/x86/purgatory/stack.S

## Purpose
Defines the purgatory stack storage.

## Important APIs, Types, And Functions
Exports `stack` and `stack_end` symbols around a fixed-size stack area.

## Control Flow
No executable control flow; entry assembly uses the symbols to initialize stack pointers.

## State And Persistence
The stack is temporary runtime storage while purgatory executes during kexec.

## Dependencies And Integration Points
Consumed by purgatory setup/entry assembly and linked into `purgatory.ro`.

## Risks And Edge Cases
Stack size must be sufficient for SHA verification and handoff code. Incorrect symbol alignment/size would corrupt adjacent purgatory data.

## Test Signals
Successful purgatory execution under kexec and absence of stack corruption indicate correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/stack.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/ras/Kconfig -->
# sources/distributed-fs/ceph-client/arch/x86/ras/Kconfig

## Purpose
Defines x86 RAS Correctable Errors Collector options.

## Important APIs, Types, And Functions
`RAS_CEC` enables the correctable error collector and selects `BITREVERSE`. `RAS_CEC_DEBUG` enables debugfs support for CEC and depends on `RAS_CEC`.

## Control Flow
Kconfig presents options and dependency/help text; no runtime code exists here.

## State And Persistence
The selected config controls compiled code and optional debugfs exposure elsewhere.

## Dependencies And Integration Points
Integrates with x86 RAS/MCE code and debugfs when enabled.

## Risks And Edge Cases
Debug support can expose internal state and should remain dependent on the collector. Config help must accurately describe platform support.

## Test Signals
Kconfig dependency resolution, builds with CEC/debug enabled and disabled, and expected debugfs presence under debug config validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/ras/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/Makefile

## Purpose
Builds the x86 real-mode trampoline blob and piggyback object used by early boot and low-level transitions.

## Important APIs, Types, And Functions
The Makefile includes `rm/Makefile`, adds `init.o` and `rmpiggy.o`, and wires real-mode targets into the object tree.

## Control Flow
Kbuild descends into real-mode build rules, creates the real-mode binary, and links the piggy object into the kernel.

## State And Persistence
No runtime state exists in the Makefile, but it controls generation of the embedded real-mode code image used at boot/resume.

## Dependencies And Integration Points
Integrates with `arch/x86/realmode/rm` build rules, early boot trampoline allocation, and users such as EFI boot-services memory handling that may reserve space for the trampoline.

## Risks And Edge Cases
Build ordering is important because `rmpiggy.o` depends on generated real-mode artifacts. Missing trampoline artifacts can break boot paths requiring real mode.

## Test Signals
Successful x86 build, presence of generated real-mode image, and boot paths using the trampoline validate the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/Makefile -->
