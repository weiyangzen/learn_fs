<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/vdpa/pds/debugfs.c

Purpose: Provides debugfs observability for PDS vDPA management identity, virtio net config/status/features, and per-virtqueue software state.

Important APIs/functions: `pds_vdpa_debugfs_create()` and `destroy()` manage the root. `pds_vdpa_debugfs_add_pcidev()`, `add_ident()`, `add_vdpadev()`, `del_vdpadev()`, and `reset_vdpadev()` manage per-VF files. Show handlers render identity, config, and per-VQ data. `print_feature_bits_all()` decodes many virtio net and transport feature bits.

Control flow: Probe creates a PCI-device directory and identity file after firmware identity is read. `dev_add` adds a config file and one file per VQ. `dev_del` resets the vDPA-specific files by removing and rebuilding the base directory and identity file.

State and persistence: Debugfs files are read-only views over live driver state and MMIO config. `config_show()` reads the virtio net config from the modern device's `device` region and status through `vp_modern_get_status()`. VQ files reflect `pds_vdpa_vq_info`.

Dependencies and integration points: Depends on Linux debugfs/seq_file, virtio net config layout, PDS auxiliary state, and PDS vDPA device structs. It is optional observability, not required for data path.

Risks: Debugfs pointers become invalid if files outlive the associated `vdpa_aux` or `pdsv`; lifecycle functions remove/recreate entries to avoid that. Feature decoding is hard-coded and will show unknown bits as `bit_N`. `pds_vdpa_debugfs_del_vdpadev()` removes the whole PCI directory, so callers must recreate identity after device deletion.

Test signals: Inspect `/sys/kernel/debug/<module>/<pci>/identity`, `config`, and `vqNN` while adding/removing devices. Verify feature names, status bits, queue addresses/indices, and absence of stale files after `dev_del` and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/debugfs.c -->
