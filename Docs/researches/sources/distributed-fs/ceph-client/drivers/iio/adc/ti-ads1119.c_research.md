# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads1119.c

Purpose: I2C IIO driver for TI ADS1119. It supports firmware-described single-ended or limited differential channels, per-channel gain and data-rate controls, internal or external reference selection, direct single conversions including offset calibration reads, optional DRDY IRQ/trigger, buffered one-hot continuous capture, debugfs register access, reset GPIO, and runtime powerdown.

Important APIs/types/functions: `struct ads1119_state` stores completion, client, reset GPIO, optional trigger, per-channel configs, cached config, and vref. Important functions are `ads1119_upd_cfg_reg()`, `ads1119_reset()`, `ads1119_configure_channel()`, data-ready polling/reading, `ads1119_single_conversion()`, raw read/write/available callbacks, debugfs access, buffer setup ops, IRQ and trigger handlers, channel allocation, probe, and runtime suspend.

Control flow: probe enables AVDD/DVDD, obtains optional external vref or uses internal 2.048 V, gets reset GPIO, builds channels from child `single-channel` or `diff-channels` properties, installs triggered buffer, optionally requests IRQ and registers an own trigger, resets and initializes vref selection, enables runtime PM, registers powerdown cleanup, and registers IIO. Direct raw/offset reads claim direct mode, runtime-resume, configure mux/gain/data rate, optionally use shorted-input mux for offset, send START/SYNC, wait by DRDY completion or polling status, read swapped conversion data, sign-extend, and autosuspend. Buffered capture switches to continuous mode for one active channel, starts conversions, then reads data on trigger.

State and persistence: persistent state is cached config register, channel mux/gain/data-rate table, vref microvolts, completion, trigger, and reset method. Hardware state includes config register fields, conversion mode, selected mux/gain/rate, vref source, and powerdown state.

Dependencies and integration: depends on I2C SMBus byte/word commands, regulators `avdd`, `dvdd`, optional `vref`, optional reset GPIO, optional IRQ, IIO triggers/buffers/debugfs, runtime PM, and firmware child-node channel descriptions.

Risks: differential mapping supports only AIN0-AIN1, AIN1-AIN2, and AIN2-AIN3. If no IRQ is present, polling timeout is based on data rate and maximum DRDY timeout. The cached config must remain synchronized with debugfs writes, but debugfs writes do not update `cached_config`. Buffer preenable sets continuous mode before runtime resume; failures can leave mode changed.

Test signals: single-ended and differential child-node parsing, too-many/invalid channels, internal and external vref paths, reset GPIO and command reset, raw and offset conversions with IRQ and polling, gain/data-rate writes and available lists, one-hot buffered capture, own trigger IRQ behavior, debugfs register reads/writes, runtime powerdown, and timeout paths.
