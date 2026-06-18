# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth-debugfs.h

## Purpose
This header provides the DPAA2 Ethernet debugfs interface contract and no-op stubs when debugfs is disabled.

## Important APIs, Types, and Functions
It defines `struct dpaa2_debugfs` containing a per-interface `struct dentry *dir`. Under `CONFIG_DEBUG_FS`, it declares init/exit and per-interface add/remove functions. Otherwise, it defines inline empty stubs for the same functions.

## Control Flow
The header lets the main driver call debugfs lifecycle hooks unconditionally. Compile-time configuration chooses real implementations or no-ops.

## State and Persistence
State is limited to a dentry pointer stored in the main private structure. There is no persistence.

## Dependencies and Integration Points
It depends on `linux/dcache.h` and forward-declares `struct dpaa2_eth_priv`. It is included by the debugfs implementation and the main DPAA2 driver.

## Risks
The stubbed API hides debugfs absence cleanly, but callers must not assume `priv->dbg.dir` is valid when debugfs is disabled. Any additions to the implementation API must be mirrored in both branches.

## Test Signals
Compile with `CONFIG_DEBUG_FS=y` and `n`, then exercise module init/probe/remove paths in both configurations.
