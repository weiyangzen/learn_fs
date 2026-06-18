# sources/distributed-fs/ceph-client/drivers/ssb/main.c

## Purpose
Central SSB bus core: registers the `ssb` bus type, manages global bus lists and early-boot attach queue, registers SSB devices/drivers, handles bus power/suspend/resume, initializes built-in cores, calculates clocks/DMA translation, and wires optional bridge drivers at module init/exit.

## Important APIs, Types, and Functions
Exports bus lookup/iteration (`ssb_pci_dev_to_bus`, `ssb_pcmcia_dev_to_bus`, `ssb_for_each_bus_call`), power (`ssb_bus_powerup`, `ssb_bus_may_powerdown`, suspend/resume), registration APIs for PCI/PCMCIA/SDIO/SoC hosts, driver registration, `ssb_set_devtypedata`, `ssb_calc_clock_rate`, `ssb_clockspeed`, device enable/disable/is-enabled, `ssb_dma_translation`, `ssb_commit_settings`, `ssb_admatch_base`, and `ssb_admatch_size`.

## Control Flow
Host-specific register functions set bus type/ops and call `ssb_bus_register`. Registration powers xtal/PLL, initializes host transport, locks global lists, scans cores, initializes PCI/PCMCIA support, powers the bus, initializes ChipCommon/EXTIF/MIPS core, fetches invariants, queues the bus, and attaches immediately after early boot. Attach powers up, initializes PCI core, registers watchdog/GPIO, powers down if allowed, registers non-system SSB devices, and moves the bus to the live list. Device registration skips system cores handled internally, creates wrapper devices for functional cores, sets parent/DMA/IRQ based on host type, and registers flash platform devices if detected. `fs_initcall` registers the bus type, drains early queue, and initializes b43 PCI bridge, PCMCIA host, and GigE driver.

## State and Persistence
Global state includes `attach_queue`, live `buses`, `next_busnumber`, `buses_mutex`, and `ssb_is_early_boot`. Per-bus state includes mapped device, power flags, core arrays, board/SPROM data, device wrappers, GPIO/watchdog/flash state, and host pointers. Hardware state includes TMSLOW/TMSHIGH/IMSTATE, clock/xtal registers, and broadcast settings.

## Dependencies and Integration Points
Integrates all SSB host backends, scan/sprom helpers, ChipCommon/PMU/EXTIF/MIPS/PCI/GigE/GPIO code, Linux driver core, platform devices, DMA mapping, PCI, PCMCIA, SDIO, and module/initcall ordering.

## Risks
Early-boot queue locking is conditional, so ordering is delicate. Error unwinding spans multiple subsystems and must keep list/mapping/power state consistent. System cores are not registered as regular devices, so built-in init must stay complete. Device enable/disable sequences include timing and reject-bit differences by backplane revision; mistakes can cause machine checks. DMA translation has chip-specific exceptions.

## Test Signals
Exercise early SoC registration and late hotplug-like host registration, verify core scan and functional device creation, suspend/resume reinitializes power and PCI setup, unregister removes devices/GPIO/mappings, clock calculations match hardware, and b43/PCMCIA/GigE init failures remain non-fatal.
