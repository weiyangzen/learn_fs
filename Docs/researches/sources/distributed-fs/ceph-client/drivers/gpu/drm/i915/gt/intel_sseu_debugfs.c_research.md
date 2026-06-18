# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sseu_debugfs.c

## Purpose
`intel_sseu_debugfs.c` exposes available and currently enabled SSEU topology through GT debugfs files.

## Important APIs, Types, And Functions
Public functions are `intel_sseu_status()` and `intel_sseu_debugfs_register()`. Internal status readers are `cherryview_sseu_device_status()`, `bdw_sseu_device_status()`, `gen9_sseu_device_status()`, and `gen11_sseu_device_status()`. `i915_print_sseu_info()` formats counts and powergating fields.

## Control Flow
`intel_sseu_status()` prints static device info from `gt->info.sseu`, allocates a temporary `sseu_dev_info`, initializes its dimensions, enters runtime PM, dispatches the platform-specific ACK register reader, prints enabled status, and frees the temporary object. Debugfs show functions wrap this status and topology printing. Registration adds `sseu_status` and `sseu_topology` files.

## State, Persistence, And Dependencies
The file stores no persistent state. It depends on runtime PM, debugfs file registration, uncore register reads, SSEU topology helpers, sequence files, and platform register definitions.

## Integration Points
GT debugfs registration calls `intel_sseu_debugfs_register()`. The top-level debugfs path can call `intel_sseu_status()` directly, so the GT is passed explicitly through `seq_file` private data or function arguments.

## Risks
Status reflects live powergating ACK registers and can differ from available topology. Register layouts differ by platform, and Gen11 has a FIXME around valid subslice masks. Allocation failure returns `-ENOMEM`; pre-Gen8 returns `-ENODEV`.

## Test Signals
Debugfs reads on CHV/BDW/Gen9/Gen11+, runtime PM coverage, comparison against query topology, and output parsing for enabled versus available counts are useful tests.
