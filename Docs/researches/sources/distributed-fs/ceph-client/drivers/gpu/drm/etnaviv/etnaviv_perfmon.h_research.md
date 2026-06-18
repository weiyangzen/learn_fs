## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_perfmon.h

### Purpose
`etnaviv_perfmon.h` declares the perfmon request structure and public perfmon query/validation/processing APIs.

### Important APIs, Types, And Functions
`struct etnaviv_perfmon_request` stores PMR flags, domain, signal, userspace sequence value, mapped BO pointer, and offset. The header declares `etnaviv_pm_query_dom()`, `etnaviv_pm_query_sig()`, `etnaviv_pm_req_validate()`, and `etnaviv_perfmon_process()`.

### Control Flow
The header does not implement flow. Its structure is filled by submit validation and later consumed by GPU sync-point callbacks.

### State, Persistence, And Dependencies
PMR state persists inside `struct etnaviv_gem_submit` until scheduler free-job cleanup releases the submit. The header depends on DRM UAPI PM domain/signal structures and `struct etnaviv_gpu`.

### Integration Points
Submit code includes this header for PMR validation and storage; GPU code includes it for sync-point sampling; ioctl query handlers use the query APIs to enumerate available counters.

### Risks
`bo_vma` is a raw CPU mapping pointer, so lifetime must remain tied to the target GEM object and submit lifetime. Offsets must be interpreted consistently by validator and processor. Adding fields changes internal ABI between files but not the external UAPI.

### Test Signals
Compile checks across submit/GPU/perfmon files, PMR lifetime under submit cleanup, invalid offset rejection, and query ioctl coverage validate the header contract.
