# sources/distributed-fs/ceph-client/drivers/video/backlight/tdo24m.c

Purpose: SPI LCD panel driver for Toppoly TDO24M/TDO35S panels. It registers an LCD class device, sends packed controller command sequences over SPI, and supports VGA/QVGA mode changes.

Important APIs/types/functions: `struct tdo24m` stores SPI device, LCD device, reusable `spi_message`/`spi_transfer`, command buffer, power, mode, and model-specific `adj_mode` callback. Command macros `CMD0`, `CMD1`, and `CMD2` pack register writes. `tdo24m_writes()` serializes command arrays. `tdo24m_power()`, `tdo24m_set_power()`, and `tdo24m_set_mode()` implement LCD behavior.

Control flow: probe configures SPI mode 3 and 8-bit words, allocates state/buffer, initializes transfer, selects TDO24M or TDO35S sequences from platform data, registers the LCD device, stores drvdata, and powers the panel on. Power-on sends display-on, reset, and mode-adjust sequences; power-off sends sleep/deep-standby sequence. Mode selection treats either xres 640 or 480 as VGA; all other inputs become QVGA.

State and persistence: `power` and `mode` are cached in memory. Panel registers retain the last SPI-programmed state while powered.

Dependencies and integration: SPI core, LCD class, legacy `linux/spi/tdo24m.h` platform data, PM sleep hooks, shutdown power-off.

Risks: several nested `tdo24m_writes()` calls ignore intermediate return values in mode adjustment and continue after failed command batches. Timing relies only on command order, not explicit panel delays except SPI completion. Tests should cover model selection, packed command byte layout, color-invert skip for `CMD0(0x21)`, mode transitions, suspend/resume, and shutdown.
