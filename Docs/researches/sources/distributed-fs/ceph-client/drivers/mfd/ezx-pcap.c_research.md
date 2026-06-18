# sources/distributed-fs/ceph-client/drivers/mfd/ezx-pcap.c

## Purpose
`ezx-pcap.c` is the SPI MFD core for the Motorola PCAP2 ASIC used in EZX phones. It provides serialized register I/O, a cascaded IRQ chip, asynchronous ADC request queueing, and platform-data-defined subdevice registration.

## Important APIs, Types, and Functions
`struct pcap_chip` stores SPI state, I/O lock, IRQ mask state, workqueue/work items, and ADC queue state. Exported register helpers are `ezx_pcap_write()`, `ezx_pcap_read()`, and `ezx_pcap_set_bits()`. IRQ helpers `irq_to_pcap()` and `pcap_to_irq()` map between Linux IRQs and PCAP local IRQs. `pcap_irq_chip`, `pcap_isr_work()`, and `pcap_irq_handler()` implement cascaded interrupts. ADC APIs include `pcap_set_ts_bits()` and `pcap_adc_async()`, with completion in `pcap_adc_irq()`.

## Control Flow
Probe requires platform data, configures 32-bit SPI mode and chip select polarity, initializes locks/work, creates an ordered workqueue, optionally redirects interrupts to the application processor, installs simple IRQ handlers for `PCAP_NIRQS`, masks and clears all PCAP interrupts, chains the parent SPI IRQ, requests the ADC done IRQ, registers platform subdevices, and runs optional board init. The chained handler ACKs the parent and schedules work; work reads mask/status, filters port-2 interrupts, acks serviceable events, dispatches unmasked local IRQs, and repeats while the GPIO line remains asserted. ADC requests are queued in an 8-slot ring and completed by the ADC IRQ callback.

## State and Persistence
Runtime state includes current mask shadow `msr`, queued ADC requests, queue head/tail, and child platform devices. Hardware state includes PCAP registers for IRQ masks/status, ADC configuration, and board-specific init. No persistent storage exists.

## Dependencies and Integration Points
The driver depends on SPI, legacy GPIO APIs, platform data, Linux IRQ core, workqueues, and PCAP register definitions. Child devices are platform-data-defined rather than OF/devm MFD cells.

## Risks and Edge Cases
The driver relies on legacy fixed IRQ bases and platform data. ADC queue size is fixed at eight and returns `-EBUSY` on full slot. IRQ mask/unmask work is asynchronous, so rapid mask changes can lag hardware. Parent IRQ wake is enabled but not disabled in remove. Subdevice creation is manual and cleanup must match all failure paths.

## Test Signals
Validate 32-bit SPI transfers, read/write/set_bits serialization, cascaded IRQ dispatch and mask writes, port-2 filtering, ADC queue full behavior, ADC result channel selection, child device registration/removal, and board init quirks.
