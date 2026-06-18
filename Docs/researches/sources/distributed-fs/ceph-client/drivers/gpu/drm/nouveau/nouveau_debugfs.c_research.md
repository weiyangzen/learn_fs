# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_debugfs.c

Purpose: Provides Nouveau debugfs files for VBIOS dump, strap register peek, performance state inspection/control, GPUVA reporting, and module-level debugfs root creation.

Important APIs/functions: `nouveau_drm_debugfs_init()`, `nouveau_debugfs_init()`, `nouveau_debugfs_fini()`, `nouveau_module_debugfs_init()`, and `nouveau_module_debugfs_fini()`. File callbacks include `nouveau_debugfs_vbios_image()`, `nouveau_debugfs_strap_peek()`, `nouveau_debugfs_pstate_get/set/open()`, `nouveau_debugfs_gpuva()`, and `nouveau_debugfs_gpuva_regions()`.

Control flow: Per-device init allocates `drm->debugfs` and constructs an nvif control object. Minor init creates writable `pstate`, DRM info files `vbios.rom`, `strap_peek`, GPUVA info, and sets the VBIOS inode size. `pstate` read queries state count, attributes, current power source, user states, and current pstate. `pstate` write parses optional `dc:`/`ac:` prefix and `none`/`auto`/hex state, resumes the device, and sends `NVIF_CONTROL_PSTATE_USER`. GPUVA walks all clients, locks each UVMM, prints drm GPUVA info and region maple tree entries.

State/persistence: Persists only the nvif control object and debugfs root/dentries. It reads `drm->vbios`, clients list, UVMM region trees, and hardware strap register. Pstate writes affect GPU power-management policy via nvif control.

Dependencies/integration: Uses Linux debugfs/seq_file, DRM debugfs helpers, runtime PM, nvif control methods, Nouveau client/UVMM locking, and global `nouveau_debugfs_root`.

Risks/test signals: Debugfs reads can race with client teardown unless locks are correct. Pstate writes are privileged but still need careful input parsing and runtime PM balancing. Test with debugfs disabled build, reading VBIOS size/contents, pstate read/write under suspend, GPUVA output with multiple clients, and module unload cleanup.
