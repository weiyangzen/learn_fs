## sources/distributed-fs/ceph-client/drivers/w1/masters/matrox_w1.c

Purpose: this PCI driver bit-bangs a 1-Wire bus through Matrox G400 VGA DDC GPIO-like registers.

Important APIs/types/functions: `struct matrox_device` holds MMIO base/register pointers, data mask, mapped BAR address, and allocated `w1_bus_master`. Helpers read/write indexed DDC registers, initialize hardware, and implement `read_bit`/`write_bit` callbacks.

Control flow: probe validates Matrox G400 PCI IDs, allocates device and bus master together, maps resource 1, computes DDC register addresses, initializes DDC state, assigns w1 bit callbacks, registers the master, and stores driver data. Write-bit uses tristate behavior by driving low for zero and releasing for one; read-bit returns the DDC data register value. Remove unregisters the master, unmaps MMIO, and frees memory.

State and persistence behavior: no persistent state beyond mapped register pointers and bus master registration. Hardware DDC state is directly manipulated per bit.

Dependencies and integration points: depends on PCI, MMIO, Matrox PCI IDs, and w1 core low-level bit callbacks.

Risks: the read callback returns the whole data register, not just a normalized bit, relying on w1 core interpretation. Error path after `w1_add_master_device()` failure unmaps only if mapping exists. Timing is delegated to w1 core bit operations and may vary on legacy hardware.

Test signals: probe/remove on G400, resource mapping failure, DDC line read/write with real hardware, and w1 device discovery over the DDC pins.
