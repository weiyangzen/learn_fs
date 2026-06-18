# sources/distributed-fs/ceph-client/include/linux/mfd/ezx-pcap.h

Purpose: This file defines the Motorola EZX PCAP2 PMIC/MFD interface. It maps PCAP subdevices, register operations, IRQ translation, ADC access, regulator IDs, interrupt IDs, battery/ADC/USB/LED/RTC fields, and SPI command framing.

Important APIs, types, and functions: `struct pcap_subdev` and `struct pcap_platform_data` describe board-provided child devices, IRQ base, config flags, GPIO, and init callback. `struct pcap_chip` is opaque to children. Exported operations are `ezx_pcap_write`, `ezx_pcap_read`, `ezx_pcap_set_bits`, `pcap_to_irq`, `irq_to_pcap`, `pcap_adc_async`, and `pcap_set_ts_bits`. Register macros cover ISR/MSR, regulators, battery, ADC, audio codec, bus control, RTC, power, peripherals, and masks. Constants define 23 PCAP IRQs, regulator IDs, ADC banks/channels/timing modes, LED/backlight fields, and RTC masks.

Control flow, state, and persistence: The parent PCAP driver frames register read/write operations over the PCAP port, registers MFD children, maps PCAP IRQs into Linux IRQs, and services asynchronous ADC completion callbacks. Persistent state resides in PMIC registers for interrupts, regulators, RTC, ADC monitor configuration, battery charging, LEDs, and bus control.

Dependencies and integration points: It integrates with SPI/GPIO board setup, IRQ domain or legacy IRQ base mapping, regulator, RTC, input/touchscreen, battery, LED/backlight, audio, and USB/transceiver children.

Risks and test signals: Risks include 25-bit register value truncation, wrong port-specific register use, ADC callback lifetime issues, IRQ base translation errors, and regulator ID drift. Test signals include read/write framing tests, interrupt clear/mask tests, async ADC completion and timeout tests, RTC day/time boundary tests, LED/backlight field tests, and suspend/resume retention of regulator and RTC state.
