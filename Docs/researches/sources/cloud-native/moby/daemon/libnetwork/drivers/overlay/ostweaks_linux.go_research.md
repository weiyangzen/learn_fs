# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/ostweaks_linux.go

Purpose: Applies Linux neighbor table sysctl tuning for overlay scalability.

Important APIs and functions: `ovConfig` defines `net.ipv4.neigh.default.gc_thresh1/2/3` target values with `checkHigher`. `checkHigher` returns true when the current value is lower than the target. `applyOStweaks` delegates to `kernel.ApplyOSTweaks`.

Control flow: called once by overlay driver configuration. Values are only raised when lower.

State and persistence: mutates host/kernel sysctl state through `kernel.ApplyOSTweaks`; no datastore.

Dependencies and integration points: used by `driver.configure` in `overlay.go`.

Risks: parse errors in `checkHigher` are ignored as zero, which may treat invalid values as needing update. Sysctl writes may fail in restricted environments.

Test signals: no direct tests in this subset.
