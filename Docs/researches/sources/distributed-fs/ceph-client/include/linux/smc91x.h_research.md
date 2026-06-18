<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smc91x.h -->
# sources/distributed-fs/ceph-client/include/linux/smc91x.h

## Purpose
`smc91x.h` defines platform data for the SMC91x Ethernet driver family. It tells the driver which bus access widths and platform quirks are supported and how the device LEDs should be configured.

## Important APIs, Types, and Functions
The file contains flags for access width and behavior: `SMC91X_USE_8BIT`, `SMC91X_USE_16BIT`, `SMC91X_USE_32BIT`, `SMC91X_NOWAIT`, `SMC91X_IO_SHIFT_*`, `SMC91X_IO_SHIFT(x)`, and `SMC91X_USE_DMA`. LED mode constants include `RPC_LED_100_10`, `RPC_LED_RES`, `RPC_LED_10`, `RPC_LED_FD`, `RPC_LED_TX_RX`, `RPC_LED_100`, `RPC_LED_TX`, and `RPC_LED_RX`. `struct smc91x_platdata` carries `flags`, LED A/B modes, and the `pxa_u16_align4` quirk for buggy PXA 16-bit writes at specific alignments.

## Control Flow
There is no executable control flow. Board code supplies `smc91x_platdata` to the Ethernet driver. During probe, the driver interprets flags to choose accessors, I/O address shift, DMA use, and LED configuration. The comments warn that 32-bit support alone is invalid because the driver requires at least 8-bit or 16-bit access.

## State and Persistence Behavior
The only C state is static platform data passed at device registration. Hardware state such as LED mode and bus access behavior is configured by the driver based on this data and persists until device reset or reconfiguration.

## Dependencies and Integration Points
The header depends only on basic C types and `bool`. It integrates with platform-device board files and the SMC91x network driver, especially on embedded systems with nonstandard bus widths or PXA alignment quirks.

## Risks and Test Signals
Risks are invalid access-width combinations, wrong I/O shift, enabling DMA on unsupported boards, and missing the PXA alignment workaround. Test signals include successful probe, register read/write sanity checks at configured widths, packet TX/RX, LED behavior, DMA stress when enabled, and platform-specific alignment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smc91x.h -->
