# sources/distributed-fs/ceph-client/drivers/hwmon/nsa320-hwmon.c

Purpose: simple platform hwmon driver for ZyXEL NSA320 boards. It bit-bangs three GPIOs connected to a Holtek MCU that reports chassis fan speed and system temperature.

Important APIs/types/functions: `struct nsa320_hwmon` stores the GPIO descriptors, cached 32-bit MCU word, last update time, and `update_lock`. `nsa320_hwmon_update()` performs the GPIO protocol. `temp1_input_show()`, `fan1_input_show()`, and `label_show()` expose hwmon attributes. Probe obtains `act`, `clk`, and `data` GPIOs and registers attribute groups.

Control flow: sysfs reads call `nsa320_hwmon_update()`. The update path returns cached data for one second, otherwise asserts the active line, waits 100 ms, clocks 32 bits MSB-first with 100-200 us half-periods, deasserts active, validates the magic byte, and caches the word. Temperature is low 16 bits in tenths of a degree and fan speed is the next byte in hundreds of RPM.

State and persistence: only a one-second in-memory cache persists between reads. GPIO levels are initialized through descriptor flags and toggled directly. Invalid reads do not replace the previous cached value.

Dependencies and integration: depends on OF compatible `zyxel,nsa320-mcu`, gpiolib consumer descriptors named `act`, `clk`, and `data`, jiffies, and classic hwmon sysfs groups.

Risks: timing margins are hardware-specific and deliberately long; the protocol resembles SPI but cannot use standard SPI timing. `MAGIC_NUMBER` must remain below 0x80 because errors are negative. Failed reads return `-EIO` encoded through signed `s32`, while `mcu_data` is unsigned in storage.

Test signals: GPIO waveform timing, magic-byte rejection, one-second cache behavior, correct temp/RPM scaling, probe deferral or failure for missing GPIOs, and operation on real NSA320 hardware.
