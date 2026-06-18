# sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pci263.c

## Purpose
This compact Comedi PCI driver supports the Amplicon PCI263 relay output board. It exposes one 16-channel digital-output subdevice where each bit controls a reed relay and where the output state can be read back from the board's two output registers.

## Important APIs, Types, and Functions
The register map is two byte-wide output ports: `PCI263_DO_0_7_REG` and `PCI263_DO_8_15_REG`. `pci263_do_insn_bits()` is the only subdevice operation; it uses `comedi_dio_update_state()` to merge mask/data writes into `s->state`, writes low and high bytes to hardware, and returns the current state in `data[1]`. `pci263_auto_attach()` enables PCI resources, records BAR2 as `dev->iobase`, allocates one subdevice, initializes its Comedi metadata, and reads the initial relay state. PCI registration is through `amplc_pci263_pci_table` and `module_comedi_pci_driver()`.

## Control Flow
Probe calls Comedi PCI auto-config and then `pci263_auto_attach()`. Attach enables the PCI device, sets up a single writable digital-output subdevice with 16 one-bit channels, and seeds `s->state` from the two hardware bytes so software readback starts in sync with relay hardware. During `insn_bits`, Comedi provides a mask and desired bits; the driver updates `s->state` only if requested bits changed, writes both output bytes, then reports the shadow state.

## State and Persistence Behavior
State is limited to `s->state`, which mirrors the relay output latch. The relay contacts and output latch persist in hardware while the board is powered and are read during attach. There is no private allocation, interrupt state, command state, or disk persistence.

## Dependencies and Integration Points
The file depends on Comedi PCI helpers, Comedi DIO instruction helpers, `range_digital`, PCI vendor ID definitions, and byte port I/O. It integrates with Amplicon PCI device ID 0x000c and exposes a standard `COMEDI_SUBD_DO` subdevice.

## Risks
The driver always writes both bytes after a masked state update, so concurrent users must rely on Comedi serialization around instructions. Relay outputs are physical actuators: stale initial hardware state or unexpected writes can change external circuits. There is no debounce, timing, or relay-settling handling because this is a simple latch driver.

## Test Signals
Validate PCI attach/detach, initial state readback from both bytes, masked writes to low and high relay channels, no hardware write when `comedi_dio_update_state()` reports no change, readback consistency after repeated writes, and behavior across module unload/reload with relays left in nonzero states.
