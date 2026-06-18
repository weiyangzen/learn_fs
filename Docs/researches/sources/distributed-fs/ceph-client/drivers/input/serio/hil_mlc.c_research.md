<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/hil_mlc.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/hil_mlc.c

## Purpose
`hil_mlc.c` is the generic HP-HIL Master Link Controller state-machine layer. It sits between an access-method driver such as `hp_sdc_mlc.c` and HIL protocol device drivers by discovering devices on an HIL loop, polling the loop, maintaining discovered-device metadata, and exposing each discovered slot as a virtual `SERIO_HIL_MLC` serio port.

## Important APIs, types, and functions
- The public API is `hil_mlc_register()` and `hil_mlc_unregister()`, exported for hardware-specific MLC backends.
- Runtime state is stored in the `hil_mlc` object supplied by the backend: callback methods `in`, `out`, and `cts`; locks and semaphores; current state-engine index; input/output packets; discovered-device tables `di`, `di_map`, `serio_map`; and the virtual serio ports.
- `hil_mlc_se[]` is the central state-machine table. It describes controller reset/test, device hard reset, interface clear, auto-configure, discovery, metadata collection, polling, and reprobe behavior through `HILSE_FUNC`, `HILSE_OUT`, `HILSE_IN`, `HILSE_EXPECT*`, and `HILSE_CTS` nodes.
- Helpers such as `hilse_take_idd()`, `hilse_take_rsc()`, `hilse_take_exd()`, and `hilse_take_rnm()` parse HIL device description packets into `di_scratch`.
- `hilse_match()` matches the discovered scratch record to an unused remembered device slot or allocates a new slot, updates reverse maps, and triggers `serio_rescan()`.
- `hil_mlc_send_polls()` converts HIL poll response packets into byte streams delivered through the bound serio driver interrupt callback.
- `hil_mlc_serio_write()` emulates cached IDD/RSC/EXD/RNM responses for upper-layer HIL drivers and rejects unsupported non-command writes.

## Control flow
Module init sets up a one-second kicker timer and enables a global tasklet. A hardware backend calls `hil_mlc_register()`, which initializes synchronization primitives and discovery state, allocates `HIL_MLC_DEVMEM` virtual serio ports, adds the MLC to the global list, and schedules the tasklet.

The tasklet walks every registered MLC and repeatedly executes `hilse_donode()` until the current node requests a break. Output nodes prepare expected input, acquire the output semaphore, call the backend `out()` callback, and then wait for the backend ISR to release input state. Input/expect nodes call the backend `in()` callback and transition according to success, protocol mismatch, or timeout. The timer periodically sets `hil_mlcs_probe` and schedules the tasklet so the loop is re-polled and hung transactions are advanced.

During normal operation the state machine reaches `HILSEN_OPERATE`, sends `HIL_CMD_POL`, forwards poll data to the matching virtual serio port, and returns to operate unless the global probe flag asks it to re-enter discovery. Unregister removes the MLC from the list, unregisters all virtual serio ports, and schedules the tasklet to drain any pending state.

## State and persistence
The file maintains global runtime state only: the registered MLC list, tasklet, kicker timer, probe flag, and stop flag. Each MLC keeps the persistent-in-RAM mapping between physical HIL device order and remembered device information slots so devices can be rescanned without losing cached identity data. No state is written to disk or firmware.

Synchronization is split across the global `hil_mlcs_lock`, per-MLC `lock`, semaphores for input/output/clear-to-send, and tasklet/timer scheduling. Device discovery data survives while the MLC is registered but is lost when the backend unregisters.

## Dependencies and integration points
This layer depends on `<linux/hil_mlc.h>` data structures, HIL packet constants from the HIL subsystem, the serio bus, timer/tasklet infrastructure, semaphores, and a backend that implements the physical MLC callbacks and schedules `mlc->tasklet` from its ISR. `hp_sdc_mlc.c` is the paired backend in this source set.

## Risks
- The state engine is table-driven and index-sensitive; changing node order or transition constants can silently alter discovery and recovery behavior.
- `hil_mlc_send_polls()` calls the bound serio driver's `interrupt` method directly after looking at `serio->drv`; lifetime and binding state must remain stable under serio core expectations.
- Backend callbacks must obey the semaphore protocol. Missed `up()` calls or stale `istarted`/`ostarted` state can stall the global tasklet.
- `hil_mlc_serio_write()` returns `-EIO` for unsupported command sequences and only emulates selected metadata commands, so upper drivers expecting more HIL command coverage may fail.
- The global `hil_mlc_stop` disables future timer rescheduling after an output error, affecting every registered MLC.

## Test signals
- Build with HIL/HP SDC configurations to catch API drift in `hil_mlc`, `serio`, timer, and tasklet interfaces.
- Exercise backend registration/unregistration and verify every virtual serio port is registered, rescanned on new device identity, and unregistered cleanly.
- HIL hardware or simulator tests should cover empty loop, multiple devices, IDD-only devices, RSC/EXD/RNM-capable devices, timeout recovery, repoll, and forced reprobe.
- Inject backend `in()` timeout and `out()` failure paths to verify tasklet rescheduling and stop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/hil_mlc.c -->
