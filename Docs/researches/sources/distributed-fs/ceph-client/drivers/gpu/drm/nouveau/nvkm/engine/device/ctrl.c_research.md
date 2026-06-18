## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/ctrl.c

### Purpose
`ctrl.c` implements the NVIF device control object, currently focused on power-state and clock-domain query/control methods.

### Important APIs, types, and functions
The exported object class descriptor is `nvkm_control_oclass`. Internal method handlers are `nvkm_control_mthd_pstate_info()`, `nvkm_control_mthd_pstate_attr()`, `nvkm_control_mthd_pstate_user()`, `nvkm_control_mthd()`, and constructor `nvkm_control_new()`.

### Control flow
The method dispatcher handles `NVIF_CONTROL_PSTATE_INFO`, `NVIF_CONTROL_PSTATE_ATTR`, and `NVIF_CONTROL_PSTATE_USER`. Each method unpacks a versioned v0 NVIF structure with `nvif_unpack()`. Pstate info returns count, AC/DC user states, power source, and current pstate, or disabled/unknown values when no clock subdevice exists. Pstate attr validates state/index, finds the indexed clock domain with a monitor name, computes min/max from the requested pstate's base/cstate list or current clock read, fills name/unit/range, and returns the next index. Pstate user applies requested user state to one or both power sources via `nvkm_clk_ustate()`.

### State and persistence behavior
Each control object stores a base `nvkm_object` and `struct nvkm_device *`. It does not cache pstate data; all state is read from or written to `device->clk`. User pstate changes persist in the clock subdevice's `ustate_ac`/`ustate_dc` behavior.

### Dependencies
It depends on `ctrl.h`, client logging, clock subdevice types and helpers, NVIF control ABI headers, ioctl logging, and `nvif_unpack()`.

### Integration points
`nvkm_control_oclass` exposes `NVIF_CLASS_CONTROL` to NVIF clients. Device/user object creation can instantiate this control object so userspace can query and set performance states.

### Risks
Versioned ABI unpacking must stay strict. The pstate attr loop assumes valid clock domain and pstate lists after validation; clock state mutations elsewhere could race if not externally serialized by higher-level ioctl/device locking. Applying user state to both power sources accumulates return codes with bitwise OR, so callers receive a combined error.

### Test signals
NVIF control ioctl tests for pstate info/attr/user, no-clock-device behavior, invalid state/index rejection, current-state clock reads, AC/DC user-state changes, and ABI size/version mismatch tests are relevant.
