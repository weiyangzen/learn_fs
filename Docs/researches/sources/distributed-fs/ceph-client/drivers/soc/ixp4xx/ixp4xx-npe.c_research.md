
# sources/distributed-fs/ceph-client/drivers/soc/ixp4xx/ixp4xx-npe.c

## Purpose
Intel IXP4xx Network Processor Engine driver. It discovers/reset-registers up to three NPE coprocessors, exports request/release/running/messaging/firmware-load APIs, and spawns optional DT child devices.

## Important APIs, Types, and Functions
- Global `npe_tab[3]` stores NPE ids, register mappings, syscon regmap, and validity.
- Exported APIs: `npe_names`, `npe_running()`, `npe_request()`, `npe_release()`, `npe_load_firmware()`, `npe_send_message()`, `npe_recv_message()`, and `npe_send_recv_message()`.
- Core internals: command read/write helpers, `npe_debug_instr()`, logical register writers, `npe_reset()`, `npe_start()`, and `npe_stop()`.

## Control Flow
Probe gets the global syscon, iterates three memory resources, checks CPU feature/reset bits for availability, maps each NPE register range, performs a deep reset sequence, marks successful NPEs valid, and populates child devices if using DT. Remove resets mapped NPEs.

Firmware loading requests firmware by name, validates image size/magic/ID/endian, rejects mismatched NPE/device IDs, rejects running NPEs, locates the EOF block, validates instruction/data block ranges against CPU-specific memory sizes, writes each word via execution commands, starts the NPE, and releases firmware. Messaging APIs poll FIFO status to send/receive two-word messages.

## State and Persistence
Driver state is global/static and persists while the module is loaded. Firmware loaded into NPE instruction/data memory and NPE run state persist until reset/reload. Module references are held by `npe_request()` and dropped by `npe_release()`.

## Dependencies and Integration Points
Depends on IXP4xx CPU feature helpers, syscon regmap, platform resources for NPE registers, firmware loader, and consumers from network/crypto/HSS drivers.

## Risks
- Firmware parsing mutates the firmware buffer when byte-swapped; firmware memory is treated as writable.
- Reset/debug instruction path has busy loops/timeouts and deep hardware assumptions.
- `npe_request()` returns global objects with module refs but no per-NPE exclusive ownership; consumers must coordinate.
- Messaging expects exactly two-word protocol messages and can timeout on firmware stalls.

## Test Signals
Probe with absent/present NPE feature bits, reset timeout, firmware bad magic/size/id/EOF/range, swapped firmware, running-NPE `-EBUSY`, message FIFO timeout, request/release module ref behavior, and child population.
