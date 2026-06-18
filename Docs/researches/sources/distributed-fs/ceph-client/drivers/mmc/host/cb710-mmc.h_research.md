# sources/distributed-fs/ceph-client/drivers/mmc/host/cb710-mmc.h

## Purpose
`cb710-mmc.h` is the private header for the ENE CB710 MMC/SD subdriver. It defines the per-reader state, slot/MMC conversion helpers, and the inferred CB710 MMC register map used by `cb710-mmc.c`.

## Important APIs, Types, and Functions
`struct cb710_mmc_reader` contains `finish_req_bh_work`, the active `mmc_request`, `irq_lock`, and `last_power_mode`. `cb710_slot_to_mmc` gets the `mmc_host` from a CB710 platform slot, and `cb710_mmc_to_slot` walks from `mmc_host` device to platform device and then to `struct cb710_slot`.

The rest of the header defines port offsets and bit masks for data, config, IRQ enable, status, command type, command argument, transfer size, and response registers. Command definitions include response type, response-present, MMC command type, read-data bit, opcode shift/mask, app-command bit, and busy-response bit.

## Control Flow and State
The header has no active control flow. Its conversion helpers are inline and are used throughout request, IRQ, IOS, and probe paths to bridge Linux MMC core objects and the CB710 core slot abstraction. Register constants guide all hardware access in `cb710-mmc.c`.

## State and Persistence Behavior
No durable persistence is defined. The header defines volatile runtime state and hardware register state only. `last_power_mode` lets the implementation avoid repeating power sequences for unchanged IOS power mode; `irq_lock` serializes IRQ enable updates.

## Dependencies and Integration Points
The header depends on `<linux/cb710.h>` for slot/chip types and on workqueues for the finish work. It is consumed by the platform driver implementation and is coupled to the CB710 core’s platform-device model. The register definitions are marked as potentially inaccurate by comments, reflecting reverse-engineered hardware behavior.

## Risks and Test Signals
Risks include incorrect register definitions, bit masks that overlap unintentionally, helper assumptions about platform driver data, and changing CB710 core types. Test signals include successful compile with CB710 core, correct slot/MMC pointer round-trips, IRQ enable/status bit behavior on card changes, response register decoding, and no regressions in suspend/resume paths that rely on these constants.
