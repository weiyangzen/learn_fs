# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/hub.c

Purpose: implements the Tegra186+ display hub, shared window-group planes, display-hub atomic private state, and runtime PM for hub clocks/resets.

Important APIs/functions: `tegra_shared_plane_create()` creates universal DRM planes with Tegra186+ formats/modifiers and zpos. Plane helpers check format/tiling, pin framebuffers, assign window ownership, program scaling/blending/YUV/address registers, and disable windows. `tegra_display_hub_atomic_check()` selects the active display clock with the highest pixel rate; `tegra_display_hub_atomic_commit()` sets hub clock parent/rate and updates fetch-meter/common state. `tegra_display_hub_prepare()/cleanup()` currently enable/disable all window groups with usecounts. Probe wires clocks, reset, window-group resets, child head clocks, runtime PM, host1x client registration, and child population.

Control flow and state: `struct tegra_display_hub` owns a DRM private object, host1x client, clocks, reset, head clocks, SoC info, and window groups. `struct tegra_shared_plane` extends `tegra_plane` with a window-group pointer. Runtime PM enables display/DSC/hub/head clocks and deasserts reset; suspend reverses it.

Dependencies/integration: integrates DRM atomic private objects, Tegra DC register access, common plane helpers, host1x client PM, OF child population, clocks/resets, and framebuffer tiling helpers.

Risks: window groups are globally enabled because finer enable points are missing. Shared-plane ownership can fail with `-EBUSY` if hardware owner differs. Scaling code contains TODO/XXX notes and currently forces 5-tap programming. 64-bit GPU sector-layout address flag is conditional on DMA address width.

Test signals: atomic multi-head commits, shared plane movement between CRTCs, block-linear and sector-layout modifiers, YUV multi-plane scanout, scaling, runtime suspend/resume, and hub clock parent selection.
