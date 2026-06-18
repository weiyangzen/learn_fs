<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx4581.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx4581.c

Purpose: implements a simple SPI RTC class driver for the Epson RX4581, exposing time read/write only.

Important APIs/types/functions: `rx4581_set_reg()` and `rx4581_get_reg()` implement the SPI register protocol, where read uses the MSB and write uses the low nibble address. `rx4581_get_datetime()` reads a stable time snapshot, and `rx4581_set_datetime()` writes BCD time after stopping the clock. RTC ops expose `read_time` and `set_time`.

Control flow: probe verifies a basic register read, registers the RTC, and stores the RTC pointer as SPI driver data. Read-time checks and clears the update flag, bulk-reads seven time registers, repeats if UF becomes set during the read, warns on low-voltage flag, and decodes BCD fields with a 1970-2069 century heuristic. Set-time builds an 8-byte write buffer, sets STOP, writes time registers, clears VLF, and clears STOP.

State and persistence: hardware persists BCD time, flag register bits, control STOP/RESET bits, RAM, alarm, and timer registers, though this driver uses only time, flags, and STOP. Driver state is only the devm RTC device.

Dependencies and integration points: depends on SPI core, RTC core, BCD helpers, and SPI device ID `rx4581`. It has no OF table, alarm support, IRQ handling, voltage ioctl, or nvmem registration.

Risks and test signals: VLF is logged but read-time still returns success, so consumers may accept unreliable time. If the bulk write fails after STOP is set, the clock may remain stopped. The day-of-week decode uses `ilog2()` and assumes a valid one-hot register. Test SPI mode/speed expected by board data, UF retry loop, VLF read/set-time clear, STOP recovery after failures, year rollover around 2069/2070, and invalid weekday encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx4581.c -->
