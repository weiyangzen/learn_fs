# sources/distributed-fs/ceph-client/include/uapi/drm/tegra_drm.h

## Purpose
This header defines both the legacy staging Tegra DRM UAPI and the newer Host1x channel/syncpoint UAPI. It covers GEM creation/mapping/tiling/flags, syncpoint read/increment/wait, legacy channel submission with relocations and wait checks, newer channel open/map/submit/unmap flows, syncobj integration, and explicit syncpoint allocation/free/wait.

## Important APIs and types
Legacy GEM structs include `drm_tegra_gem_create`, `gem_mmap`, set/get tiling, and set/get flags. Legacy syncpoint structs include `syncpt_read`, `syncpt_incr`, and `syncpt_wait`, with `DRM_TEGRA_NO_TIMEOUT`. Legacy channel submission uses `open_channel`, `close_channel`, `get_syncpt`, `get_syncpt_base`, `drm_tegra_cmdbuf`, `drm_tegra_reloc`, `drm_tegra_waitchk`, and `drm_tegra_submit`.

The newer ABI starts at command IDs `0x10` and `0x20`. `drm_tegra_channel_open` selects a Host1x class and returns a context, engine version, and capabilities such as cache coherence. `drm_tegra_channel_map` maps GEM handles to channel-local mapping IDs with read/write flags. `drm_tegra_submit_buf` defines relocation patching against mappings. `drm_tegra_submit_cmd` represents gather-uptr and syncpoint wait commands. `drm_tegra_channel_submit` passes buffer, command, gather-data arrays, optional syncobj in/out handles, and a syncpoint increment descriptor. `drm_tegra_syncpoint_allocate/free/wait` manage explicit syncpoints.

## Control flow and state
Legacy userspace creates GEM buffers, opens a channel for a client ID, obtains syncpoint IDs and wait bases, builds command buffers, relocations, wait checks, and syncpoint increment arrays, then submits and receives a fence threshold. New userspace opens a Host1x channel, maps BOs to that channel, builds gather data and relocation descriptors, submits command arrays with optional DRM syncobj dependencies, receives the final syncpoint value, and later unmaps/closes resources. Syncpoint waits compare an ID against a threshold with either millisecond legacy timeout or absolute nanosecond timeout in the new ABI.

## State and persistence behavior
GEM handles persist per DRM file; tiling and bottom-up flags are persistent BO metadata. Legacy channel contexts are opaque `__u64`, while new channel contexts are `__u32`; both remain valid until close. Channel mappings persist until unmapped and are the stable IDs used for relocations. Syncpoints are persistent counters, and allocated syncpoints must be freed. Submission fence values are thresholds, not opaque fence handles.

## Dependencies and integration points
The header depends on `drm.h`, Host1x engine classes, Tegra syncpoints, DRM GEM, DRM syncobjs, and memory-layout modifiers such as tiled/block/bottom-up surfaces. It integrates with host command streams and gather opcodes, where userspace provides Host1x command words but the kernel patches relocations and enforces synchronization.

## Risks and test signals
Risks include incorrect legacy/new context mixing, wrong array counts, command-buffer relocation beyond bounds, nonzero reserved fields, unsafely mapped write-only/read-only buffers, syncpoint leaks, and timeout semantic confusion. Test signals should cover both legacy and new ioctl families, tiling/flag round trips, syncpoint wait timeout/no-timeout behavior, channel map/unmap lifetime, gather-uptr command parsing, relative and absolute syncpoint waits, syncobj in/out replacement, cache-coherent capability reporting, and invalid relocation shift/offset handling.
