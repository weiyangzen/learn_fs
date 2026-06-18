
# sources/distributed-fs/ceph-client/sound/pci/oxygen/oxygen_io.c

Purpose: low-level register, AC97, SPI, I2C, UART, and EEPROM I/O helpers exported to all Oxygen modules.

Important functions: `oxygen_read/write{8,16,32}` wrap port I/O and persist writes into `saved_registers`; masked variants do read-modify-write with saved-state updates. `oxygen_write_ac97`, `oxygen_read_ac97`, and masked AC97 writes implement retry/verification around unreliable AC97 transactions. `oxygen_write_spi`, `oxygen_write_i2c`, UART reset/write, and EEPROM read/write provide board-code transport primitives.

Control flow: AC97 waits on `ac97_waitqueue` but also polls status because interrupts may be disabled. Writes require two completions; reads require two equal values with inversion between attempts. SPI writes data bytes then triggers and waits for not-busy. I2C uses a conservative sleep before writing bus registers.

State/persistence: MMIO writes update `saved_registers`; successful AC97 writes update `saved_ac97_registers`. These are consumed by `oxygen_pci_resume`.

Risks: timing-sensitive hardware access, port-I/O ordering, and cached state consistency. Tests should stress AC97 read/write retries, SPI/I2C codec programming, suspend/resume register restore, EEPROM repair path, and error logging on timeout.
