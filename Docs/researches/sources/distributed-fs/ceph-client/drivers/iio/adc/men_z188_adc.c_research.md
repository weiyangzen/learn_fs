# sources/distributed-fs/ceph-client/drivers/iio/adc/men_z188_adc.c

Purpose: this MCB bus IIO driver supports the MEN 16z188 ADC core. It exposes eight voltage channels with raw readings from memory-mapped registers.

Important APIs, types, and functions: `struct z188_adc` stores the requested memory resource and mapped base address. `z188_iio_read_raw()` reads a channel register, checks the oversampling error bit, and returns extracted data. `men_z188_config_channels()` enables automatic mode and configures all channels for voltage mode with gain bits cleared. `men_z188_probe()` maps resources, configures hardware, and registers IIO; `men_z188_remove()` unregisters and frees resources.

Control flow: probe allocates an IIO device, requests the `z188-adc` MCB memory resource, ioremaps it, configures channels, saves driver data, and registers. A raw read uses channel index times four as the register offset, checks `ADC_OVR`, extracts `ADC_DATA`, and returns `IIO_VAL_INT`. Remove reverses registration, iounmap, and MCB resource ownership.

State and persistence: the driver keeps only mapped resource state. Hardware configuration persists in the ADC control/config registers after probe until device removal or reset. There is no mutex, regulator, buffering, or runtime PM.

Dependencies and integration points: it depends on the MCB subsystem, MMIO accessors, IIO direct mode, and module namespace import `MCB`. Device matching uses MCB device ID `0xbc`.

Risks and test signals: test resource request/map failure paths, eight channel reads, oversampling error handling, and remove cleanup. A risk is the config loop using `addr + i` byte offsets while read channels use `chan * 4`; that should be checked against the hardware register map. Another risk is no serialization around MMIO reads/configuration, though the simple direct-read design may not require it.
