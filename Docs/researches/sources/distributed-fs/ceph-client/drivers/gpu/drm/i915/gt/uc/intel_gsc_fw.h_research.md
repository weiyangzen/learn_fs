# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_fw.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_gsc_fw.h

### Purpose
`intel_gsc_fw.h` declares the GSC firmware management API used by the GSC uC coordinator and status paths.

### Important APIs, Types, And Functions
It declares binary-info parsing, upload, init-done, proxy-init-done, and proxy status functions for `struct intel_gsc_uc`, `struct intel_uc_fw`, and `struct intel_uncore`.

### Control Flow
There is no executable flow in the header.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
It owns no state and depends on forward declarations plus Linux types. It integrates `intel_gsc_uc.c`, debugfs, and proxy readiness checks with the firmware implementation. Risks are declaration drift or exposing status helpers without the necessary runtime-PM context. Compile coverage and GSC load/proxy tests are the signals.
