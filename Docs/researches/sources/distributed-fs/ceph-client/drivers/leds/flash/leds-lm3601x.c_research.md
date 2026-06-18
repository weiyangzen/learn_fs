# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-lm3601x.c

## Purpose
This I2C/regmap driver supports Texas Instruments LM36010 and LM36011 flash lighting controllers. It exposes either torch or infrared mode plus flash strobe controls through the LED flash class.

## Important APIs, Types, and Functions
`struct lm3601x_led` stores the flash class device, I2C client, regmap, mutex, cached timeout/faults, firmware current limits, and selected LED mode. Regmap configuration is `lm3601x_regmap`, with `LM3601X_FLAGS_REG` marked volatile. LED flash operations are `lm3601x_brightness_set()`, `lm3601x_strobe_set()`, `lm3601x_flash_brightness_set()`, `lm3601x_flash_timeout_set()`, `lm3601x_strobe_get()`, and `lm3601x_flash_fault_get()`.

## Control Flow
Probe parses the first child node for `reg`, torch max current, flash max current, and max timeout, creates an I2C regmap, tries a software reset, initializes the mutex, and registers a flash LED class device. Torch brightness reads/clears faults, writes the torch register, and sets enable bits for torch or IR mode. Flash brightness writes the flash current register. Strobe computes the timeout register encoding using lower or upper timeout step ranges, sets strobe mode in the enable register, then reads faults.

## State and Persistence
State is volatile and protected by `led->lock`. `flash_timeout` is cached by the timeout setter and applied during strobe. `last_flag` caches translated LED fault bits from the hardware flags register. Regmap caching uses `REGCACHE_MAPLE` for nonvolatile registers.

## Dependencies and Integration Points
The driver depends on I2C, regmap, LED flash class, and firmware node properties. It binds OF compatibles `ti,lm36010` and `ti,lm36011`, plus matching I2C IDs. The LED label defaults to `torch` or `infrared` according to child `reg`.

## Risks and Edge Cases
`lm3601x_parse_node()` stores the child fwnode in an output parameter and then always drops it before returning; this can leave registration with a stale fwnode pointer and should be reviewed. The strobe code compares `led->flash_timeout` in microseconds to a raw register value read from `LM3601X_CFG_REG`, so it may rewrite more often than intended. Timeout mask updates pass an unshifted value to `LM3601X_TIMEOUT_MASK`; this relies on the mask starting at bit 1 and may need field preparation. Fault reads ignore errors in `fault_get()`.

## Test Signals
Test both LM36010 and LM36011 compatibles, torch and IR child `reg` modes, timeout values below and above 400 ms, flash brightness programming, strobe get/set, standby on remove, and fault mapping for timeout, UVLO, thermal, current limit, short, IVFM, and OVP.
