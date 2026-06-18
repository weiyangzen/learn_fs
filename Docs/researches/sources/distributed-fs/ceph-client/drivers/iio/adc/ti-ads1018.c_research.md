# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads1018.c

Purpose: SPI IIO driver for ADS1018/ADS1118 ADCs with voltage and internal-temperature channels. It supports per-channel PGA/data-rate settings, direct one-shot reads, one-hot continuous buffered capture, and an optional data-ready trigger using a shared DRDY/MISO-style line.

Important APIs/types/functions: `struct ads1018` stores SPI device, optional trigger, DRDY GPIO/IRQ, per-channel config, chip info, reusable read message, and aligned buffers. Key routines are `ads1018_calc_delay()`, `ads1018_single_shot()`, raw read/write/available callbacks, trigger state helpers, buffer preenable/postdisable, IRQ handler, trigger handler, trigger setup, and probe.

Control flow: probe initializes channel defaults, builds a reusable read message, optionally creates a DRDY trigger from SPI IRQ or `drdy` GPIO, sets up triggered buffer ops, and registers IIO. Direct raw reads claim direct mode, write a one-shot config with selected mux/PGA/max data rate and optional temp mode, delay for worst-case conversion, read the conversion, shift/sign-extend, and return. Buffer preenable validates a one-hot scan, writes continuous conversion config for the selected channel, and buffer postdisable returns the chip to one-shot mode. Own-trigger enable locks the SPI bus and holds CS low so DRDY can signal; trigger handler reads with exclusive bus/held CS or plain SPI read for external triggers.

State and persistence: persistent state is per-channel PGA/data-rate arrays, optional trigger/IRQ, and SPI message buffers. Hardware state persists in the last written config: one-shot idle or continuous selected channel, data rate, PGA, temp mode, and pull-up/NOP validity bits.

Dependencies and integration: depends on SPI, optional GPIO descriptor and IRQ, IIO trigger/buffer APIs, one-hot scan validation, bitfield helpers, and OF/SPI IDs for ADS1018 and ADS1118.

Risks: DRDY line handling requires holding chip select and locking the SPI controller, so trigger enable/disable must be balanced. IRQ handler checks GPIO level to filter interrupts caused by SPI transfers. Direct reads always use the maximum data-rate delay, independent of per-channel configured rate. Only one channel can be buffered at a time.

Test signals: ADS1018 and ADS1118 gain/data-rate tables, voltage and temperature raw/scale reads, scale and sample-frequency writes/available lists, one-hot scan validation, continuous buffer capture with own and external triggers, DRDY GPIO/SPI IRQ paths, bus lock balancing, and postdisable one-shot config.
