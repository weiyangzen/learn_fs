# sources/distributed-fs/ceph-client/drivers/ata/pata_pdc2027x.c

## Purpose
Supports Promise PDC20268 through PDC20277 PATA controllers, including PATA100/PATA133 variants, MMIO taskfile windows, PLL detection/adjustment, and 133 MHz timing table overrides.

## Important APIs, Types, And Functions
Helpers `port_mmio()` and `dev_mmio()` compute register windows. `pdc2027x_cable_detect()`, `pdc2027x_prereset()`, `pdc2027x_mode_filter()`, `pdc2027x_set_piomode()`, `pdc2027x_set_dmamode()`, `pdc2027x_set_mode()`, and `pdc2027x_check_atapi_dma()` implement libata policy. `pdc_read_counter()`, `pdc_detect_pll_input_clock()`, `pdc_adjust_pll()`, and `pdc_hardware_init()` calibrate hardware. `pdc_ata_setup_port()` maps MMIO ATA registers.

## Control Flow
PCI probe allocates a two-port host, enables the device, maps BAR5, sets DMA mask, assigns MMIO command/BMDMA addresses, initializes PLL hardware, enables bus mastering, and activates BMDMA interrupts. For PATA133 variants, libata mode setting is followed by explicit timing table writes because hardware SET FEATURES timing may be wrong at 133 MHz.

## State And Persistence
Controller state persists in MMIO timing/control/PLL registers. No private host data is allocated; `host->iomap` is the key runtime mapping.

## Dependencies And Integration Points
Uses PCI managed resources, libata BMDMA, SCSI command opcodes for ATAPI DMA whitelisting, ktime for PLL measurement, and PM resume reinitialization.

## Risks And Edge Cases
PLL input measurement reads a split decrementing counter and must retry around rollover. The mode filter contains a suspicious Maxtor-related UDMA6 workaround that affects slave devices. ATAPI DMA is whitelisted to avoid lost IRQs. Firmware-disabled ports return `-ENOENT`.

## Test Signals
PDC20268/69/70/71/75/76/77 IDs, 40/80-wire detection, PLL clock on nonstandard PCI clocks, PIO/MDMA/UDMA timing writes, ATAPI DMA whitelist, suspend/resume reinit, and disabled-port handling.
