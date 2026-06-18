<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/warp.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/warp.c

Purpose: implements PIKA Warp board support, including OF bus probing, machine descriptor, POST reporting, optional digital temperature monitor thread, critical-temperature shutdown handling, fan monitoring, and manual LED GPIO setup.

Important APIs/types/functions: `warp_device_probe()` probes PLB/OPB/EBC buses; `define_machine(warp)` installs UIC and reset hooks; `warp_post_info()` reads FPGA POST words; under `CONFIG_SENSORS_AD7414`, `pika_setup_leds()` acquires green/red LED GPIOs and registers `leds-gpio`, `pika_setup_critical_temp()` programs the AD7414 and IRQ, `temp_isr()` enters emergency LED blink/reset loop, `pika_dtm_thread()` polls temperature and fan status, and `pika_dtm_start()` maps the FPGA and starts the kernel thread.

Control flow: base late init prints POST info if temperature support is absent. With AD7414 support, late init maps the FPGA, prints POST, starts `pika-dtm`, finds the AD7414 I2C client, sets LED ownership, programs high/low temperature thresholds, requests the critical-temp IRQ, then once per second reads temperature, mirrors it to FPGA offset `0x20`, and checks fan error state. Critical temperature disables local IRQs, turns green LED off, logs emergency text, repeatedly pokes an FPGA reset register, toggles red LED, and never returns.

State and persistence: global `dtm_fpga` stores mapped FPGA registers; `warp_gpio_led_pins` hold GPIO descriptors; `warp_gpio_leds` persists as a platform device; the DTM kernel thread persists until stopped; static fan state prevents repeated logs. Hardware state includes FPGA temperature mirror, LED outputs, AD7414 thresholds, and critical IRQ registration.

Dependencies and integration: depends on OF nodes `pika,warp`, `pika,fpga-sd`, `pika,fpga`, `warp-power-leds`, and `adi,ad7414`, UIC, I2C, gpiod, LEDs GPIO platform driver, kthreads, and PPC4xx reset.

Risks and test signals: critical ISR loops forever in interrupt context; LED GPIO acquisition bypasses DT automatic LED registration intentionally; thread startup requires the I2C device to exist; `dtm_fpga` is not unmapped on normal thread lifetime. Test Warp boot with and without AD7414 support, POST logging, LED registration, temperature polling, fan fault log throttling, critical-temp IRQ behavior on hardware, and reset path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/warp.c -->
