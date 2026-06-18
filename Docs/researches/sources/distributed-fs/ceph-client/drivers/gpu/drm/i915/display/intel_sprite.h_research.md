# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sprite.h

Purpose: declares the public interface for legacy sprite plane support. Under `I915` it exposes plane construction, source-coordinate validation, CHV rotation validation, and per-platform minimum CDCLK helpers. Outside `I915`, `intel_sprite_plane_create()` is an inline stub returning `NULL`, keeping shared display code buildable when this legacy implementation is absent.

Important APIs: `intel_sprite_plane_create(struct intel_display *, enum pipe, int)` builds one overlay plane for a pipe and sprite index. `intel_plane_check_src_coordinates()` is declared here although implemented elsewhere, so sprite validation can share source coordinate rules. `chv_plane_check_rotation()` enforces a Cherryview hardware limitation. `ivb_plane_min_cdclk()`, `hsw_plane_min_cdclk()`, and `vlv_plane_min_cdclk()` are reusable bandwidth calculators.

Control flow and integration: display plane enumeration calls the create helper when sprite planes exist. Atomic check paths can call the validation helpers through the `intel_plane` function pointers selected in `intel_sprite.c`. The header depends only on forward declarations and `linux/types.h`, minimizing include coupling.

State and persistence: no state is stored here. Its main persistence risk is ABI or compile-time contract drift: callers rely on I915-only declarations and the non-I915 stub behavior. Tests should cover I915 builds with sprite planes and non-I915 builds where the stub path compiles cleanly.

Risks: changing prototypes affects plane initialization and any primary-plane code reusing the CDCLK helpers. The `enum pipe` type differs from the stub argument type (`int pipe`), so cross-build compatibility should be checked if this interface changes.
