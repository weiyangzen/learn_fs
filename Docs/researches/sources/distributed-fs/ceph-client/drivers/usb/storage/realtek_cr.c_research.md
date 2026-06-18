<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/realtek_cr.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/realtek_cr.c

## Purpose

`realtek_cr.c` supports Realtek RTS51xx USB card readers. It probes reader status through vendor SCSI commands, configures auto-delink behavior, and optionally wraps the normal protocol handler with selective-suspend-aware behavior.

## Important APIs, Types, and Functions

`struct rts51x_status` stores per-LUN reader status returned by command `F0 09`; `struct rts51x_chip` stores IDs, LUN count, status array, flags, runtime PM state, and the backed-up protocol handler. Low-level helpers include `rts51x_bulk_transport()`, `rts51x_read_mem()`, `rts51x_write_mem()`, `rts51x_read_status()`, `rts51x_check_status()`, `do_config_autodelink()`, and `config_autodelink_after_power_on()`. PM paths use `realtek_cr_suspend()`, `realtek_cr_resume()`, and, under `CONFIG_REALTEK_AUTOPM`, `rts51x_invoke_transport()`.

## Control Flow

Initialization allocates `rts51x_chip`, obtains max LUN, allocates one status record per LUN, reads status for each LUN, detects firmware/product combinations that support auto-delink, optionally installs the autosuspend wrapper, and configures auto-delink registers. The vendor transport hand-builds Bulk-Only CBWs with Realtek CDBs and validates CSWs. Runtime suspend/resume serializes against `us->dev_mutex` and writes Realtek internal registers before power-down or after power-on. The optional protocol wrapper prevents low-value polling commands from waking a selectively suspended device and synthesizes TEST_UNIT_READY or ALLOW_MEDIUM_REMOVAL results from cached LUN readiness.

## State and Persistence Behavior

Per-device state lives in `us->extra`. It caches status, flags, power state, ready LUN bits, and timer state. Register writes to addresses such as `0xFE47`, `0xFE77`, `0xFE79`, and `0x48` alter device firmware behavior for auto-delink and oscillator/power handling. No host file persistence exists.

## Dependencies and Integration Points

The file depends on usb-storage Bulk-Only structures, SCSI command APIs, runtime PM, timers, unusual Realtek IDs, and usb-storage lifecycle callbacks. It integrates with generic protocol handling by backing up and optionally replacing `us->proto_handler`.

## Risks and Test Signals

Risk areas include handwritten CBW/CSW handling, firmware-specific register magic, status-length assumptions, race-prone runtime PM transitions, and compile-time behavior differences with `CONFIG_REALTEK_AUTOPM`. In `config_autodelink_before_power_down()`, one path reads `0xFE47` but writes the modified value to `0xFE77`, which is suspicious. Tests should cover multiple LUNs, suspend/resume with in-flight commands, auto-delink on supported and unsupported firmware, status short reads, CSW signature/tag failures, and behavior with autosuspend disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/realtek_cr.c -->
