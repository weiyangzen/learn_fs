# sources/distributed-fs/ceph-client/drivers/spi/spi-loopback-test.c

## Purpose

`spi-loopback-test.c` is a SPI protocol test driver and reusable test helper implementation. It runs a table of synthetic SPI messages against a target device, optionally requiring physical/controller loopback, to validate controller behavior around transfer lengths, alignment, CS handling, delays, DMA-like boundaries, and RX/TX buffer integrity.

## Important APIs, Types, And Functions

The module parameters control simulation, message dumps, loopback checking, requested `SPI_LOOP`, `SPI_NO_CS`, test/length filtering, vmalloc buffers, range checking, and inter-test delay. The static `spi_tests[]` table defines one-, two-, and three-transfer cases with TX-only, RX-only, full-duplex, page-boundary, overlapping-cacheline, alignment, and delay scenarios.

The driver probe is `spi_loopback_test_probe()`. Exported helpers are `spi_test_execute_msg()`, `spi_test_run_test()`, and `spi_test_run_tests()`. Internal helpers translate symbolic TX/RX offsets into allocated buffers, fill data patterns, dump messages, check modified RX ranges, verify loopback data, and enforce elapsed-time lower bounds.

## Control Flow, State, And Persistence

Probe optionally changes the SPI device mode, then calls `spi_test_run_tests()`. That allocates large TX/RX buffers with `kzalloc()` or `vmalloc()`, iterates the test array, clones each template, expands length/alignment combinations, translates pseudo-pointers, fills TX/RX patterns, executes via `spi_sync()` unless simulating, and validates results. A timed-out message is retried after scheduling.

State is per-run test data and module parameters. The file has no persistent storage, but it exports helpers for other in-kernel SPI tests.

## Dependencies And Integration Points

It depends on SPI core and local `spi-test.h`. It binds by OF compatible `linux,spi-loopback-test`, with a module parameter allowing compatible override. It is a consumer/test driver, not a controller.

## Risks And Test Signals

Risks include destructive runtime cost on real devices, false failures without actual loopback, pointer-template mutation if a copied test is not used correctly, and very verbose logs on dump/error paths. Useful signals are successful completion across controllers, failures pinpointing actual length mismatches, RX writes outside expected ranges, loopback byte mismatches, and elapsed time shorter than physical transfer minimums.
