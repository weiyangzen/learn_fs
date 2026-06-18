# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54pci.c

## Purpose
This file implements the Prism54 PCI frontend. It probes PCI devices, requests firmware asynchronously, uploads LM86 firmware through direct memory windows, manages DMA descriptor rings, handles interrupts/tasklets, bridges p54 common TX/RX callbacks to PCI DMA, and performs suspend/resume basics.

## Important APIs, Types, and Functions
- `p54p_table[]` lists supported PCI IDs.
- `p54p_upload_firmware()` resets the device, parses firmware, verifies LM86, writes firmware chunks into device memory, and boots RAM firmware.
- `p54p_refill_rx_ring()`, `p54p_check_rx_ring()`, and `p54p_check_tx_ring()` manage descriptor ring buffers and DMA ownership.
- `p54p_interrupt()` acknowledges interrupts and schedules `p54p_tasklet()` or completes boot.
- `p54p_tx()` maps SKBs into TX descriptors and rings the device.
- `p54p_open()` and `p54p_stop()` implement p54 common bus callbacks.
- `p54p_probe()`, `p54p_firmware_step2()`, and `p54p_remove()` implement device lifecycle.

## Control Flow
Probe enables the PCI device, validates BAR size, requests regions, sets 32-bit DMA masks, enables bus mastering/MWI, allocates common hw, maps registers, allocates coherent ring control, installs bus callbacks, initializes locks/tasklet/completion, and starts asynchronous firmware request. Firmware callback opens the device once, reads EEPROM through common firmware I/O, stops the device, then registers mac80211 hardware; on error it releases the driver.

Open requests IRQ, clears rings, uploads firmware, refills RX data/management rings, programs ring-control DMA address, enables INIT interrupt, resets the device, waits for boot completion, then enables UPDATE interrupts. Runtime interrupts acknowledge the device and schedule a tasklet. The tasklet reclaims TX rings, processes RX rings through `p54_rx()`, refills RX descriptors, and notifies firmware of updates. Stop disables interrupts, frees IRQ/tasklet, resets the device, unmaps/free all RX/TX SKBs, and zeroes ring control.

## State and Persistence Behavior
PCI-private persistent state includes mapped CSR pointer, coherent `p54p_ring_control`, ring DMA address, per-ring host/device indexes, RX/TX SKB arrays, firmware pointer, tasklet, IRQ state, and completions. Firmware image is held until remove. DMA descriptors persist while device is open.

## Dependencies and Integration Points
It depends on PCI core, DMA mapping, firmware loader, tasklets, IRQs, p54 common APIs, p54 LMAC header macros, and mac80211 registration through common code. It exports no symbols; the module is registered with `module_pci_driver()`.

## Risks and Edge Cases
DMA is limited to 32 bits. Firmware must be LM86 for PCI. Ring logic must keep descriptor arrays, SKB arrays, and device indexes synchronized. Asynchronous firmware callback races removal, handled by `fw_loaded` completion and `pci_dev_get/put`. Stop must unmap both RX and TX descriptors even if partially initialized. Suspend/resume saves state and power-cycles PCI but relies on higher layers to stop/start cleanly.

## Test Signals
Signals include PCI probe, firmware upload/boot completion, EEPROM read, mac80211 registration, RX/TX traffic through rings, interrupt/tasklet activity, clean remove while firmware request is pending, and suspend/resume without leaked DMA mappings.
