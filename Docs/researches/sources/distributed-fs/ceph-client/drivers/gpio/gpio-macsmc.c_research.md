<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-macsmc.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-macsmc.c

## Purpose
`gpio-macsmc.c` exposes Apple Silicon SMC PMU GPIO keys as a can-sleep gpiochip. It supports reading inputs and writing outputs but does not yet implement mode changes or IRQ configuration.

## Important APIs, types, and functions
`struct macsmc_gpio` stores the Apple SMC pointer, gpiochip, device, and first SMC key index. `macsmc_gpio_key()` builds `gPxx` keys, `macsmc_gpio_nr()` decodes key names, and `macsmc_gpio_find_first_gpio_index()` binary-searches the SMC key table. Operations are get_direction, get, set, and valid-mask initialization.

## Control flow
Probe gets the parent `apple_smc`, finds the first GPIO key, validates that at least one key lies in range, initializes a 64-line dynamic gpiochip, and registers it. Valid-mask initialization walks SMC keys from the first GPIO key until `gPff` or count limit and marks decoded GPIO numbers. Get determines direction, then reads either `CMD_OUTPUT` or `CMD_INPUT`; set writes `CMD_OUTPUT`.

## State and persistence behavior
The SMC owns actual GPIO state and modes. The driver stores only the key-table starting index and derives valid pins at registration. No mode or IRQ state is changed by the driver.

## Dependencies and integration points
It binds to `apple,smc-gpio`, depends on the Apple SMC MFD, SMC key enumeration and u32 read/write commands, and gpiolib valid masks.

## Risks and edge cases
SMC command semantics vary across PMU hardware, especially detailed config bits. Direction detection falls back from pin mode to IRQ mode and treats failure as output. `macsmc_gpio_set()` ORs the command into the value before writing, so command/value encoding must match SMC expectations.

## Test signals
Test key-table binary search on different SMC key layouts, valid-mask decoding for sparse keys, input/output reads, output writes, failure of `CMD_PINMODE` fallback behavior, and absence of unsupported mode/IRQ operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-macsmc.c -->
