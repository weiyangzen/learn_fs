# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fbtft-io.c

## Purpose

`fbtft-io.c` provides low-level bus write/read helpers used by the FBTFT core and panel drivers. It covers normal SPI transfers, software-emulated 9-bit SPI, SPI reads with optional startbyte, and GPIO-parallel write strobes for 8-bit and 16-bit buses.

## Important APIs, Types, and Functions

Exported functions are `fbtft_write_spi()`, `fbtft_write_spi_emulate_9()`, `fbtft_read_spi()`, `fbtft_write_gpio8_wr()`, `fbtft_write_gpio16_wr()`, and the unimplemented `fbtft_write_gpio16_wr_latched()`. The file consumes `struct fbtft_par`, especially `par->spi`, `par->extra`, `par->startbyte`, and `par->gpio.wr/db[]`.

## Control Flow

SPI write wraps one `spi_transfer` in a synchronous message. Emulated 9-bit SPI treats the source buffer as 16-bit words containing a 9th D/C bit, packs groups into big-endian 8-byte chunks plus an added byte, and sends the transformed buffer through `spi_write()`. SPI read optionally sends a startbyte prefix and then performs a synchronous transfer. GPIO write helpers toggle `/WR`, set changed data bits on the db lines, and restore the strobe for each byte or word.

## State and Persistence Behavior

The file does not own persistent state. It mutates bus pins and uses `par->extra` as a transient conversion buffer. The optimized GPIO paths keep static `prev_data` values, so data-line caching is shared across all users of that function in the kernel image.

## Dependencies and Integration Points

It depends on Linux SPI and gpiod APIs and is selected by `fbtft_probe_common()` based on bus mode. Debug output uses FBTFT debug macros from `fbtft.h`.

## Risks and Edge Cases

`fbtft_write_spi()` returns `-1` instead of a conventional errno when `par->spi` is missing. Emulated 9-bit SPI requires length divisible by 8 and assumes `par->extra` is large enough for the transformed stream. The static GPIO `prev_data` optimization is unsafe if multiple displays or different GPIO buses use the helper concurrently because cached previous bus state is global. The 16-bit GPIO path assumes even `len`; odd lengths would underflow logical packet framing. The latched 16-bit helper is exported but always fails.

## Test Signals

Exercise SPI transfer failure, absent SPI device, startbyte reads at and above the 32-byte limit, 9-bit emulation packing with known vectors, GPIO writes with repeated and changing data, concurrent multi-device GPIO users, and callers that request the unimplemented latched helper.
