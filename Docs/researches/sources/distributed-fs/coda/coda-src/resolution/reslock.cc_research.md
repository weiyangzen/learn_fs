<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/reslock.cc -->
# sources/distributed-fs/coda/coda-src/resolution/reslock.cc

Purpose: participant RPCs for coordinator-driven volume locking and initial status/log-size fetch during resolution.

Important APIs/control flow: `RS_LockAndFetch` gets connection info, translates VSG volume ID, obtains an exclusive volume lock keyed by the coordinator host, fetches the target vnode ignoring inconsistencies, returns its VV and `ResStatus`, computes a maximum log shipment size when RVM resolution is enabled, initializes timing probes for directories, then releases the volume object while retaining the volume lock. `RS_UnlockVol` validates that the caller owns the volume lock and releases it.

State/persistence: manipulates volume lock state and returns vnode status. Does not mutate object contents except timing probe state.

Dependencies/integration: depends on `conninfo`, volume/vnode locking, VRDB translation, `AllowResolution`, `V_RVMResOn`, `recov_vol_log` size, and timing globals.

Risks/test signals: logsize is estimated as `nentries * 200`, a heuristic rather than exact serialization size. Unlock rejects callers that do not match the stored IP. Test lock acquisition/release, wrong unlocker, missing connection info, disabled RVM resolution, directory timing probe initialization, and errors after volume lock acquisition to ensure locks are released.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/reslock.cc -->
