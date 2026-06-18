# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-gpio.c

Purpose: controls cx25821 GPIO direction/value for board initialization and audio clock output support.

Important APIs and functions: exported `cx25821_set_gpiopin_direction(struct cx25821_dev *dev, int pin_number, int pin_logic_value)` changes output-enable bits for low/high GPIO banks. Static `cx25821_set_gpiopin_logicvalue` sets a pin output value after forcing output direction. `cx25821_gpio_init` applies board-specific GPIO setup.

Control flow: direction helper rejects pin numbers >=47, chooses low or high OE register, reads current OE state, sets or clears the selected bit, and writes the result. Logic-value helper calls direction with output mode, selects low/high data register, updates the bit, and writes it. Board init currently sets GPIO5 high for `CX25821_BOARD_CONEXANT_ATHENA10`/default and delays 20 ms.

State and persistence: GPIO state persists in hardware registers while the device is powered. There is no software shadow; all operations are read-modify-write against MMIO.

Dependencies and integration points: depends on `cx25821.h` register macros, `GPIO_LO`, `GPIO_HI`, `GPIO_LO_OE`, `GPIO_HI_OE`, and `Set_GPIO_Bit`/`Clear_GPIO_Bit`. Core initialization calls `cx25821_gpio_init`, and ALSA start uses `cx25821_set_gpiopin_direction` for audio MCLK-related GPIO0 setup.

Risks: high-bank bit calculation subtracts 31 rather than 32, which may be intentional for register bit layout but is easy to misuse. `pin_logic_value` semantics in the direction helper map 1 to setting the OE bit and 0 to clearing it; comments say GPIOs 0 and 1 are output but implementation is generic. No locking protects concurrent GPIO read-modify-write operations.

Test signals: board bring-up verifying Medusa/Athena path selection on GPIO5, audio capture clock availability on GPIO0, and register readback for low/high GPIO banks.
