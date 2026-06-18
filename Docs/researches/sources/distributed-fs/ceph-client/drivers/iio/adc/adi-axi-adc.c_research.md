# sources/distributed-fs/ceph-client/drivers/iio/adc/adi-axi-adc.c

## Purpose
`adi-axi-adc.c` is a platform driver for Analog Devices AXI ADC FPGA IP cores. It registers an IIO backend that front-end ADC drivers can use for channel enablement, data formatting, DMA buffer allocation, calibration/status checks, sample-trigger polarity, I/O delay tuning, interface alignment, oversampling controls, and raw bus access for AD7606-style child devices.

## Important APIs, Types, and Functions
`struct axi_adc_info` describes expected HDL version, backend info, optional child-node support, and platform data. `struct adi_axi_adc_state` stores match info, MMIO regmap, device pointer, and a mutex for register sequences. Backend ops are grouped into generic AXI ADC, AD485x-specific, and AD408x-specific `struct iio_backend_ops` tables.

Important operations include `axi_adc_enable()/disable()`, `axi_adc_data_format_set()`, `axi_adc_data_sample_trigger()`, `axi_adc_iodelays_set()`, `axi_adc_test_pattern_set()`, `axi_adc_chan_status()`, `axi_adc_chan_enable()/disable()`, `axi_adc_interface_type_get()`, `axi_adc_num_lanes_set()`, DMA buffer request/free, debugfs register/status helpers, AD485x data size and oversampling functions, AD408x filter and data-align functions, and `ad7606_bus_reg_read/write()`.

## Control Flow
Probe maps MMIO, creates a 32-bit regmap, obtains match data and core clock, forces the core into reset, reads and validates the HDL major version, registers the selected IIO backend, and optionally instantiates a child platform device for the `adi,axi-ad7606x` binding. Enable deasserts MMCM reset, polls DRP lock, then releases core reset. Frontend drivers call backend ops to enable/disable channels, configure format sign extension or offset-binary handling, set PN test patterns, request DMAengine buffers, set I/O delays, read PN status, or align AD408x serial data.

The AD7606 bus helper temporarily switches the raw config bus into register mode: reads issue an address with the read bit, fetch `CONFIG_RD`, extract the low byte, then write zero to return to ADC mode; writes similarly encode address and value and restore ADC mode.

## State, Persistence, and Dependencies
State is MMIO hardware state plus the registered backend. There is no persistent storage. Dependencies include platform MMIO resources, clocks, regmap MMIO, IIO backend framework, IIO DMAengine buffers, child platform devices, firmware child nodes, and ADI AXI version helpers.

## Integration Points
This backend is consumed by front-end drivers such as `ad9467.c`. OF compatibles select generic `adi,axi-adc-10.0.a`, `adi,axi-ad408x`, `adi,axi-ad485x`, or `adi,axi-ad7606x`. It imports `IIO_BACKEND` and `IIO_DMAENGINE_BUFFER`, and supplies `ad7606_platform_data` for child bus access.

## Risks and Test Signals
Risks include HDL/driver version mismatch, failing DRP lock, delay-clock problems indicated by all-ones delay readback, incorrect lane count, concurrent raw bus operations without locking, DMA name mismatches, and child-node validation failures. Test by probing each compatible, checking version rejection, enabling/disabling the backend, requesting DMA buffers with default and custom `dma-names`, sweeping I/O delay taps, running PRBS status checks through a frontend, testing AD485x packet-size and oversampling paths, AD408x sync polling, and AD7606 child register reads/writes returning to ADC mode.
