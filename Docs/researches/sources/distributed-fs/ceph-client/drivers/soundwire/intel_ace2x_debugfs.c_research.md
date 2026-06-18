# sources/distributed-fs/ceph-client/drivers/soundwire/intel_ace2x_debugfs.c

## Purpose

`intel_ace2x_debugfs.c` provides debugfs support for Intel ACE2.x SoundWire links. It exposes ACE2.x SHIM, vendor-specific SHIM, optional microphone privacy, and Cadence debug registers, plus writable debugfs knobs for master/slave data mode overrides.

## Important APIs, types, and functions

- `intel_ace2x_debugfs_init()` creates `intel-sdw` under the bus debugfs root.
- `intel_ace2x_debugfs_exit()` removes the debugfs subtree.
- `intel_reg_show()` formats selected SHIM2, PCMSYCH, vendor clock, wake, IOCTL, ACTMCTL, and optional PVCCS registers.
- `intel_set_m_datamode()` and `intel_set_s_datamode()` validate data-mode values, taint the kernel, and modify `bus->params.m_data_mode` or `s_data_mode`.
- `intel_sprintf()` centralizes 16-bit vs 32-bit register reads into the fixed 2-page buffer.

## Control flow

The ACE2.x hardware ops table points debugfs init/exit at this file. During link startup, the auxiliary driver calls `sdw_intel_debugfs_init()`, which dispatches to `intel_ace2x_debugfs_init()`. Users reading `intel-registers` get a snapshot of the selected hardware registers. Users writing data-mode files alter the in-memory bus parameter used by later stream preparation/programming.

## State and persistence behavior

The debugfs directory pointer is stored in `sdw->debugfs`. Register reads do not alter hardware state. Data-mode writes mutate `struct sdw_bus_params` and persist until overwritten, bus reset/reinit, or driver teardown. Because those writes bypass normal configuration, they intentionally call `add_taint(TAINT_USER, LOCKDEP_STILL_OK)`.

## Dependencies and integration points

This file depends on `CONFIG_DEBUG_FS`, Intel register definitions, Cadence debugfs helpers, and `struct sdw_intel`. Its public declarations are conditionally provided by `intel.h`; when debugfs is disabled, inline no-op stubs replace these functions.

## Risks and edge cases

- The register dump uses a fixed two-page buffer; adding more registers without checking remaining space can truncate output.
- Writable data-mode knobs can create configurations not expected by stream code or hardware.
- Debugfs accesses assume link resources and MMIO mappings remain valid for the directory lifetime.
- The number of PCMSYCH registers dumped is based on BSS from PCMSCAP; if hardware reports inconsistent capability, the dump can omit useful registers.

## Test signals

Build with `CONFIG_DEBUG_FS=y` and `n`. On ACE2.x hardware, confirm `intel-sdw/intel-registers` produces SHIM and VS sections, PVCCS appears only when `mic_privacy` is true, data-mode writes reject values above `SDW_PORT_DATA_MODE_STATIC_1`, and debugfs removal during driver unload leaves no stale dentries.
