## sources/distributed-fs/coda/coda-src/volutil/vol-info.cc

Purpose: `vol-info.cc` generates a textual report for a Coda volume and transfers it to the client. It can include volume header metadata, resolution logs/stats, and optionally all vnode records.

Important APIs/types/functions: RPC `S_VolInfo` resolves a volume key, attaches the volume, writes `/tmp/volinfo.tmp`, and transfers it. Helpers are `PrintHeader`, `printvns`, `PrintVnode`, `date`, and `typestring`.

Control flow: initialize volutil, locate volume id with `VOL_Locate`, attach via `VGetVolume`, open the temp file, print header fields, print resolution log/statistics if enabled, optionally iterate large and small vnode indexes, close file, put volume, then send the file using SMARTFTP `FILEBYNAME`.

State and persistence behavior: creates/overwrites a fixed temp file `/tmp/volinfo.tmp` and reads volume/vnode state. It does not mutate the volume except resolution stats pre/post collection may update in-memory statistic state.

Dependencies/integration points: integrates with volume lookup/attachment, vnode index iterators, resolution logs (`V_VolLog`), stats, RPC2 side effects, and shared `PrintVnode` used by `vol-create` debug code.

Risks: fixed temp filename is race-prone and unsafe under concurrent requests. The function does not check `fopen` failure before printing. Date formatting uses `localtime` and `sprintf` into caller buffer. `VInitVolUtil` return is ignored. It exposes raw vnode inode/dir-node pointer values in text output.

Test signals: request by name and id, invalid volume key, `dumpall` on/off, volumes with resolution enabled/disabled, concurrent requests, side-effect failure, and file permission/temp directory failure.
