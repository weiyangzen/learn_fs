# sources/distributed-fs/ceph-client/drivers/siox/siox-bus-gpio.c

Purpose: platform SIOX master that implements the synchronous SIOX push/pull cycle using GPIO descriptors for DIN, DOUT, DCLK, and DLD.

Important APIs and functions: `siox_gpio_probe` allocates a managed `siox_master`, obtains GPIOs with `devm_gpiod_get`, sets `smaster->pushpull`, assigns bus number 0, and registers the master. `siox_gpio_pushpull` toggles load and clock lines, shifts bytes out in inverted DOUT form, samples DIN, observes configurable nanosecond delays, and writes received bytes.

Control flow: platform probe binds via OF compatible `eckelmann,siox-gpio`. Once registered, the SIOX core poll thread calls `pushpull` with prepared output and input buffers for each bus cycle. The GPIO routine clocks the longer of set/get byte counts and handles leading/trailing load pulses.

State and dependencies: per-device GPIO descriptors in `siox_gpio_ddata`; module parameters are static delay globals but not exposed as module_param in this file. Dependencies include GPIO consumer API, platform driver core, SIOX core, and `ndelay`. Risks include sleep-capable GPIO calls inside polling context, fixed `busno = 0`, timing accuracy limits, inverted DOUT protocol assumptions, and no automatic delay discovery. Test signals are OF probe, visible `siox-0` master, oscilloscope-valid GPIO waveforms, successful device status synchronization, and error paths for missing GPIOs.
