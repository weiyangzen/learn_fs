# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_lpc_mec.h

Purpose: private interface and register definitions for Microchip EC EMI support used by the Chrome EC LPC module.

Important APIs, types, and functions: defines `enum cros_ec_lpc_mec_emi_access_mode` for byte/word/long/long-auto-increment access, `enum cros_ec_lpc_mec_io_type` for read/write, register offset macros relative to an EMI base, and declarations for MEC init, ACPI mutex setup, range check, and byte IO.

Control flow: `cros_ec_lpc.c` includes this header, initializes base/end, checks whether offsets are MEC-mapped, and delegates read/write bytes to `cros_ec_lpc_io_bytes_mec()` when appropriate.

State and persistence: no storage in the header. Declared functions operate on static state in `cros_ec_lpc_mec.c`.

Dependencies and integration points: includes `linux/acpi.h`; intended only for Chrome EC LPC transport internals.

Risks and edge cases: register macros assume an eight-port EMI window. Long auto-increment semantics are hardware-specific and callers must preserve alignment/range requirements. Since implementation state is global, the API does not support independent per-device contexts.

Test signals: compile integration with the composite `cros_ec_lpcs` module and runtime checks through the MEC helper implementation.
