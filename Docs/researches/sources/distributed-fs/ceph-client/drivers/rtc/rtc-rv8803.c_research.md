<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv8803.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv8803.c

Purpose: implements Micro Crystal RV8803 and Epson RX8803/RX8804/RX8900 I2C RTCs with time, minute-resolution alarms, voltage status, one-byte NVRAM, wake IRQ support, and RX8900 backup/trickle options.

Important APIs/types/functions: `struct rv8803_data` stores client, RTC, `flags_lock`, cached control register, RX8900 backup options, alarm corruption flag, and chip type. Transfer wrappers `rv8803_read_reg()`, `rv8803_read_regs()`, `rv8803_write_reg()`, and `rv8803_write_regs()` retry around the chip's documented no-ACK window. `rv8803_regs_init()`, `rv8803_regs_reset()`, and `rv8803_regs_configure()` initialize variant-specific registers.

Control flow: probe checks SMBus functionality, reads and warns about voltage/alarm flags, allocates the RTC, requests optional threaded IRQ and wake IRQ, applies RX8900 DT properties, configures WADA and backup control, registers the RTC, and registers 1-byte nvmem. Reads reject alarm-corruption state and V2F, perform a second time read around second 59, and decode BCD. Set-time stops the clock, writes BCD fields, restarts, and clears voltage flags after possible register reset. Alarm set disables AIE/UIE, clears AF, writes minute/hour/day, and re-enables selected interrupts.

State and persistence: hardware keeps time, alarm, flags, control bits, RAM, oscillator offset, and RX8900 backup flags. Driver state caches `ctrl` to coordinate alarm/update interrupt enables and marks invalid alarm registers as data-risk state.

Dependencies and integration points: depends on I2C SMBus block/byte operations, RTC core, nvmem, PM wake IRQ helpers, OF/I2C IDs, and optional wakeup-source property.

Risks and test signals: cached control state must stay synchronized with hardware writes. Invalid BCD alarm values force future time reads to fail until reset through set-time. Test no-ACK retry behavior, V1F/V2F ioctls, alarm invalidation/reset, IRQ flag clearing under mutex, wakeup-source without IRQ, RX8900 `epson,vdet-disable` and `trickle-diode-disable`, suspend/resume wake enable, and nvmem byte access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rv8803.c -->
