# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_ssi_dbg.c

## Purpose
`fsl_ssi_dbg.c` provides optional debugfs support for the SSI driver. It counts interrupt/status events observed by `fsl_ssi_isr` and exposes them in a `stats` debugfs file per SSI device.

## Important APIs, Types, And Functions
The functions exported to the main driver are `fsl_ssi_dbg_isr`, `fsl_ssi_debugfs_create`, and `fsl_ssi_debugfs_remove`. The internal display callback is `fsl_ssi_stats_show`, wrapped by `DEFINE_SHOW_ATTRIBUTE(fsl_ssi_stats)`. The `SIER_SHOW` macro prints a counter when the corresponding interrupt enable constant exists.

## Control Flow
The SSI IRQ handler calls `fsl_ssi_dbg_isr` with the raw SISR value. The function increments counters in `struct fsl_ssi_dbg.stats` for each set SISR bit. Probe calls `fsl_ssi_debugfs_create`, which creates a directory named after the device and a read-only `stats` file. Remove and probe error paths call `fsl_ssi_debugfs_remove`, which recursively removes the directory. Reading `stats` prints all tracked counters.

## State And Persistence
Counters live inside the parent driver's `struct fsl_ssi_dbg` and persist until device removal. They are not reset by reads, suspend/resume, or stream restarts. The debugfs dentry pointer is stored in the same struct for cleanup.

## Dependencies And Integration Points
The file depends on debugfs, seq_file show helpers, Linux device names, and SISR/SIER constants from `fsl_ssi.h`. It is only compiled when debugfs support is enabled through the header's conditional declarations.

## Risks And Edge Cases
Counter increments are not explicitly locked; they occur in IRQ context and can race with debugfs reads, so values are diagnostic rather than synchronized accounting. The `SIER_SHOW` macro tests compile-time constants, so it does not filter by the runtime SIER register value. Failure to create debugfs entries is not checked, consistent with debugfs being optional.

## Test Signals
With debugfs enabled, run playback/capture and inspect `/sys/kernel/debug/<device>/stats`. Force or observe underrun/overrun/frame events and verify corresponding counters increase. Build with debugfs disabled to ensure main SSI calls compile to no-ops.
