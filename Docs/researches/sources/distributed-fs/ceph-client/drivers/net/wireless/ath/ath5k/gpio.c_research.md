# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/gpio.c

## Purpose
`gpio.c` controls ath5k GPIO pins and hardware LED pin states. It exposes generic GPIO direction/read/write helpers, configures GPIO interrupts for RFKill, and maps abstract `AR5K_LED_*` states onto `AR5K_PCICFG` LED mode bits. The file covers both GPIO-backed LEDs handled by `led.c` and dedicated LED_0/LED_1 hardware pins controlled directly through PCI configuration bits.

## Important APIs and Control Flow
`ath5k_hw_set_ledstate()` clears existing LED bits and writes a new state. AR5210 has separate LED handling, so the function computes both normal and AR5210 bit patterns. SCAN/AUTH blink pending, INIT turns activity off, ASSOC/RUN selects associated mode, and unknown states fall back to PROM/none.

GPIO helpers are direct register operations with range checks against `AR5K_NUM_GPIO`. `ath5k_hw_set_gpio_input()` and `ath5k_hw_set_gpio_output()` update `AR5K_GPIOCR`; `ath5k_hw_get_gpio()` reads `AR5K_GPIODI`; `ath5k_hw_set_gpio()` updates `AR5K_GPIODO`. `ath5k_hw_set_gpio_intr()` programs GPIO interrupt select/level bits, updates `ah->ah_imr` with `AR5K_IMR_GPIO`, and enables GPIO in `AR5K_PIMR`.

## State, Dependencies, and Integration
Persistent state lives mostly in hardware registers and in `ah->ah_imr`. The file depends on `ath5k_hw_reg_read/write`, `AR5K_REG_ENABLE_BITS`, `AR5K_REG_DISABLE_BITS`, register masks from `reg.h`, and LED/RFKill metadata decoded from EEPROM. Integration points are RFKill switch setup, LED state updates from mac80211 association/scan callbacks, and software LED registration in `led.c`.

## Risks and Test Signals
Risks include invalid GPIO indexes, polarity inversion for RFKill, AR5210 LED bit differences, and `ah->ah_imr` diverging from the hardware IMR if GPIO interrupts are enabled outside normal mask sequencing. Test signals include visible LED transitions for INIT/SCAN/ASSOC, correct GPIO-backed RFKill interrupts on both active-high and active-low switches, no writes for out-of-range GPIOs, and no regression on AR5210 cards.
