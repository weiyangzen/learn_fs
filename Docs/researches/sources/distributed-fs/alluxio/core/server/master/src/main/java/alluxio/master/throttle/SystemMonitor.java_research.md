# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/SystemMonitor.java

Purpose: non-thread-safe throttle monitor that samples server/filesystem indicators, maintains a sliding window, computes system status, and logs pressure diagnostics.

Important APIs/types/functions: enums `SystemStatus` and `StatusTransition`; constructor; `run`; `collectIndicators`; `collectServerIndicators`; `collectFileSystemIndicators`; `produceDeltaFilesystemIndicators`; `checkBoundary`; `checkAndBackPressure`; private `PitInfo`.

Control flow: each `run` records snapshot time, samples server indicators, conditionally samples filesystem counters based on current status, evaluates transitions, logs status, then stores PIT info for the next cycle. Thresholds are reinitialized at most every roughly 68 seconds using `System.nanoTime() >> 36`. Status moves IDLE <-> ACTIVE <-> STRESSED <-> OVERLOADED based on low/high PIT and aggregate thresholds; a delayed heartbeat beyond overloaded GC-time threshold forces OVERLOADED.

State and persistence: keeps recent `ServerIndicator` samples, aggregate indicator, current/previous filesystem indicators, delta indicator, threshold indicators, current status, previous PIT info, and heartbeat timing. It registers a `system.status` gauge. No journal persistence.

Dependencies/integration: driven by `DefaultThrottleMaster.ThrottleExecutor`; reads `PropertyKey.MASTER_THROTTLE_*` thresholds and metrics registry values through indicator classes.

Risks: despite monitoring CPU/RPC/direct memory, `checkBoundary` currently compares only heap used, so configured CPU/RPC thresholds do not influence transitions there. Constructor initializes `PitInfo` arguments in an order that appears inconsistent with its constructor names, so pause/time baseline interpretation deserves scrutiny. Not thread-safe; callers should keep one heartbeat thread.

Test signals: cover status escalation/de-escalation across thresholds, delayed heartbeat overload, sliding-window add/reduce, filesystem delta only during consecutive stressed/overloaded samples, threshold refresh, gauge registration, and JVM pause baseline behavior.
