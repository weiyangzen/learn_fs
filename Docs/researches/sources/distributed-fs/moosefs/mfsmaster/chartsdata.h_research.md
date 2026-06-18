# sources/distributed-fs/moosefs/mfsmaster/chartsdata.h

This header exposes initialization and current resource-usage access for mfsmaster chart sampling.

It declares `chartsdata_resusage(uint64_t *mem, uint64_t *syscpu, uint64_t *usrcpu)` and `chartsdata_init(void)`. Startup calls `chartsdata_init`; callers needing cached resource values call `chartsdata_resusage` after initialization.

Chart persistence and cached resource globals are hidden in the implementation. The implementation writes through the common charts subsystem and is registered from `init.h` as the charts module.

Risks are that freshness and initialization state are not expressed in the API. Test signals are compile coverage, a startup path reaching `chartsdata_init`, and expected resource values after refresh.
