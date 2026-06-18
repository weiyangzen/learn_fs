# sources/distributed-fs/ceph-client/drivers/spi/spi-test.h

## Purpose
`spi-test.h` defines the shared data structures, constants, buffer markers, fill modes, iteration lengths, and function prototypes used by SPI self-test code in this driver tree. It is not a controller driver; it describes reusable SPI transfer test cases that can be executed against a `struct spi_device`.

## Important APIs, Types, And Functions
The central type is `struct spi_test`. It contains a human-readable description, a template `spi_message`, up to `SPI_TEST_MAX_TRANSFERS` transfer descriptors, callback hooks for running or executing tests, an expected return code, iteration controls for length and buffer alignment, fill-pattern settings, and elapsed-time storage.

The header declares `spi_test_run_test()`, `spi_test_execute_msg()`, and `spi_test_run_tests()`. It defines symbolic dummy buffer address macros `RX(off)` and `TX(off)`, maximum sizes (`SPI_TEST_MAX_SIZE`, `SPI_TEST_MAX_ITERATE`), validation patterns for unwritten or protected regions, fill modes such as `FILL_MEMSET_*`, `FILL_COUNT_*`, `FILL_TRANSFER_BYTE_*`, and default length iteration lists.

## Control Flow
There is no executable control flow in the header. Consumers build arrays of `struct spi_test`, optionally set callbacks, and pass them to the declared runner functions. The runner is expected to translate dummy `RX()`/`TX()` markers into actual test buffers, fill TX buffers according to `fill_option`, apply length/alignment iterations, execute SPI messages, and compare results with `expected_return` and protected-buffer patterns.

## State And Persistence
State is per `struct spi_test` instance. The only mutable fields defined here are test descriptors, callback pointers, iteration arrays, fill settings, and `elapsed_time`. No global mutable state or persistent storage is defined.

## Dependencies And Integration Points
The header depends on `linux/spi/spi.h` and therefore on SPI core message and transfer types. It is an integration point between SPI test implementations and any SPI device/controller under test.

## Risks
`RX_START`, `TX_START`, and `SPI_TEST_MAX_SIZE_HALF` use high-bit sentinel values cast to pointers or lengths; consumers must translate them before dereferencing or allocating. Iteration arrays are fixed-size and sentinel-terminated with `-1`, so malformed test definitions can overrun intended iteration logic. Fill modes are numeric macros rather than an enum, so invalid values need validation in consumers. The test maximum size is large enough to exercise DMA but can be expensive.

## Test Signals
Signals are produced by consumers of this header: successful execution of generated SPI messages, expected error returns, no writes into `SPI_TEST_PATTERN_DO_NOT_WRITE` guard regions, no `SPI_TEST_PATTERN_UNWRITTEN` values in expected RX regions, and elapsed-time measurements. Boundary lengths in `ITERATE_LEN` and `ITERATE_MAX_LEN` are designed to expose FIFO, DMA, page, and alignment bugs.
