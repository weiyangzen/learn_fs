# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/debugfs.c

Purpose: creates debugfs controls and diagnostics for GVT and individual vGPUs.

Important APIs/types/functions: public functions are `intel_gvt_debugfs_init()`, `intel_gvt_debugfs_clean()`, `intel_gvt_debugfs_add_vgpu()`, and `intel_gvt_debugfs_remove_vgpu()`. File operations include `vgpu_mmio_diff_show()`, `vgpu_scan_nonprivbb_get()`, `vgpu_scan_nonprivbb_set()`, and `vgpu_status_get()`. Internal diff tracking uses `struct mmio_diff_param` and `struct diff_mmio`.

Control flow: global init creates a `gvt` debugfs root and a `num_tracked_mmio` file. Per-vGPU init creates `vgpuN` directories with `mmio_diff`, `scan_nonprivbb`, and `status` files. `mmio_diff` locks GVT and MMIO context state, reads hardware tracked MMIO under wakeref, compares against vGPU virtual registers, sorts differences by offset, prints them, and frees temporary nodes. The `scan_nonprivbb` attribute controls the command parser mask for nonprivileged batch scanning.

State and persistence: persistent debugfs dentries are stored in `gvt->debugfs_root` and `vgpu->debugfs`. `scan_nonprivbb` directly mutates `vgpu->scan_nonprivbb`; `status` reflects attached/active bits. `mmio_diff` allocates only transient list entries.

Dependencies and risks: depends on debugfs, seq_file helpers, list sorting, GVT MMIO iteration, uncore reads, and scheduler locks. Risks include debugfs unsafe file lifetime, atomic allocation failure during diff collection, lock ordering around GVT and MMIO context locks, and exposing mutable parser behavior through debugfs. Test signals include create/remove under debugfs, accurate MMIO diff counts, scan mask round trips, status bit reporting, and clean recursive removal on vGPU/GVT teardown.
