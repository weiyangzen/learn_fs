<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ich.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ich.c

## Purpose
`gpio-ich.c` exposes GPIO lines in Intel ICH6-10, Series 5/6, Atom C2000, Avoton/Rangeley, and related LPC bridges. It operates on legacy I/O-port resources provided by the LPC ICH MFD layer and handles chipset-specific register layouts and quirks.

## Important APIs, types, and functions
`struct ichx_desc` describes per-chip register offsets, line count, blink support, GPE0 usage, ignored `USE_SEL` bits, and optional request/get overrides. Global `ichx_priv` stores the single active instance. Core helpers are `ichx_write_bit()`, `ichx_read_bit()`, direction/get/set/request functions, `ichx_gpio_request_regions()`, and `ichx_gpio_probe()`.

## Control flow
Probe selects a descriptor from `lpc_ich_info->gpio_version`, requests the usable I/O register regions, optionally requests the PM/GPE0 I/O region, configures a gpiochip, and registers it. Reads and writes compute register group and bit from absolute GPIO offset. ICH6/3100 variants special-case GPIO 0-15 through PM GPE0 status and GPIO 16/17 through alternate `USE_SEL` bits.

## State and persistence behavior
Most state is hardware register state. Avoton uses `outlvl_cache[]` because its output levels cannot be read reliably from `GPIO_LVL`; cached bits are ORed with read hardware values and updated on writes. The global private object means one system-wide instance, not multiple independent devices.

## Dependencies and integration points
The driver is a platform child of `lpc_ich`, consumes `struct lpc_ich_info`, uses `inl()`/`outl()` I/O-port access, and exposes a gpiolib chip with optional module parameter `gpiobase`.

## Risks and edge cases
Global state prevents multiple concurrent ICH GPIO instances. Direction and request operations rely on BIOS `USE_SEL` setup except for known ignored bits. Many pins are input-only or output-only, so write-then-verify can return `-EPERM`. Avoton cache can diverge if firmware or another agent modifies output levels.

## Test signals
Test descriptor selection for each `gpio_version`, region conflicts, ICH6 GPE0 reads, fixed-base and dynamic-base registration, input-only/output-only verification failures, Avoton cached output behavior, and blink-disable on GPIO 0-31 outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-ich.c -->
