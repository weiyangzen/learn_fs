# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/fw.c

## Purpose
`fw.c` is the firmware container wrapper. It declares firmware and board files for module metadata, provides the 32-bit MMIO memset primitive required by wil6210 hardware, and includes `fw_inc.c`, which contains the parser and loader implementation.

## Important APIs, Types, And Functions
`MODULE_FIRMWARE()` advertises default Sparrow, Sparrow Plus, Talyn, and board-file names to userspace firmware tooling. `wil_memset_toio_32()` writes a repeated 32-bit value to MMIO using `__raw_writel()`, matching the driver's broader rule that device memory access must avoid 64-bit transactions on 64-bit hosts. Including `fw_inc.c` makes the static parser helpers share this translation unit and access `wil_memset_toio_32()`.

## Control Flow
The file has no standalone runtime entry point beyond helper inclusion. Firmware load is initiated elsewhere, primarily `wil_reset()` in `main.c`, which calls `wil_request_firmware()` and `wil_request_board()` implemented by the included `fw_inc.c`.

## State And Persistence
No persistent driver state is owned here. Firmware file names become module metadata. The memset helper mutates target device memory during firmware fill-record handling.

## Dependencies And Integration Points
It depends on Linux firmware APIs, module metadata, CRC support needed by `fw_inc.c`, and local firmware structures from `fw.h`. The wrapper integrates the parser into a translation unit with access to driver MMIO helpers and `wil6210_priv`.

## Risks
The loop in `wil_memset_toio_32()` assumes callers pass aligned sizes validated by `fw_inc.c`. Any new fill-record path must preserve the validation that sizes are at least one dword and dword aligned. Because `fw_inc.c` is included rather than compiled separately, symbol visibility and include order matter.

## Test Signals
Firmware images with fill records should be tested on 64-bit hosts. Build tests should catch include-order regressions. Firmware metadata can be checked with module tools to confirm expected firmware names are exposed.
