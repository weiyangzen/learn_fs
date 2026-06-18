# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgs8gxx.c

## Purpose
`lgs8gxx.c` is the broader Legend Silicon GB20600/DMB-TH demodulator family driver for LGS8913, LGS8GL5, LGS8G75, and experimental LGS8G42/G52/G54 variants. It programs ADC/IF/TS modes, performs auto-detection of guard interval and transmission parameters, optionally loads LGS8G75 firmware, and exposes DTMB frontend operations.

## Important APIs, Types, and Functions
Core helpers are `lgs8gxx_write_reg()`, `lgs8gxx_read_reg()`, `lgs8gxx_soft_reset()`, and `wait_reg_mask()`. Configuration helpers include `lgs8gxx_set_ad_mode()`, `lgs8gxx_set_if_freq()`, `lgs8gxx_set_mode_auto()`, `lgs8gxx_set_mode_manual()`, `lgs8gxx_set_mpeg_mode()`, `lgs8g75_set_adc_vpp()`, `lgs8913_init()`, and `lgs8g75_init_data()`. Locking paths are `lgs8gxx_wait_ca_lock()`, `lgs8gxx_is_autodetect_finished()`, `lgs8gxx_autolock_gi()`, `lgs8gxx_auto_detect()`, and `lgs8gxx_auto_lock()`. DVB callbacks include init, write, I2C gate control, set frontend, tune settings, status, BER, signal strength, SNR, ucblocks, and release.

## Control Flow
Attach validates config/I2C, allocates state, probes register 0, installs ops, and for LGS8G75 downloads `lgs8g75.fw` into device memory. Init optionally sets LGS8G75 ADC range, configures MPEG output, runs LGS8913-specific setup, writes IF frequency NCO, and configures ADC input mode. Set-frontend invokes the tuner and then `lgs8gxx_auto_lock()`: the driver switches to auto mode, tries guard intervals and CPN combinations with soft resets and lock polling, reads detected parameters, applies product-specific fixes, stores current guard interval, and switches to manual mode. Status checks product-specific lock registers; signal metrics use either LGS8913 CIR scanning/fake signal, LGS8G75 level registers, or generic AGC categories.

## State and Persistence
`struct lgs8gxx_state` retains the config, I2C adapter, frontend, and current guard interval. Device registers and optional downloaded firmware hold the meaningful demodulator state. No suspend cache exists. BER measurement temporarily starts/stops packet counters and reads volatile total/error registers.

## Dependencies and Integration Points
The driver depends on Linux firmware loading, I2C, DVB frontend core, `do_div()` math, product IDs from `lgs8gxx.h`, private mode constants from `lgs8gxx_priv.h`, and external tuner callbacks. It exports `lgs8gxx_attach()`, registers module firmware `lgs8g75.fw`, and advertises `SYS_DTMB`.

## Risks and Edge Cases
Firmware load failure for LGS8G75 is not propagated by attach, so the frontend can be returned after a failed init-data download. Many helper failures return `-1` or are ignored, making root-cause diagnosis harder. `fake_signal_str` defaults on for LGS8913 because real strength scanning is slow. Auto-detect retries are limited and may fail without detailed error propagation. Alternate I2C address selection for non-LGS8G75 registers above `0xC0` must match board routing.

## Test Signals
Test each product id that has board support, LGS8G75 firmware request and register download, IF/baseband and external ADC combinations, serial/parallel TS and clock polarity/gating, tuner I2C gate writes, auto-lock across guard intervals, lock status mapping, BER packet-counter reads, LGS8913 fake and real signal modes, and attach cleanup after I2C probe failures.
