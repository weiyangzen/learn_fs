
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qmc.c

## Purpose
Implements the Freescale CPM1/QE QMC multichannel controller as a platform driver and as an exported channel API for child protocol drivers. It binds to `fsl,cpm1-scc-qmc` and `fsl,qe-ucc-qmc`, configures SCC/UCC QMC mode, programs TSA time-slot tables, owns shared DPRAM/MURAM parameter areas, and exposes QMC channel operations for HDLC and transparent modes.

## Important APIs, Types, and Functions
- Internal state centers on `struct qmc` and `struct qmc_chan`. `struct qmc` owns SCC/UCC registers, SCC PRAM, DPRAM, DMA-coherent BD and interrupt tables, TSA serial handle, channel list, and channel lookup array. `struct qmc_chan` owns mode, time-slot masks, Tx/Rx BD rings, completion descriptors, counters, and stop/halt flags.
- Exported channel API: `qmc_chan_get_info()`, `qmc_chan_get_ts_info()`, `qmc_chan_set_ts_info()`, `qmc_chan_set_param()`, `qmc_chan_write_submit()`, `qmc_chan_read_submit()`, `qmc_chan_stop()`, `qmc_chan_start()`, `qmc_chan_reset()`, phandle/child lookup helpers, and devres variants.
- Hardware setup functions include `qmc_init_resources()`, `qmc_qe_soft_qmc_init()`, `qmc_init_tsa()`, `qmc_setup_chan()`, `qmc_setup_ints()`, `qmc_init_xcc()`, and `qmc_finalize_chans()`.
- Interrupt path is `qmc_irq_handler()` -> `qmc_irq_gint()` -> `qmc_chan_write_done()` / `qmc_chan_read_done()` plus underrun/busy handling.

## Control Flow
Probe allocates `struct qmc`, gets the TSA serial phandle, maps CPM1 or QE resources, optionally loads Soft-QMC firmware for QE, parses channel child nodes, allocates DMA-coherent BD and interrupt rings, initializes QMC global parameters and TSA tables, initializes all channel parameter areas and BDs, initializes SCC/UCC, requests IRQ, enables global interrupts, force-stops channels, enables SCC/UCC Tx/Rx, stores drvdata, then populates child devices.

Per-transfer control flow is ring-based. Submitters write DMA address/length and callbacks into the next BD, set ownership bits with a write barrier, optionally poll the Tx channel, and advance the free pointer. Interrupt completion walks done pointers while hardware ownership is clear, clears the software-owned `UB` marker, drops the lock around callbacks, then advances. Rx busy interrupts may reset receive state immediately if BDs are pending or mark the channel halted for restart on the next submit.

Start/stop is serialized by `ts_lock`, with direction-specific `rx_lock`/`tx_lock`. Stop sends CPM/QE channel commands, marks stopped, and disables TSA entries once both directions are stopped for shared 64-entry tables. Start enables TSA entries, sets transparent sync if needed, reloads receiver state or enables transmitter state, and rolls back the other direction on partial failure.

## State and Persistence
Persistent runtime state is in devm-managed `qmc`, channel objects, coherent BD/int tables, SCC PRAM, DPRAM, and hardware registers. Channel time-slot masks are mutable only while affected directions are stopped. `nb_tx_underrun`, `nb_rx_busy`, `rx_pending`, `is_rx_halted`, and stop flags survive until reset/remove. No file persistence exists. Firmware state may persist in QE firmware subsystem and is checked before upload.

## Dependencies and Integration Points
Depends on CPM/QE support, `soc/fsl/qe/qmc.h`, `ucc_slow.h`, QE commands/MURAM helpers, CPM commands, firmware loader, DT child nodes, and local `tsa.h`. QMC is tightly integrated with TSA: time-slot capacity comes from `tsa_serial_get_info()`, SCC/UCC connection comes through `tsa_serial_connect()`, and QE UCC numbers come from `tsa_serial_get_num()`. Child drivers bind below QMC via `devm_of_platform_populate()` and use exported QMC channel handles.

## Risks
- Register programming is endian-sensitive and hardware-specific; wrong compatible data or resource layout can corrupt PRAM/DPRAM.
- `qmc_remove()` and some error labels call `qmc_setbits32(..., 0)` when disabling Tx/Rx, which is a no-op; intended clearing would need `qmc_clrbits32()`. This is a behavioral risk if remove/error cleanup depends on disabling the controller.
- Callbacks run from IRQ context after locks are dropped, so consumers must not sleep and must tolerate reentrancy.
- `qmc_chan_set_ts_info()` correctly requires stopped directions for changed masks; callers that race start/stop paths must respect the exported API locking contract.
- Firmware loading validates size/header but still depends on platform-supplied firmware identity and QE global firmware state.
- BD ring capacity is fixed at 8 Tx and 8 Rx descriptors per channel; high-latency consumers can hit `-EBUSY`.

## Test Signals
Useful tests are DT probe with both CPM1 and QE compatibles, phandle lookup deferral, invalid channel id/mode/timeslot masks, 32+32 versus 64 shared TSA tables, HDLC parameter validation, Tx/Rx ring wrap and callback ordering, stop/start rollback paths, Soft-QMC firmware load failure paths, IRQ queue overflow and Rx busy recovery, and remove/error cleanup confirming controller disable behavior.
