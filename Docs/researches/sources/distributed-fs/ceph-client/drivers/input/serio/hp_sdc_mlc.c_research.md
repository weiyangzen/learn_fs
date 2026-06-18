<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/hp_sdc_mlc.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/hp_sdc_mlc.c

## Purpose
`hp_sdc_mlc.c` is the hardware-access backend that connects the generic HIL MLC state machine in `hil_mlc.c` to HP System Device Controller raw HIL services from `hp_sdc.c`. It translates SDC HIL interrupts into HIL packets and translates MLC output/CTS requests into SDC transactions.

## Important APIs, types, and functions
- The module owns one static `hil_mlc hp_sdc_mlc`.
- `struct hp_sdc_mlc_priv_s` stores emulated test mode, a reusable `hp_sdc_transaction`, transaction sequence storage, and state for pairing SDC 5X status bytes with data bytes.
- `hp_sdc_mlc_isr()` is registered through `hp_sdc_request_hil_irq()` and fills `mlc->ipacket[]`, handles SDC HIL errors, releases `mlc->isem`, and schedules the MLC tasklet when a match, record termination, or error occurs.
- `hp_sdc_mlc_in()` implements the MLC input callback, returning success, timeout, or still-waiting state based on `isem`, timeout values, and emulated controller-test mode.
- `hp_sdc_mlc_cts()` implements clear-to-send by reading `HP_SDC_CMD_READ_USE` and checking `HP_SDC_USE_LOOP` through a semaphore-backed SDC transaction.
- `hp_sdc_mlc_out()` implements HIL output by building SDC transactions for `HP_SDC_CMD_DO_HIL` data commands or `HP_SDC_CMD_SET_LPC` loop-control commands.

## Control flow
Module init initializes the private reusable transaction and assigns `cts`, `in`, `out`, and `priv` in the static MLC object. It registers the MLC with `hil_mlc_register()`, then requests the raw HIL IRQ hook from `hp_sdc`. If the hook request fails, it unregisters the MLC.

When `hil_mlc` asks to send a packet, `hp_sdc_mlc_out()` takes `osem`, handles test-mode control packets locally when possible, validates unsupported APE/IPF combinations, fills the reusable SDC transaction sequence, and enqueues it. The SDC transaction completion releases `osem` or `csem`, allowing the MLC state machine to advance.

Incoming raw HIL SDC interrupts enter `hp_sdc_mlc_isr()`. Status/data events are packed into HIL packet words, address bits are normalized across related bytes, error statuses are converted into HIL error bits, and the generic MLC tasklet is scheduled once the expected packet or an error/termination condition is reached. Exit releases the HIL IRQ hook and unregisters the MLC.

## State and persistence
All state is runtime-only. The static MLC and private transaction are reused for the single onboard SDC-backed loop. Semaphores in the MLC coordinate input, output, and loop-use polling. `emtestmode` emulates HIL controller test responses instead of sending real SDC HIL data. No persistent settings are saved by this module.

## Dependencies and integration points
This file depends directly on `hil_mlc_register()`/`hil_mlc_unregister()` and the HP SDC exported transaction and HIL hook APIs. It also depends on HIL packet constants and SDC status/error definitions. It is the glue loaded after `hp_sdc` discovers and initializes the controller.

## Risks
- The reusable transaction object must not be enqueued concurrently for two actions; semaphore and state-machine assumptions are critical.
- Several invalid protocol situations use `BUG_ON()`, so unexpected control packets or loop-busy states can crash the kernel rather than returning an error.
- ISR packet assembly depends on SDC-specific 5X status/data ordering and address correction; subtle protocol changes can break discovery.
- `hp_sdc_mlc_in()` uses timeout state prepared by `hil_mlc`; incorrect `instart`/`intimeout` handling can cause false timeouts or hangs.

## Test signals
- Build with HP SDC and HIL MLC enabled to catch exported-symbol and structure drift.
- Exercise module load/unload after `hp_sdc` initialization, including denial of the raw HIL hook.
- Hardware or simulated SDC tests should cover normal HIL data, command status, SDC error statuses, loop reconfiguration notifications, input timeout, controller test mode, and loop-use busy handling.
- Verify `hil_mlc` device discovery works through this backend and that semaphores are released on all SDC completion and error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/hp_sdc_mlc.c -->
