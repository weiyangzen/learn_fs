# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_lpc_mec.c

Purpose: Microchip EC EMI access helper for the Chrome EC LPC transport. It provides range detection, byte/long auto-increment read/write through MEC EMI registers, and optional ACPI AML mutex coordination.

Important APIs, types, and functions: exported functions are `cros_ec_lpc_mec_init()`, `cros_ec_lpc_mec_acpi_mutex()`, `cros_ec_lpc_mec_in_range()`, and `cros_ec_lpc_io_bytes_mec()`. Internal helpers lock/unlock either a kernel mutex or AML mutex and program EMI address registers via `cros_ec_lpc_mec_emi_write_address()`.

Control flow: LPC probe initializes the MEC EMI base/end. For each range, `cros_ec_lpc_mec_in_range()` validates whether the requested offset lies wholly inside or outside the MEC window. `cros_ec_lpc_io_bytes_mec()` chooses byte access for misaligned/short operations or long auto-increment for aligned larger operations, locks, writes the EMI address, loops over data B0-B3 ports, adjusts access mode for misaligned tail writes, computes checksum, unlocks, and returns checksum or error.

State and persistence: file-static `mec_emi_base`/`mec_emi_end` define the active window. `aml_mutex` optionally replaces the local `io_mutex`, coordinating with ACPI AML code. No per-device storage, so only one MEC range/mutex is supported.

Dependencies and integration points: raw IO port access, ACPI mutex API, LPC driver wrappers, and definitions from the header. Used by `cros_ec_lpc.c` for memory-map and host-command bytes that fall in the MEC range.

Risks and edge cases: globals make multiple MEC instances unsafe. If unlock via AML mutex fails, the function returns an error after data transfer, which may confuse callers expecting checksum. Range checks warn and reject partial overlaps. Long access cannot be used for misaligned writes because B3 flushes, so mode switching is subtle.

Test signals: aligned and misaligned reads/writes, zero-length operations, boundary and partial-overlap range checks, AML mutex acquisition failures, checksum correctness, and concurrent access with ACPI firmware on Framework MEC systems.
