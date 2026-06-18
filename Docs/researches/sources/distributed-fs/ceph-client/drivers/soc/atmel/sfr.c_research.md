# sources/distributed-fs/ceph-client/drivers/soc/atmel/sfr.c

## Purpose
This driver exposes Atmel SAMA5D2/SAMA5D4 Special Function Register serial-number words through NVMEM and feeds them into kernel randomness.

## Important APIs, Types, And Functions
`struct atmel_sfr_priv` holds the SFR regmap. `atmel_sfr_read()` reads from `SFR_SN0 + offset` with 32-bit stride. `atmel_sfr_nvmem_config` describes an 8-byte read-only NVMEM provider. `atmel_sfr_probe()` registers the provider and adds serial number bytes to randomness.

## Control Flow
Probe allocates private state, obtains a regmap from the node syscon, fills config `dev` and `priv`, registers NVMEM, reads the full serial number, and calls `add_device_randomness()` if the read succeeds.

## State, Persistence, And Dependencies
State is device-managed private data and the NVMEM registration. Hardware serial registers persist in SoC SFRs. Dependencies include syscon/regmap, NVMEM provider framework, OF/platform binding, and randomness API.

## Integration Points
Consumers can read the serial number through NVMEM. The driver binds to `atmel,sama5d2-sfr` and `atmel,sama5d4-sfr`.

## Risks
The global `atmel_sfr_nvmem_config` is mutated at probe time, which is not ideal for multiple instances. `atmel_sfr_read()` divides bytes by 4 and relies on NVMEM stride/word-size alignment. Returning the serial read result from probe can fail binding if randomness read fails after NVMEM registration.

## Test Signals
Probe both compatibles, read NVMEM bytes, verify regmap bulk read offsets, test error propagation from regmap and NVMEM registration, and check randomness path does not break probe unexpectedly.
