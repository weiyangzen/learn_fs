# sources/distributed-fs/ceph-client/fs/nfs/flexfilelayout/flexfilelayout.h

Purpose: defines the shared data model and helper accessors for the NFSv4 flexfile pNFS layout driver. It is the contract between the main layout driver and device-id/DS helper code.

Important APIs and types: defines layout flags `FF_FLAGS_NO_LAYOUTCOMMIT`, `FF_FLAGS_NO_IO_THRU_MDS`, and `FF_FLAGS_NO_READ_IO`; mirror and stripe caps; layoutstats constants; `struct nfs4_ff_ds_version`; `struct nfs4_ff_layout_ds`; `struct nfs4_ff_layout_ds_err`; `struct nfs4_ff_io_stat`; `struct nfs4_ff_layoutstat`; `struct nfs4_ff_layout_ds_stripe`; `struct nfs4_ff_layout_mirror`; `struct nfs4_ff_layout_segment`; `struct nfs4_flexfile_layout`; and `struct nfs4_flexfile_layoutreturn_args`. Inline helpers translate generic pNFS objects to flexfile containers and compute stripe ids.

Control flow: the header itself has no active control flow, but its accessors shape driver behavior. `FF_LAYOUT_FROM_HDR`, `FF_LAYOUT_LSEG`, and `FF_LAYOUT_MIRROR_DS` are container conversions. `FF_LAYOUT_COMP` and `FF_LAYOUT_DEVID_NODE` safely select mirror/device nodes. `nfs4_ff_layout_calc_dss_id` maps a file offset through stripe unit and stripe count to the selected DS stripe. Flag helpers decide whether MDS fallback and reads on RW layouts are allowed.

State and persistence behavior: all structures are in-memory runtime state. Device ids are chained through the global pNFS deviceid cache. Mirrors are refcounted and linked on the layout header. DS errors persist until fetched for layout error/return reporting. Credentials are RCU pointers in each stripe. Layoutstats counters and busy timers accumulate until reported or encoded.

Dependencies and integration points: includes Linux refcounting and the NFS pNFS header. It declares functions implemented by `flexfilelayout.c` and `flexfilelayoutdev.c` for device-id allocation/free, DS preparation, DS client selection, credentials, error tracking/encoding/fetching, filehandle/stateid selection, and fallback policy.

Risks: structure invariants matter: all mirrors in a segment are expected to have a valid `dss_count`, `mirror_array_cnt` must not exceed the configured cap, `mirror_ds` may be NULL or an ERR_PTR during connection setup, and RCU credential pointers require paired refcount handling. `nfs4_ff_layout_ds_version` assumes `mirror_ds` and at least one version are valid, so callers must prepare/check DS state first.

Test signals: compile coverage with pNFS flexfile enabled, KASAN/lockdep/RCU checks during layout allocation/free, striped offset tests for `nfs4_ff_layout_calc_dss_id`, DS unavailable paths that use `FF_LAYOUT_DEVID_NODE`, and layout flag tests for fallback/read selection.
