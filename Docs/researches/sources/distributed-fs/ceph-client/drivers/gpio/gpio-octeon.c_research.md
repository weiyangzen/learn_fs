<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-octeon.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-octeon.c

## Purpose
Small Cavium OCTEON GPIO driver exposing 20 non-sleeping lines with input/output direction, set/clear output writes, and input readback.

## Important APIs, types, and functions
`struct octeon_gpio` contains the chip and CSR base. `bit_cfg_reg()` handles the per-line config register stride and discontinuity after line 15. GPIO callbacks are `octeon_gpio_dir_in()`, `octeon_gpio_dir_out()`, `octeon_gpio_get()`, and `octeon_gpio_set()`.

## Control flow
Probe maps the platform resource, stores the base as a CSR address, fills a fixed-base chip with 20 lines, and registers it. Output direction writes the requested level through `TX_SET`/`TX_CLEAR`, then writes `tx_oe` in the config register. Reads use `RX_DAT`.

## State and persistence behavior
No software state or PM context exists; hardware owns direction and values. The chip uses legacy fixed base 0.

## Dependencies and integration points
Depends on OF compatible `cavium,octeon-3860-gpio`, gpiolib, platform MMIO resources, and OCTEON `cvmx_*` CSR helpers.

## Risks and edge cases
Casting the mapped base to `u64` is architecture-specific. Fixed GPIO base 0 can conflict. No IRQ, pinconf, dynamic line count, or context restore exists.

## Test signals
Probe, correct config offsets for lines 0-19, output-before-direction behavior, `RX_DAT` reads, and fixed numbering on OCTEON boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-octeon.c -->
