# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_backend.c

## Purpose
`sun4i_backend.c` implements the original Allwinner Display Engine backend as a `sunxi_engine`. It programs layer composition registers, validates atomic plane constraints, coordinates optional frontend scaler/CSC use, commits shadowed register updates, handles backend-to-TCON mux quirks, and manages clocks/resets through component binding.

## Important APIs, Types, and Functions
- `struct sun4i_backend_quirks`: per-compatible flags for output muxing and lowest-plane alpha support.
- Layer update APIs exported through `sun4i_backend.h`: enable, coordinate, format, buffer, frontend, zpos, and cleanup.
- Atomic engine ops: `sun4i_backend_atomic_begin`, `sun4i_backend_atomic_check`, `sun4i_backend_commit`, `sun4i_backend_mode_set`, color correction, and vblank frontend teardown.
- Binding helpers: `sun4i_backend_of_get_id`, `sun4i_backend_find_frontend`, `sun4i_backend_bind/unbind`.

## Control Flow, State, and Persistence
Component bind allocates backend state, sets DMA device once, identifies backend ID from OF graph, optionally links a frontend, maps registers, deasserts reset, enables bus/mod/ram clocks, initializes optional SAT resources, creates a regmap, adds the engine to `sun4i_drv.engine_list`, clears backend registers, disables autoload, enables the backend, and selects output mux by ID on affected SoCs. Atomic check sorts planes by normalized zpos, decides which single plane can use frontend, enforces one YUV backend plane, enforces hardware alpha limits, and assigns pipe numbers. Plane updates write sizes, coordinates, formats, alpha, YUV coefficients, DMA addresses, line widths, and pipe/priority.

Persistent state includes clock/reset handles, frontend pointer and teardown flag protected by spinlock, quirks, and engine list membership. Hardware state persists in backend registers until overwritten or reset.

## Dependencies and Integration Points
The file depends on DRM atomic/plane helpers, DMA framebuffer helpers, regmap, reset, clocks, component framework, OF graph, `sun4i_layer`, `sun4i_frontend`, and `sunxi_engine`. It is bound by the sun4i master driver and feeds TCONs.

## Risks and Test Signals
Risks include complex alpha/pipe constraints, only one frontend/YUV plane, packed-only YUV backend support, 32-bit DMA assumptions, frontend teardown timing at vblank, and output mux assumptions. Tests should cover multi-plane zpos/alpha combinations, scaling via frontend, unsupported scaling without frontend, YUV packed sequences, backend mux IDs, SAT init on A33, error unwinding, and vblank teardown artifact avoidance.
