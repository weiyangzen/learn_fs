# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-mt7621.c

## Purpose

`pcie-mt7621.c` is a built-in MediaTek/Ralink MT7621 PCIe host controller driver for up to three virtual PCIe bridges. It parses per-port resources from DT, handles MT7621 reset polarity quirks, powers PHYs and clocks, detects which slots have link, programs bridge windows and class codes, and registers a PCI host bridge using Type 1 style config access.

## Important APIs, Types, And Functions

- `struct mt7621_pcie` stores shared MMIO base, device pointer, active port list, and whether reset controls are inverted for MT7621 E2.
- `struct mt7621_pcie_port` stores per-port MMIO base, clock, PHY, reset control, optional GPIO endpoint reset, slot number, and enabled state.
- `mt7621_pcie_parse_dt()` maps shared registers and parses available child nodes with `of_pci_get_devfn()`.
- `mt7621_pcie_parse_port()` maps per-slot resources, gets child clock, reset, PHY, optional GPIO reset, and appends the port.
- `mt7621_pcie_init_ports()` asserts RC and EP resets, deasserts RC resets, initializes PHYs for ports except the special slot 1 path, deasserts EP resets, checks link status, disables empty ports, and handles shared PHY behavior between slots 0 and 1.
- `mt7621_pcie_enable_ports()` programs MEM/IO base registers, enables clocks for linked ports, enables per-port interrupts, maps BAR0 to DDR, fixes class/revision, and tunes FTS.
- `mt7621_pcie_map_bus()` programs `RALINK_PCI_CONFIG_ADDR` and returns the config data window for generic config access.
- `mt7621_pcie_probe()` handles host bridge allocation, SoC revision quirk detection, DT parse, port init, enable, and `pci_host_probe()`.

## Control Flow

Probe requires an OF node, allocates host bridge private state, initializes the port list, checks `soc_device_match()` for MT7621 E2 inverted resets, parses shared/per-port DT state, initializes ports and link status, enables active ports, and registers the host bridge. If no links are detected, it logs the condition and returns success without registering a host, treating an empty board as nonfatal.

Config cycles use `PCI_CONF1_EXT_ADDRESS()` written to a shared address register, with generic PCI config helpers reading/writing the data register. Startup programming uses helper `read_config()`/`write_config()` for RC-side tuning registers.

## State And Persistence

The port list persists for the driver lifetime. `enabled` records link-detected ports. Reset polarity is persisted in `resets_inverted`. Per-port PHY and clock state remains active for enabled ports; empty ports are reset/disabled. There is no persistent storage.

## Dependencies And Integration Points

The driver depends on OF child nodes and resources, child clocks, reset controls, GPIO descriptors for endpoint resets, PHY framework, `soc_device_match()` revision data, PCI host bridge APIs, and generic config access. It is registered with `builtin_platform_driver()` for `mediatek,mt7621-pci`.

## Risks And Edge Cases

- Slot 1 is treated specially during PHY init, and slot 0/1 share behavior can power off slot 0 PHY when both are disabled; board-specific topology matters.
- Reset polarity is tied to SoC revision match `mt7621` `E2`; missing revision data can invert reset behavior.
- `mt7621_pcie_probe()` returns success when no cards are connected, so absence of a PCI host may be expected but can surprise generic tests.
- Remove only releases reset controls; as a built-in legacy driver it does not perform full root bus teardown in its remove callback.
- IO resource is mandatory in `mt7621_pcie_enable_ports()`.

## Test Signals

Validate MT7621 E2 and non-E2 reset polarity, DT child parsing for all three ports, no-card boot returning success, linked slot enumeration, GPIO PERST timing, IO/MEM base programming, class code/FTS setup, generic config reads/writes, and clock enable failures unwinding reset controls.
