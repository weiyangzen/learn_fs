# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi.h

Purpose: Defines the UCSI core contract, command encodings, bitfield maps, data structures, quirks, optional helper prototypes/stubs, and connector/UCSI state used by all UCSI core and transport files.

Important APIs/types/functions: `struct ucsi_operations` is the transport interface for version/CCI/message reads and sync/async control plus optional connector/altmode hooks. `struct ucsi` stores global version, device, ops, capabilities, connectors, debugfs, init/resume work, PPM lock, notification mask, flags, completion, and quirks. `struct ucsi_connector` stores per-port Type-C objects, altmode arrays, cached bitmaps, power supply, PDO/RDO data, telemetry, PD objects, USB role switch, and identities. Macros encode UCSI commands and read version-gated fields through `UCSI_CONCAP` and `UCSI_CONSTAT`.

Control flow and state: the header does not execute flow, but it defines state ownership and invariants used by `ucsi.c`: one `ucsi` owns an array of connectors; connector cached bitmaps represent the last command responses; ops serialize PPM I/O; optional helper functions compile to stubs when dependencies are disabled.

Persistence behavior: none directly. Structures define in-memory state only.

Dependencies/integration points: includes Linux bitmap, completion, device, power_supply, Type-C, USB PD, USB role, and unaligned helpers. Optional sections integrate with `CONFIG_POWER_SUPPLY`, `CONFIG_TYPEC_DP_ALTMODE`, `CONFIG_TYPEC_TBT_ALTMODE`, and `CONFIG_DEBUG_FS`.

Risks: command and field encodings are protocol-critical; errors affect every transport. `ucsi_bitfield_read` guards minimum version but does not model removed fields. `UCSI_MAX_DATA_LENGTH` changes payload size across UCSI versions, and transports must support the core's requested length. Quirk flags alter PDO timing, partner PDO reads, and USB4/USB interpretation.

Test signals: compile matrix with optional subsystems disabled/enabled, UCSI version 1.0/1.2/2.0/2.1/3.0 behavior, command encoding tests through debugfs or trace, and connector status parsing for orientation, USB4 flags, power readings, PD revision, BC status, and change bits.
