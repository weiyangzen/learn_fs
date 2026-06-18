# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_proxy.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_proxy.h

### Purpose
`intel_gsc_proxy.h` declares the software proxy lifecycle, request handling, and IRQ entry points for GSC-to-CSME mediation.

### Important APIs, Types, And Functions
It declares `intel_gsc_proxy_init()`, `intel_gsc_proxy_fini()`, `intel_gsc_proxy_request_handler()`, and `intel_gsc_proxy_irq_handler()` for `struct intel_gsc_uc`.

### Control Flow
The header has no runtime flow.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
It owns no state and depends on Linux types plus a forward declaration. It integrates `intel_gsc_uc.c` work handling and interrupt plumbing with proxy implementation. Risks are limited to prototype drift. Compile and proxy init/IRQ coverage are the test signals.
