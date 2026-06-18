# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/plane.h

Purpose: declares Tegra plane and plane-state structures plus common plane helper APIs.

Important APIs/types: `struct tegra_plane` embeds `drm_plane` and stores owning DC, register offset/index, and interconnect paths. `struct tegra_cursor` extends it with cursor BO/dimensions. `struct tegra_plane_state` extends DRM plane state with host1x mappings, per-plane IOVAs, tiling, hardware format/swap, reflection flags, legacy blending/opacity, and bandwidth fields. Public helpers cover prepare/cleanup, state add, format mapping/classification, legacy state setup, and interconnect init.

Control flow and state: these structures are allocated/duplicated by `plane.c` and consumed by DC/hub update paths.

Dependencies/integration: depends on DRM plane types, Tegra BO, host1x mapping, ICC, and DC-specific consumers.

Risks: arrays are fixed at three planes, matching supported framebuffer plane count assumptions. `to_tegra_plane_state(NULL)` returns NULL for convenience, but callers must still guard dereferences.

Test signals: compile coverage and atomic state duplication/destruction under plane updates.
