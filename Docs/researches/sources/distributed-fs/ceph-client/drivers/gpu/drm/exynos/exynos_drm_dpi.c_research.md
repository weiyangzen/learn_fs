# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_dpi.c

Purpose: this file implements the parallel DPI/RGB output glue for Exynos DRM. It creates a simple encoder and connector for panels connected to the FIMD RGB port or using display timings embedded under the FIMD node.

Important structures and APIs: `struct exynos_dpi` contains a `drm_encoder`, `drm_connector`, optional `drm_panel`, optional `videomode`, and the panel DT node. `exynos_dpi_probe()` parses DT and returns the embedded encoder pointer. `exynos_dpi_bind()` initializes a TMDS-style simple encoder, sets possible CRTCs to `EXYNOS_DISPLAY_TYPE_LCD`, and creates a DPI connector. `exynos_dpi_remove()` disables the panel path.

Control flow: probe allocates context, calls `exynos_dpi_parse_dt()`, and resolves a remote panel through `of_drm_find_panel()` if an RGB remote node exists. Bind runs later from FIMD component bind and registers the encoder/connector. Connector detection always reports connected. `get_modes` prefers local `display-timings`; if absent, it delegates to the panel. Encoder enable prepares and enables the panel; disable disables and unprepares it.

State and persistence: state is devm-managed context plus DRM connector/encoder objects. There is no retained userspace state. Panel power state is driven by encoder enable/disable.

Dependencies and integration points: this file uses OF graph, DRM panel, simple KMS helper, atomic connector helpers, and `exynos_drm_set_possible_crtcs()`. It is attached by FIMD when `ctx->encoder` is present.

Risks: detection is unconditional, so broken panel DT or missing physical connection is not reflected through connector status. `exynos_dpi_parse_dt()` returns `NULL` from probe on `-EINVAL`, meaning "no DPI" rather than a hard error. Panel lookup can defer via `ERR_PTR`.

Test signals: DT cases with display timings only, remote panel only, missing panel, deferred panel probe, connector mode enumeration, and panel prepare/enable sequencing during modeset and shutdown.
