# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hub.h

Purpose: declares display hub and shared-plane data structures plus public hub integration functions.

Important APIs/types: `struct tegra_windowgroup` tracks per-window-group reset, parent host1x client, usecount, and lock. `struct tegra_shared_plane` embeds `tegra_plane`. `struct tegra_display_hub` stores DRM private object, host1x client, clocks, resets, head clocks, SoC capabilities, and window groups. `struct tegra_display_hub_state` stores atomic-selected DC/clock/rate. Public functions cover prepare/cleanup, shared-plane creation, atomic check, and atomic commit.

Control flow and state: hub state is part of DRM atomic private object machinery, allowing clock-parent/rate decisions to be staged before commit.

Dependencies/integration: depends on DRM plane/private state concepts, host1x client types, reset/clock types, and `plane.h`.

Risks: window-group usecount correctness depends on paired prepare/cleanup and mutex protection. `supports_dsc` controls optional clock acquisition.

Test signals: build coverage, atomic hub state duplication/destruction tests, and prepare/cleanup balance checks.
