# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/tcm-sita.c

Purpose: Provides the SiTA TILER container manager allocation algorithm for 1D and 2D slot reservation over a bitmap-backed container.

Important APIs/types/functions: `sita_init` constructs `struct tcm` and installs function pointers. Internal algorithms include `r2l_b2t_1d` for right-to-left/bottom-to-top 1D allocation, `l2r_t2b` for left-to-right/top-to-bottom aligned 2D allocation, `sita_reserve_1d`, `sita_reserve_2d`, `sita_free`, and `free_slots`.

Control flow: `sita_init` allocates a `tcm` plus bitmap, initializes dimensions and spinlock, and clears all slots. 1D reserve searches for a long enough free run, marks it, and converts the linear position to area coordinates. 2D reserve scans zero areas with alignment/offset constraints, checks row boundaries and subsequent row intersections, marks every row on success, and records the rectangle. Free converts an area back to start/width/height and clears bits.

State and persistence: Container state is in `tcm->bitmap`, protected by `tcm->lock`. The file has a static `mask[8]` scratch bitmap used under the same lock during 2D searches.

Dependencies and integration: Implements the function table declared in `tcm.h`; used by OMAP DMM/TILER code to reserve aperture slots for GEM and user-GART mappings.

Risks: Static `mask[8]` assumes slot stride fits that scratch size. The 2D allocator has an explicit TODO for overlapping 4K boundaries and FIXME for `slots_per_band > stride`. 1D search arithmetic around unsigned positions must avoid underflow. Allocation policy can fragment the bitmap.

Test signals: Reserve/free round trips for 1D and 2D areas, alignment and offset cases, full/fragmented containers, invalid zero dimensions, concurrent reserve/free under lock, and boundary cases at row ends.
