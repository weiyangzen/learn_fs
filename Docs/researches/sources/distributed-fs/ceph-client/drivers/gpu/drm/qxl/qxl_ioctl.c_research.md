# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_ioctl.c

Purpose: This file implements QXL-specific DRM ioctls for allocation, mapping, execbuffer submission, explicit update areas, capability queries, and surface allocation.

Important APIs, types, and functions: Public ioctl handlers include `qxl_alloc_ioctl()`, `qxl_map_ioctl()`, `qxl_execbuffer_ioctl()`, `qxl_update_area_ioctl()`, `qxl_getparam_ioctl()`, `qxl_clientcap_ioctl()`, and `qxl_alloc_surf_ioctl()`. Internal helpers process relocations through `apply_reloc()`, `apply_surf_reloc()`, `qxlhw_handle_to_bo()`, and `qxl_process_single_command()`.

Control flow: Execbuffer processing accepts only draw commands, validates command size and user pointers, allocates a release BO, copies the command payload after the release-info header, stamps `mm_time`, copies relocation metadata from userspace, resolves GEM handles into release BO lists, reserves/validates all BOs, applies physical-address or surface-ID relocations, fences objects, and pushes the command ring. Update-area ioctl validates rectangle ordering, looks up/reserves the BO, validates placement, ensures a surface ID, and issues an update-area I/O command.

State and persistence: Ioctls create GEM BOs, release objects, relocation writes into BO memory, host-visible surfaces, and command submissions. User handles persist until closed; releases persist until host completion.

Dependencies and integration points: Registered in `qxl_drv.c`; depends on QXL UAPI structs, DRM GEM lookup, usercopy helpers, TTM validation, release helpers, BO mapping, command ring pushes, and QXL protocol relocation semantics.

Risks: User input is high-risk: command sizes, relocation counts, offsets, and surface allocation sizes need overflow and bounds scrutiny. `qxl_alloc_surf_ioctl()` computes `size = abs(stride) * height + abs(stride)` without explicit overflow checks. Relocation writes assume destination offsets are valid within mapped BO pages.

Test signals: Fuzz QXL ioctls with invalid handles, bad pointers, high relocation counts, oversized command sizes, invalid update rectangles, negative stride surface allocation, and interrupted command-ring waits; run normal xf86-video-qxl acceleration paths.
