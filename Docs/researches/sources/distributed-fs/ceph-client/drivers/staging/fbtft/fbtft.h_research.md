# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fbtft.h

## Purpose

`fbtft.h` is the public-private header for staging FBTFT panel drivers. It defines display/platform data, the operation callback table, per-device runtime state, exported helper prototypes, driver-registration macros, and debug bit definitions.

## Important APIs, Types, and Functions

Core types are `struct fbtft_ops`, `struct fbtft_display`, `struct fbtft_platform_data`, and `struct fbtft_par`. The header declares core, I/O, and bus helper functions and defines `write_reg()`/`NUMARGS()` for variable-length controller register writes. Registration macros `FBTFT_DT_TABLE`, `FBTFT_SPI_DRIVER`, `FBTFT_REGISTER_DRIVER`, and `FBTFT_REGISTER_SPI_DRIVER` scaffold SPI and platform drivers around `fbtft_probe_common()` and `fbtft_remove_common()`.

## Control Flow

Panel drivers fill `struct fbtft_display`, optionally override `fbtft_ops`, and use the macros to generate standard probe/remove paths. At runtime, the core stores device state in `struct fbtft_par`, with operation pointers selected from defaults and driver/platform overrides.

## State and Persistence Behavior

`struct fbtft_par` holds all long-lived per-display kernel state: SPI/platform pointers, framebuffer pointer, platform data, pseudo palette, transmit and scratch buffers, GPIO descriptors, dirty-line tracking, gamma data, debug flags, update timing, BGR/extra settings, and backlight polarity. Nothing in this header implies file persistence.

## Dependencies and Integration Points

The header depends on Linux fbdev, spinlocks, SPI, platform devices, GPIO descriptors, mutexes through included contexts, and ASoC-independent FBTFT bus implementations. It is the integration contract between generic core code and many small panel drivers.

## Risks and Edge Cases

`write_register` is a varargs function, so type/length correctness is entirely caller/callee discipline. Registration macros create static symbols with fixed names, so each translation unit can instantiate only one generated driver family cleanly. Debug bits extend to bit 31 and shorthand expansion can set all bits. The comments mention unused or legacy fields such as `ssbuf`, reflecting staging-level API churn.

## Test Signals

Compile representative panel drivers using both registration macros. Check structure layout assumptions, operation override precedence, varargs register-write call sites, debug mask behavior, and include-order dependencies across SPI-only and platform-capable builds.
