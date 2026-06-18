<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_th.h -->
# sources/distributed-fs/ceph-client/include/linux/intel_th.h

Purpose: Defines Intel Trace Hub MSU buffer provider interface.

Important APIs/types/functions: Buffer capability enum values identify buffer direction/features. `struct msu_buffer` describes name, owner, ops/callbacks, allocation/free/activate/deactivate behavior, window locking, and scatterlist backing. APIs register/unregister MSU buffer providers and unlock MSC windows. `module_intel_th_msu_buffer()` creates module init/exit for a provider.

Control flow: Buffer modules register an `msu_buffer`; Trace Hub core calls provider callbacks to allocate and manage trace capture windows.

State/persistence: Buffer provider registration persists until module exit; allocated scatter-gather windows persist while trace capture is active.

Dependencies/integration: Depends on scatterlist, device model, module lifecycle, and Intel TH/MSC code.

Risks: Window lock/unlock and SG ownership must match DMA/capture lifetime or traces corrupt.

Test signals: Module register/unregister, trace capture allocation/free, window unlock, and active capture teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_th.h -->
