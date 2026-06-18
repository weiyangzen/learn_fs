# sources/distributed-fs/ceph-client/drivers/staging/fbtft/internal.h

## Purpose

`internal.h` is the small internal declaration header shared by FBTFT core and sysfs files. It keeps sysfs and parser helpers out of the main panel-driver-facing header surface.

## Important APIs, Types, and Functions

It declares `fbtft_sysfs_init()`, `fbtft_sysfs_exit()`, `fbtft_expand_debug_value()`, and `fbtft_gamma_parse_str()`.

## Control Flow

`fbtft-core.c` includes this header to call sysfs setup/teardown, debug expansion, and property gamma parsing. `fbtft-sysfs.c` provides the definitions.

## State and Persistence Behavior

The header owns no state. The declared functions operate on `struct fbtft_par` state allocated by the core.

## Dependencies and Integration Points

It assumes `struct fbtft_par` and `u32` are visible through inclusion order, normally by including `fbtft.h` first.

## Risks and Edge Cases

The header does not include `fbtft.h` itself, so direct inclusion without prior type declarations can fail. That is acceptable for a narrow internal header but fragile if reused.

## Test Signals

Compile all FBTFT translation units with include-order warnings and ensure no external panel driver needs this header directly.
