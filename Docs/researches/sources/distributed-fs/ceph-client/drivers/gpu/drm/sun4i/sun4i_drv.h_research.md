# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_drv.h

## Purpose
`sun4i_drv.h` defines the small master-driver private structure shared by Allwinner display-engine components.

## Important APIs, Types, and Functions
- `struct sun4i_drv`: contains `engine_list`, `frontend_list`, and `tcon_list`, each populated by component bind functions and consumed by pipeline setup code.

## Control Flow, State, and Persistence
There is no direct control flow. `sun4i_drv_bind` initializes the lists and stores the structure in `drm->dev_private`. Component drivers add/remove their instances during bind/unbind, and backend code searches `frontend_list` to wire optional frontend processing.

## Dependencies and Integration Points
The header includes Linux list/clock/regmap headers and is included by master, backend, frontend, and framebuffer code. It is the common rendezvous structure for the componentized display pipeline.

## Risks and Test Signals
The lists are not independently locked during normal component bind/unbind, so users rely on component-framework ordering and DRM master lifecycle. Tests should exercise component bind/unbind ordering and multi-pipeline configurations where lists contain several engines, frontends, and TCONs.
