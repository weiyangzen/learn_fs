# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_pcimio.c

## Purpose
`ni_pcimio.c` is the PCI/PXI/PCIe Comedi wrapper for NI PCI-MIO E-Series, M-Series, S-Series 6143, 611x, 67xx, and many related multifunction DAQ boards. It provides the large PCI board capability table, MITE setup, board-family flag derivation, M-Series EEPROM preload, 6143 initialization, IRQ setup, PCI id binding, and detach cleanup. Core subdevice behavior is provided by the included `ni_mio_common.c` with `PCIDMA` enabled.

## Important APIs, Types, And Functions
The file defines AO range tables for E-Series external reference and M-Series 625x/628x variants, an `enum ni_pcimio_boardid`, and a large `ni_boards[]` table. Each board entry records the Comedi-visible name, optional alternate routing name, AI/AO channel counts and maxdata, FIFO depths, gain table, speed limits, register family, 8255/32-DIO flags, calibration DACs, and DIO timing.

`pcimio_ai_change()`, `pcimio_ao_change()`, `pcimio_gpct0_change()`, `pcimio_gpct1_change()`, and `pcimio_dio_change()` adapt Comedi buffer changes to the corresponding MITE rings. `m_series_init_eeprom_buffer()` temporarily maps a MITE I/O window and copies M-Series calibration EEPROM bytes into `devpriv->eeprom_buffer`. `init_6143()` programs board-specific registers for the simultaneous-sampling 6143 path. `pcimio_auto_attach()` performs PCI attach and delegates common subdevice construction to `ni_E_init()`. `pcimio_detach()` frees IRQs, MITE rings, MITE attachment, MMIO mapping, and PCI resources.

## Control Flow
The PCI table maps NI device ids to board ids. Probe calls `comedi_pci_auto_config()`, which invokes `pcimio_auto_attach()` with the board id. Attach enables PCI resources, allocates common private state, attaches MITE using window 0, derives private family flags from `board->reg_type`, allocates five MITE rings, preloads M-Series EEPROM or initializes 6143 hardware when applicable, requests the IRQ, and calls `ni_E_init(dev, 0, 1)`. After common initialization, attach installs per-subdevice buffer-change callbacks so Comedi async buffer changes update the proper MITE descriptors.

Detach first calls `mio_common_detach()` to destroy NI-TIO counter state, then releases the IRQ, frees all rings, detaches MITE, unmaps MMIO if present, and disables PCI resources. Driver registration is handled by `module_comedi_pci_driver()`.

## State And Persistence Behavior
The board table is static metadata. Runtime state lives in `struct ni_private`, MITE rings/channels, the copied M-Series EEPROM buffer, Comedi subdevices, IRQ state, and MMIO mapping. The EEPROM preload reads persistent hardware calibration data but stores only a volatile copy. The wrapper itself does not write persistent hardware configuration or filesystem state.

## Dependencies And Integration Points
This file depends on Linux PCI/module support, `linux/comedi/comedi_pci.h`, `mite.h`, `ni_stc.h`, and the included common implementation. With `PCIDMA` defined, `ni_mio_common.c` compiles PCI DMA paths, MMIO register accessors, CDIO DMA, GPCT DMA, and MITE-backed AI/AO streaming.

## Risks
The board table is broad and a wrong field can misconfigure channels, timing, FIFO depth, ranges, calibration, register family behavior, or route lookup. Attach has many allocation steps; cleanup relies on detach after partial failures. `m_series_init_eeprom_buffer()` temporarily reprograms MITE window registers and must restore them correctly. Some boards use alternate route names, guessed FIFO depths, or comments noting unsupported/broken features such as SCXI on M-Series and DIO on 673x.

## Test Signals
Validation should include PCI id table coverage, representative attach/detach for each register family, MITE ring allocation failure paths, M-Series EEPROM readback, 6143 initialization, buffer-change callbacks, IRQ request failure behavior, and end-to-end AI/AO/DIO/counter command tests through the common code. Board metadata can be checked by comparing expected Comedi subdevice counts, ranges, maxdata, and timing constraints per board.
