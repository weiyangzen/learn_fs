<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/mellanox/mlx-platform.c -->
# sources/distributed-fs/ceph-client/drivers/platform/mellanox/mlx-platform.c

## Purpose
`mlx-platform.c` is the Mellanox/NVIDIA platform orchestration driver for switch, modular, blade, DGX, XDR, smart-switch, and BlueField-adjacent platform families identified through DMI and ACPI. It maps the platform CPLD/FPGA register block, builds a `regmap` over LPC I/O or Lattice FPGA PCI bridge memory, selects per-system static platform data, and instantiates child platform devices for I2C, I2C muxes, hotplug/event monitoring, LEDs, register sysfs access, fan telemetry/control, watchdogs, and DPU controllers.

The file is mostly declarative hardware description: CPLD offsets, event masks, mux channel layouts, hotplug item arrays, LED/register/fan/watchdog descriptors, and DMI callbacks. The executable core ties those tables to Linux platform devices and handles resource mapping, adapter-number shifting, watchdog capability upgrades, reboot/poweroff hooks, and teardown.

## Important APIs, Types, And Functions
- `struct mlxplat_priv` stores all runtime-owned child `platform_device` handles, the shared `regmap`, hotplug resource metadata, I2C initialization status, and optional FPGA IRQ.
- `mlxreg_core_data`, `mlxreg_core_item`, `mlxreg_core_platform_data`, and `mlxreg_core_hotplug_platform_data` tables describe downstream `mlxreg-*` child drivers. They encode labels, CPLD registers, masks, capabilities, slot numbers, I2C board info, health semantics, and notifier callbacks.
- `i2c_mux_reg_platform_data` tables describe parent bus IDs, base adapter numbers, mux selector registers, values, and channel counts for default, extended, modular, rack-switch, and NG800 topologies.
- `mlxplat_mlxcpld_writeable_reg()`, `mlxplat_mlxcpld_readable_reg()`, and `mlxplat_mlxcpld_volatile_reg()` constrain the register surface exposed to `regmap`.
- `mlxplat_mlxcpld_reg_read()` and `mlxplat_mlxcpld_reg_write()` are byte-wide `ioread8()`/`iowrite8()` callbacks used by all `regmap_config` variants.
- DMI callbacks such as `mlxplat_dmi_default_matched()`, `mlxplat_dmi_ng400_matched()`, `mlxplat_dmi_modular_matched()`, `mlxplat_dmi_smart_switch_matched()`, and `mlxplat_dmi_l1_switch_matched()` select global table pointers: mux data, hotplug data, LED data, register IO data, fan data, watchdog type, DPU data, I2C data, and regmap defaults.
- `mlxplat_logicdev_init()` prefers Lattice FPGA PCI bridges and falls back to direct LPC CPLD I/O when FPGA bridge devices are absent.
- `mlxplat_platdevs_init()` registers child devices: `mlxreg-hotplug`, `leds-mlxreg`, `mlxreg-io`, `mlxreg-fan`, `mlx-wdt`, and `mlxreg-dpu`.
- `mlxplat_i2c_main_init()` verifies/allocates a main `i2c_mlxcpld` bus, wires the shared regmap and PCI I2C bridge address, and triggers mux plus child-device initialization.
- `mlxplat_probe()` maps logic resources, allocates private state, initializes regmap defaults, starts I2C and child devices, syncs regcache, and registers reboot hooks where selected.
- `mlxplat_remove()` and the `*_exit()` helpers unregister child devices and release mapped logic devices in reverse order.

## Control Flow
Module initialization starts in `mlxplat_init()`. It first calls `dmi_check_system(mlxplat_dmi_table)`. A matching DMI entry runs one of the per-family callbacks; that callback mutates global selection variables and registers the singleton `mlxplat` platform device. If no DMI entry matches, the module returns `-ENODEV`.

After DMI setup, `platform_driver_register()` binds `mlxplat_driver` to the platform device and calls `mlxplat_probe()`. ACPI systems can provide an FPGA IRQ through `acpi_dev_gpio_irq_get()`, but the DMI table still gates module startup. Probe then calls `mlxplat_logicdev_init()`: first trying three Lattice PCI bridge functions for LPC, I2C, and JTAG access, and falling back to mapping the LPC CPLD register window with `devm_ioport_map()` if the PCI bridge path returns `-ENODEV`.

Probe creates a `regmap` over the mapped base address, writes each selected regmap default, then initializes the I2C path. `mlxplat_mlxcpld_verify_bus_topology()` scans I2C adapter IDs from the default parent bus and shifts mux base IDs plus hotplug `shift_nr` if the expected parent adapter is occupied. `i2c_mlxcpld` registration can complete synchronously or call back through `completion_notify`; either path reaches `mlxplat_i2c_mux_topology_init()`, registers `i2c-mux-reg` devices, and then calls `mlxplat_platdevs_init()`.

Child platform devices are brought up in dependency order: hotplug first, then LEDs, register IO, fan, watchdogs, and DPUs. Failure paths unwind the already-registered devices. Remove and probe error paths reverse the same layers: platform children, muxes, main I2C controller, logic-device mappings, reboot notifier, and poweroff hook.

