# sources/distributed-fs/ceph-client/fs/nfsd/pnfs.h

Purpose: `pnfs.h` declares NFSD pNFS layout infrastructure used by NFSv4.1+ layout operations. It provides layout operation callbacks, device-id mapping, layout state preprocessing/return APIs, and no-op stubs when pNFS is disabled. The source was read as a complete 110-line file.

Important APIs/types/functions: important types are `struct nfsd4_deviceid_map` and `struct nfsd4_layout_ops`. Callback members cover device info, layout get, layout commit, layout encoding, client fencing, notification types, and recall behavior. Declarations include `nfsd4_preprocess_layout_stateid`, `nfsd4_insert_layout`, `nfsd4_return_file_layouts`, `nfsd4_return_client_layouts`, `nfsd4_set_deviceid`, `nfsd4_find_devid_map`, `nfsd4_setup_layout_type`, `nfsd4_return_all_client_layouts`, `nfsd4_return_all_file_layouts`, `nfsd4_close_layout`, `nfsd4_init_pnfs`, and `nfsd4_exit_pnfs`.

Control flow: the header has no executable control flow except stubs. In enabled builds, NFSv4 layout operations preprocess a layout stateid, call the export-selected layout backend through `nfsd4_layout_ops`, insert or return layout state, encode responses through XDR helpers, and optionally fence clients using backend-specific logic with retry backoff capped by `MAX_FENCE_DELAY`.

State and persistence: declared state is live NFSv4/pNFS state: per-client and per-file layout stateids, layout segments, device-id maps keyed by fsid/device generation, and backend callbacks. There is no direct persistence here, but layout state interacts with client lease/grace semantics and backend fencing.

Dependencies and integration points: depends on NFSv4 state (`state.h`), NFSv4 XDR (`xdr4.h`), exportfs, and export metadata. Optional backends include block, SCSI, and flexfile layouts. It is integrated by NFSv4 operation handlers and service/module init paths via `nfsd4_init_pnfs`/`nfsd4_exit_pnfs`.

Risks: feature stubs must make non-pNFS builds behave as if no layouts exist. Device-id fsid encoding must match filehandle/export identity. Fencing retries can delay recovery; disabled recalls or unsupported backends must not leave clients with stale layout authority. Layout stateid preprocessing must distinguish create versus existing paths and layout types.

Test signals: build coverage with `CONFIG_NFSD_PNFS` off and each backend on, layoutget/layoutcommit/layoutreturn protocol tests, device-id stability checks, recall/fence retry behavior, client/file-wide layout return tests, and export option tests that enable or suppress layout types.
