<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sdca_ump.h -->
# sources/distributed-fs/ceph-client/include/sound/sdca_ump.h

## Purpose
`sdca_ump.h` declares SDCA UMP mailbox/message helpers. It manages host/device ownership handoff and reading or writing SDCA message payloads through device and function regmaps.

## Important APIs, types, and functions
Ownership helpers are `sdca_ump_get_owner_host()` and `sdca_ump_set_owner_device()`. Data movement helpers are `sdca_ump_read_message()` and `sdca_ump_write_message()`, parameterized by entity, offset selector, length selector, and message offset/length. Timeout helpers are `sdca_ump_cancel_timeout()` and `sdca_ump_schedule_timeout()` for delayed work.

## Control flow
Callers request host ownership of a UMP control, use SDCA offset and length selectors to locate message buffers, move the message bytes through regmap, then return ownership to the device or schedule timeout handling if ownership does not transition promptly.

## State and persistence behavior
The header owns no state. Message ownership is stored in SDCA hardware controls; timeout state lives in caller-provided `delayed_work`. Allocated message buffers returned by read helpers must be lifetime-managed by callers.

## Dependencies and integration points
It integrates parsed SDCA function/entity/control data with regmap-backed mailbox access and ASoC components. It is used by HIDE, FDL, security/privacy, smart mic/amp, and extension-unit message paths.

## Risks and test signals
Risks include ownership races, timeout leaks, incorrect message length validation, buffer allocation/free mismatches, using device versus function regmap incorrectly, and failing to restore device ownership on errors. Test signals include host/device ownership transitions, zero and maximum-length messages, timeout scheduling/cancellation, interrupted transfers, and concurrent UMP users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sdca_ump.h -->