## State And Persistence
Persistent hardware state lives in CPLD/FPGA registers, not in files. The driver writes selected default values during probe, including write-protect, PWM, watchdog action, and aggregator-mask defaults depending on the matched system family. Runtime state is stored in static global pointers selected by DMI and in `struct mlxplat_priv` attached with `platform_set_drvdata()`.

The shared `regmap` uses `REGCACHE_FLAT`. Many CPLD status and event registers are marked volatile, while selected defaults are written then `regcache_mark_dirty()` and `regcache_sync()` synchronize cache with hardware. Child drivers share the same regmap pointer, so LED, IO, hotplug, fan, watchdog, and DPU operations all act on the same underlying CPLD register file.

Power and reset behavior can outlive normal driver operations: the L1 switch DMI path installs `pm_power_off = mlxplat_poweroff` and a reboot notifier. Poweroff writes `MLXPLAT_CPLD_HALT_MASK` to `GP1` and calls `kernel_halt()`. The reboot notifier may write `MLXPLAT_CPLD_RESET_MASK` when a system restart is requested and the CPLD system-reset bit is set.

## Dependencies And Integration Points
- Linux subsystems: DMI, ACPI companion devices, platform bus, PCI, I/O port and MMIO mapping, DMA masks, regmap, I2C core, I2C mux-reg, reboot/poweroff, and kernel halt/poweroff paths.
- Mellanox platform child drivers: `i2c_mlxcpld`, `i2c-mux-reg`, `mlxreg-hotplug`, `leds-mlxreg`, `mlxreg-io`, `mlxreg-fan`, `mlx-wdt`, `mlxreg-lc`, and `mlxreg-dpu`.
- Hardware interfaces: LPC CPLD I/O at `0x2000`/`0x2500`, optional Lattice PCI bridges for LPC/I2C/JTAG, FPGA IRQ `17` or ACPI-provided GPIO IRQ, and I2C hotplug devices such as PSU monitors and EEPROMs.
- DMI identities: `VMOD0001` through newer `VMOD0022` families plus Mellanox product-name prefixes such as `MSN24`, `MSN27`, `MSN21`, `MSN201`, `MQM87`, `MSN37`, `MSN34`, and `MSN38`.
- Notifier integration: hotplug notifiers can invoke platform-specific callbacks. The L1 power-button handler calls `kernel_power_off()` on short press; the intrusion handler toggles a latch-reset bit through regmap.

## Risks And Edge Cases
- The file relies heavily on mutable global platform-data pointers. DMI callbacks mutate static descriptor tables in place, including mux parent/base IDs and hotplug deferred/shift fields. Reprobe, unusual module reload sequences, or multiple matching devices would need care because these tables are not copied per instance.
- `mlxplat_mlxcpld_verify_bus_topology()` shifts adapter numbering when the expected I2C parent is busy. Incorrect shifts would break child hotplug I2C board registration or collide with existing adapters.
- Regmap readability/writeability/volatility lists are large hand-maintained switch statements. Missing a register can silently block child driver access; incorrectly allowing a register can expose unsafe writes.
- Hardware-family DMI matching order matters. More-specific SKU matches must precede generic board matches; otherwise a board could receive the wrong mux, LED, watchdog, or regmap default set.
- `mlxplat_pci_fpga_device_exit()` unmaps/releases PCI bridge resources and is called in strict reverse order. Partial PCI bridge discovery failures must keep the globals consistent so exit does not touch uninitialized bridges.
- Watchdog type may be overridden at runtime by `mlxplat_mlxcpld_check_wd_capability()`. Misinterpreting the capability bit changes watchdog register layout and timeout behavior.
- Poweroff and intrusion handlers write control registers from asynchronous event contexts. Register-access failures are logged but may leave hardware in its previous latch/power state.

## Test Signals
- Boot/module-load logs should show successful DMI match, platform-driver probe, logic-device mapping, regmap initialization, and child platform-device registration without unwind errors.
- `/sys/bus/platform/devices/` should contain the expected child devices for the matched family: `i2c_mlxcpld`, `i2c-mux-reg.*`, `mlxreg-hotplug`, `leds-mlxreg`, `mlxreg-io`, optional `mlxreg-fan`, one or two `mlx-wdt.*`, and optional `mlxreg-dpu.*`.
- I2C adapter numbering should match the selected mux topology, or be consistently shifted when the default parent bus was occupied. Hotplug PSU/fan/line-card/DPU devices should appear on the expected adapter numbers.
- `mlxreg-io` attributes should expose family-appropriate CPLD version, reset-cause, BIOS, fan direction, power, JTAG, line-card, or DPU controls with the declared permissions.
- Hotplug tests should toggle PSU, fan, line-card, EROT, power-button, intrusion, and DPU-ready events on hardware or emulation and confirm event masks, inversion semantics, notifiers, and child I2C device creation/removal.
- Watchdog tests should validate the selected type1/type2/type3 register layout, timeout defaults, ping, action, time-left, and reset-cause reporting.
- Reboot and poweroff tests for L1 switch systems should confirm the reboot notifier and `pm_power_off` path write the expected CPLD masks and unregister cleanly on driver removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/mellanox/mlx-platform.c -->
