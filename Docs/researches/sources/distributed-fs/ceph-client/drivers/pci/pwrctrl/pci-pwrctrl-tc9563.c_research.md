# sources/distributed-fs/ceph-client/drivers/pci/pwrctrl/pci-pwrctrl-tc9563.c

## Purpose
This is a device-specific PCI power-control provider for the Toshiba TC9563 PCIe switch. It enables switch power rails, controls reset, creates an auxiliary I2C client, and programs TC9563 registers for port disable, ASPM entry delays, TX amplitude, N_FTS, and DFE behavior before allowing PCI enumeration.

## Important APIs, types, and functions
`struct tc9563_pwrctrl` embeds `struct pci_pwrctrl` and stores regulators, per-port configuration, reset GPIO, I2C adapter, and dummy I2C client. `struct tc9563_pwrctrl_cfg` stores DT-derived settings for each port. I2C access helpers are `tc9563_pwrctrl_i2c_write()`, `tc9563_pwrctrl_i2c_read()`, and `tc9563_pwrctrl_i2c_bulk_write()`. Configuration helpers include `tc9563_pwrctrl_disable_port()`, `tc9563_pwrctrl_set_l0s_l1_entry_delay()`, `tc9563_pwrctrl_set_tx_amplitude()`, `tc9563_pwrctrl_disable_dfe()`, `tc9563_pwrctrl_set_nfts()`, and `tc9563_pwrctrl_assert_deassert_reset()`. `tc9563_pwrctrl_probe()` wires DT, supplies, GPIO, I2C, and pwrctrl registration.

## Control flow
Probe allocates state, reads the `i2c-parent` phandle and address, obtains the I2C adapter, creates a dummy I2C client, gets six named regulators, gets the `resx` reset GPIO asserted high, initializes pwrctrl, parses upstream and downstream port DT nodes into the per-port config array, and registers readiness. On power-on, it enables all regulators, deasserts the external GPIO reset, waits for oscillator stability, asserts internal reset over I2C, iterates all port configs applying disable/delay/amplitude/N_FTS/DFE programming, then deasserts internal reset. On any error it powers the device off. Removal powers off, unregisters the dummy I2C device, and releases the adapter reference.

## State and persistence
All state is per platform device. Runtime hardware state persists in TC9563 registers and power/reset lines until power-off or reset. DT properties are cached in `cfg[]`; disabled child nodes become `disable_port=true`. There is no filesystem persistence.

## Dependencies and integration points
The driver depends on regulators, GPIO descriptors, OF/platform matching, I2C transfer APIs, unaligned endian helpers, bitfield helpers, and the PCI pwrctrl core. It matches `pci1179,0623` and is intended to run before PCI enumeration so the switch is configured and released from reset when the PCI core scans the bus.

## Risks
I2C transfer failures abort power-on, but `tc9563_pwrctrl_i2c_write()` returns the raw negative or unexpected transfer count except for success; callers treat any nonzero as failure. Port parsing assumes child order maps to DSP1, DSP2, DSP3 and embedded Ethernet under DSP3; unexpected DT topology could overflow or misassign `port` because the loop increments without an explicit `TC9563_MAX` guard. Only DSP1 and DSP2 have disable sequences; a disabled DSP3 or Ethernet node will flow into the DSP2-style `else` path. Probe error cleanup calls `tc9563_pwrctrl_power_off()` after a failed readiness registration even though power-on may not have occurred. Register sequences include hardcoded offsets from vendor documentation, so review requires hardware validation.

## Test signals
Hardware bring-up should verify regulator order, reset polarity, oscillator delay, I2C endianness, and register values with a logic analyzer or I2C trace. DT tests should cover missing `i2c-parent`, unavailable adapter deferral, bad regulator/GPIO acquisition, each per-port property, disabled ports, embedded Ethernet child parsing, and removal cleanup. PCI enumeration after power-on should show the TC9563 switch and downstream devices with expected ASPM/link behavior.
