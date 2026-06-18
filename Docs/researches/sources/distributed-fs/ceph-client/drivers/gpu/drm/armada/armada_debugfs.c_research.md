# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_debugfs.c

## Purpose

`armada_debugfs.c` implements debugfs support for the Armada DRM driver. It exposes the global linear GEM memory allocator state and per-CRTC LCD register dumps/masked writes.

## Important APIs, Types, And Functions

The exported functions are `armada_drm_crtc_debugfs_init()` and `armada_drm_debugfs_init()`. `armada_debugfs_gem_linear_show()` prints `priv->linear` through `drm_mm_print()`. `armada_debugfs_crtc_reg_show()` dumps registers from offsets `0x84` through `0x1c4`. `armada_debugfs_crtc_reg_write()` parses `reg mask val`, validates range/alignment, and applies a masked register write.

## Control Flow

The driver-level debugfs init creates a DRM info file named `gem_linear`. Each CRTC late-register hook creates `armada-regs` under the CRTC debugfs entry. Reads walk allocator/register state. Writes to `armada-regs` are accepted only at offset zero, truncated to a small stack buffer, parsed, range-checked, then applied directly to MMIO.

## State And Persistence Behavior

Debugfs reads do not mutate state except for normal locking. Writes mutate live hardware registers and persist until later driver writes or reset. `gem_linear` output reflects the current `drm_mm` allocator protected by `linear_lock`.

## Dependencies And Integration Points

The file depends on debugfs, seq_file, uaccess, DRM debugfs helpers, Armada private state, and CRTC MMIO. It is conditionally built by the Makefile under `CONFIG_DEBUG_FS` and called from the master and CRTC registration paths.

## Risks And Edge Cases

The register write interface is powerful and bypasses normal driver validation; it is root/debugfs-only but can disrupt active scanout. Only a fixed register range is exposed. Parsing uses `%lx` values and does not accept symbolic names. Direct MMIO writes are not synchronized with all atomic paths except no explicit locks here.

## Test Signals

Validation includes debugfs presence under `CONFIG_DEBUG_FS`, absence when disabled, `gem_linear` consistency during GEM allocate/free, register dump readability, invalid write rejection, valid masked write behavior, and no crashes during concurrent modesets.
