# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/mxic_nand.c

## Purpose
`mxic_nand.c` is the raw NAND controller driver for the Macronix Multi-I/O interface in raw NAND mode. It exposes a simple `exec_op` implementation backed by controller FIFO transfers, manual chip-select control, ready-pin interrupts, clock and phase setup, and single-chip MTD registration.

## Important APIs, Types, and Functions
`struct mxic_nand_ctlr` owns the three clocks (`ps`, `send`, `send_dly`), completion, register base, raw NAND controller, device pointer, and embedded `nand_chip`. Register definitions cover host configuration, interrupt status/enables, TX/RX FIFOs, slave-select control, linear read/write modes, DMA registers, randomizer registers, GPIO, delay lines, and data strobe.

The important functions are `mxic_nfc_probe()`, `mxic_nfc_remove()`, `mxic_nfc_exec_op()`, `mxic_nfc_setup_interface()`, `mxic_nfc_data_xfer()`, `mxic_nfc_wait_ready()`, `mxic_nfc_hw_init()`, `mxic_nfc_set_freq()`, `mxic_nfc_clk_setup()`, `mxic_nfc_clk_enable()`, `mxic_nfc_clk_disable()`, and `mxic_nfc_isr()`. Controller ops include only `exec_op` and `setup_interface`; ECC is left to the NAND core configuration rather than custom page callbacks in this file.

## Control Flow
Probe allocates the controller, gets all clocks, maps registers, binds the first NAND child as the flash node, initializes the raw NAND controller, fetches the IRQ, performs base hardware initialization, requests the IRQ, scans one NAND chip, registers the MTD, and stores driver data. Hardware init sets the controller for raw NAND type, manual chip-select mode, 8-bit I/O, interrupt status enables, ready-pin interrupt signal enable, zeroes ONFI input count and linear-read config, and disables the host controller.

`mxic_nfc_exec_op()` accepts all operations in check-only mode. For real execution it asserts manual CS, initializes the completion, and iterates each NAND op instruction. Command, address, data-in, and data-out instructions program `SS_CTRL(0)` with command/address/data bus width, dummy cycle, byte-count, and read/write direction fields, then use `mxic_nfc_data_xfer()` to move bytes through TXD/RXD FIFO registers. Wait-ready instructions block on the IRQ completion with a one-second timeout. CS is deasserted after the instruction loop.

Timing setup converts SDR `tRC_min` into a target frequency, caps it at 50 MHz, disables clocks, configures send and delayed-send clock rates, writes a fixed input delay code, sets output phase based on frequency, re-enables clocks, and enables EDO strobe mode when `tRC_min` is below 30 ns.

## State and Persistence Behavior
The driver persists no host-side state. Runtime state is the embedded NAND chip, MMIO register configuration, clock rates/phases, completion object, and IRQ state. `nand_scan()` and `mtd_device_register()` create the kernel-visible MTD device; removal unregisters the MTD, calls `nand_cleanup()`, and disables clocks. There is no custom BBT, OOB layout, suspend/resume, DMA, or multi-chip state in this file.

## Dependencies and Integration Points
The driver integrates with the Linux platform driver model, OF match table (`mxic,multi-itfc-v009-nand-controller`), clock framework, MMIO polling helpers, interrupt completions, raw NAND controller operations, and MTD registration. It includes software Hamming ECC headers but does not install custom ECC callbacks; ECC behavior is expected to be selected by NAND core/device-tree policy.

## Risks
The implementation is intentionally simple but has several hardware assumptions. It uses one embedded `nand_chip` and effectively binds child nodes into a single chip, so multi-chip topologies are not represented. `exec_op` returns success for all check-only operations, so unsupported operation shapes would only fail at execution time if the FIFO sequence cannot handle them. FIFO transfer polling has one-second timeouts per byte group and warns if RX FIFO remains non-empty. Clock setup disables clocks before applying rates and phases; failures in the middle can leave clocks off until cleanup or retry.

## Test Signals
Useful signals include probe with all three clocks present, missing-clock errors, IRQ request failure, read-id/status/reset operations through `exec_op`, data-in/data-out transfers with lengths not divisible by four, ready-pin interrupt completion and timeout behavior, setup-interface frequency capping at 50 MHz, EDO strobe enablement for fast timings, MTD registration failure cleanup, and remove path unregistering and disabling clocks.
