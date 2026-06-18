# sources/distributed-fs/ceph-client/drivers/gpio/gpio-xra1403.c

## Purpose
Supports the EXAR XRA1403 16-bit SPI GPIO expander using regmap-backed direction and value registers, with optional reset GPIO handling and debugfs register dumping.

## Important APIs, Types, And Functions
- `struct xra1403` stores the `gpio_chip` and SPI regmap.
- `xra1403_regmap_cfg` defines the 7-bit register plus pad-bit SPI format.
- `to_reg` maps a 16-bit line offset to low or high byte register addresses.
- `xra1403_direction_input`, `xra1403_direction_output`, `xra1403_get_direction`, `xra1403_get`, and `xra1403_set` implement gpiolib callbacks.
- `xra1403_dbg_show` dumps raw registers and requested line state when debugfs is enabled.
- `xra1403_probe` optionally deasserts reset, initializes regmap, and registers the chip.

## Control Flow
Probe allocates state, requests an optional active-low reset GPIO as output-low to bring the expander out of reset, initializes chip callbacks and metadata, creates an SPI regmap, and registers a 16-line sleepable chip. Direction input sets the bit in `XRA_GCR`; direction output clears the bit and writes the output-control register. Get reads `XRA_GSR`; set updates `XRA_OCR`.

## State And Persistence
No software shadow is maintained. XRA1403 registers store direction, output control, input polarity, pull-ups, interrupt settings, and input filter state. The driver only manipulates direction and output/value registers, while debugfs reads the broader register file.

## Dependencies And Integration Points
Depends on SPI, regmap, optional GPIO descriptor named `reset`, gpiolib, OF compatible `exar,xra1403`, and SPI ID `xra1403`.

## Risks And Edge Cases
If reset GPIO acquisition returns an error, probe only warns and continues, which may leave the expander held in reset on boards where reset is required. Direction-output is non-atomic between direction and value writes. IRQ registers exist but this driver does not wire them into Linux IRQs. Debugfs ignores regmap read errors while building the raw dump.

## Test Signals
Validate low/high byte mapping for offsets 7 and 8, direction bit polarity, output register writes, reset GPIO present/absent/error cases, SPI regmap format, debugfs dump output, and probe from both SPI ID and OF compatible.
