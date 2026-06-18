<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/OfflineWaitTimeoutTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/OfflineWaitTimeoutTk.h

**Purpose:** Computes the millisecond timeout a caller should wait for target offline state propagation, parameterized over storage or metadata configuration classes.

**Important APIs/types/functions:** Template class `OfflineWaitTimeoutTk<Cfg>` with static `calculate(Cfg* cfg)`. It requires config methods `getSysUpdateTargetStatesSecs()` and `getSysTargetOfflineTimeoutSecs()`.

**Control flow:** If an explicit target-state update interval is configured, the timeout is `(5 + 3 * updateInterval + offlineTimeout) * 1000`. If the update interval is zero/defaulted, the code assumes update interval equals one third of offline timeout and returns `(5 + 2 * offlineTimeout) * 1000`.

**State and persistence behavior:** Stateless pure calculation. It does not cache config values or mutate configuration.

**Dependencies and integration points:** Used where services wait for management/target state convergence. The five-second constant reflects the `InternodeSyncer` loop interval, so this helper is coupled to that background synchronization cadence.

**Risks:** If `InternodeSyncer` timing or default update interval semantics change, this calculation can become stale. It accepts a raw config pointer and does not guard null. It returns `unsigned int` milliseconds, so very large second values can overflow.

**Test signals:** Unit tests should cover explicit update interval, zero/default interval, boundary values, and overflow-sensitive large config values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/OfflineWaitTimeoutTk.h -->
