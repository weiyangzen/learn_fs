# sources/distributed-fs/ceph-client/drivers/iio/adc/aspeed_adc.c

## Purpose
`aspeed_adc.c` is a platform IIO ADC driver for Aspeed AST2400, AST2500, AST2600 ADC0/ADC1, and AST2700 ADC0/ADC1 controllers. It exposes direct voltage channels, scale, sample frequency, offset compensation, optional battery-sensing mode, trim-data loading from syscon OTP fields, and controller clock-divider setup.

## Important APIs, Types, and Functions
`struct aspeed_adc_model_data` captures per-SoC capabilities: sample-rate range, fixed reference voltage, init-sequence polling requirement, prescaler need, battery-sensing support, scaler width, channel count, and trim location. `struct aspeed_adc_data` stores device/model pointers, MMIO base, clock hardware, reset control, vref, sample period, compensation value, and battery-sensing gain.

Important helpers are `aspeed_adc_channels_mask()`, `aspeed_adc_get_active_channels()`, `aspeed_adc_set_trim_data()`, `aspeed_adc_compensation()`, `aspeed_adc_set_sampling_rate()`, `aspeed_adc_read_raw()`, `aspeed_adc_write_raw()`, `aspeed_adc_reg_access()`, `aspeed_adc_vref_config()`, and probe. Channel tables cover 16 normal channels and an 8-channel battery-sensing variant where channel 7 has distinct offset handling.

## Control Flow
Probe allocates IIO state, maps MMIO, registers a fixed divide-by-2 clock from the DT parent, optionally registers a prescaler, registers the scaler divider, deasserts reset with managed cleanup, configures reference voltage from fixed model data, optional `vref`, or `aspeed,int-vref-microvolt`, loads trimming data from syscon, detects `aspeed,battery-sensing`, enables the scaler clock, sets the default 65 kS/s sampling rate, starts the engine in normal mode, optionally waits for `INIT_RDY`, computes compensation by enabling compensation sensing and averaging 16 samples from channel 0, enables all normal channels, and registers IIO.

Raw reads return 10-bit MMIO samples. For the battery channel on capable controllers, the driver temporarily enables channel 7 and battery-sensing mode, waits for settling, applies the configured divider gain, and restores the control register. Offset returns the computed compensation value, also gain-adjusted for battery sensing. Scale returns `vref_mv / 2^10`, and sample frequency is derived from the scaler clock divided by 12 conversion clocks. Writes allow only sample frequency changes; raw and scale writes return `-EPERM`.

## State, Persistence, and Dependencies
Runtime state includes clock-divider configuration, reset state, reference selection bits, trim register value, compensation value, sample period, channel-enable bits, and optional battery-sensing mode. Dependencies include platform MMIO, reset controls, clock provider/divider APIs, regulators, syscon regmap, OF properties, IIO direct mode, and debugfs register access.

## Integration Points
The driver binds to Aspeed OF compatibles for AST2400/2500/2600/2700 variants. It consumes optional `vref`, `aspeed,int-vref-microvolt`, and `aspeed,battery-sensing`, and looks up the global `syscon` node for trim fields.

## Risks and Test Signals
Risks include incorrect vref units or range handling, syscon lookup fragility, sample-rate divider rounding, compensation timing, battery channel control-register restoration, and channel-count differences between 16-channel and 8-channel controllers. Test by probing all model data variants, verifying sample-frequency set/get boundaries, checking scale for fixed/internal/external references, confirming compensation offset is stable, reading normal and battery channels, validating `INIT_RDY` timeout behavior, and using debugfs reg access only on aligned valid registers.
