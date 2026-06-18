# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_debug.h

Purpose: Declares the optional DP debugfs initialization API and provides a stub when debugfs is disabled.

Important APIs/types: `msm_dp_debug_init()` accepts device, panel, link, connector, debugfs root, and eDP flag. Under `CONFIG_DEBUG_FS` it is implemented by `dp_debug.c`; otherwise the static inline stub returns `-EINVAL`.

Control flow/state: DP display setup calls this during connector/debugfs initialization. The eDP flag controls whether compliance test files are created.

Dependencies/integration: Includes DP panel and link headers and forward declarations through those includes. Uses DRM connector and debugfs types in the function signature.

Risks and test signals: Callers must tolerate `-EINVAL` when debugfs is disabled. Build-test both debugfs-enabled and disabled configurations and confirm no required runtime path depends on debugfs success.
