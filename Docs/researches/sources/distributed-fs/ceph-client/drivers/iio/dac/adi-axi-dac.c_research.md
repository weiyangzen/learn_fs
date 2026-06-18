## sources/distributed-fs/ceph-client/drivers/iio/dac/adi-axi-dac.c

Purpose: Implements the Analog Devices AXI DAC FPGA IP as an IIO backend rather than as a direct DAC frontend. It exposes enable/disable, DMA buffer setup, data source selection, debugfs register access, DDS tone attributes, and a custom register bus path used by the `adi,axi-ad3552r` high-speed child integration.

Important APIs/types/functions: `struct axi_dac_state` stores the MMIO `regmap`, mutex, backend metadata, sampled DAC clock rate, and read-only config. `struct axi_dac_info` selects generic vs AD3552R behavior. Backend operations are split between `axi_dac_generic_ops` and `axi_ad3552r_ops`. Key functions include `axi_dac_enable()`, `axi_dac_disable()`, `axi_dac_request_buffer()`, `axi_dac_extend_chan()`, `axi_dac_data_source_set/get()`, `axi_dac_set_sample_rate()`, `axi_dac_bus_reg_read/write()`, and `axi_dac_create_platform_device()`.

Control flow: probe enables the AXI clock, optionally enables `dac_clk`, maps MMIO, resets the core, checks the IP major version, reads `AXI_DAC_CONFIG_REG`, forces `R1_MODE`, initializes the mutex, and registers an IIO backend. For the AD3552R compatible, child firmware nodes are validated and turned into platform devices with bus callbacks. Runtime backend calls then set reset bits, wait for DRP lock, allocate DMAengine output buffers, select internal tone/DMA/ramp sources, and manage the custom bus stream FSM.

State and persistence: State is volatile FPGA register state plus `st->dac_clk`, which is used to preserve DDS output frequency across sample-rate changes by reading the old tuning word and rewriting it for the new rate. No NVM is written. Mutex locking protects multi-register sequences and shared cached rate data.

Dependencies and integration points: Depends on `linux/adi-axi-common.h`, `regmap_mmio`, clocks, platform firmware properties, IIO backend APIs, and `iio_dmaengine_buffer_setup_ext()`. It imports `IIO_BACKEND` and `IIO_DMAENGINE_BUFFER` namespaces and integrates with `ad3552r-hs.h` through platform data bus callbacks.

Risks and test signals: Validate IP version mismatch handling, DRP-lock timeout, DDS-disabled paths, sample-rate retuning, custom bus busy timeout, child node `reg` validation, and DMA name fallback from `dma-names` to `tx`. Hardware tests should cover generic AXI DAC and AD3552R child operation, including debugfs register reads, stream enable/disable, DDR toggling, and ext-info frequency/phase/scale round trips.
