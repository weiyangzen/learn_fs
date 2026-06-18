# sources/distributed-fs/coda/coda-src/vol/voldefs.h

Purpose: centralizes volume type aliases, volume-name formatting, key configuration paths, and file-server connection flags.

Important definitions: aliases map `readwriteVolume`, `readonlyVolume`, `backupVolume`, `replicatedVolume`, and `nonReplicatedVolume` onto numeric `RWVOL`, `ROVOL`, `BACKVOL`, `REPVOL`, and `NONREPVOL`. `VFORMAT` formats volume header/external names as `V%010u`. Paths include `MAXVOLIDPATH` and `SERVERLISTPATH`. `CONNECT_FS` and `DONT_CONNECT_FS` control volume package init behavior.

Control flow/state: no runtime state; these constants are consumed by `volume.h`, `volhash.cc`, `volume.cc`, utilities, and lookup code.

Dependencies/integration: uses `vice_config_path` through path macros. Risks include adding a volume type without updating `VolumeWriteable`, VLDB/VRDB assumptions, or external format compatibility. Test signals: volume type handling in attach/list/lookup, server-list path resolution, and volume external-name formatting.
