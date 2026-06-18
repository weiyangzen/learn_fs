## sources/distributed-fs/eos/mgm/ofs/cmds/Version.inc

Purpose: implements file version creation and version retention purge. Versions are stored under hidden `.sys.v#.<name>/` directories with filenames derived from ctime and fid.

Important APIs and types: `XrdMgmOfs::Version`, `XrdMgmOfs::PurgeVersion`, `VirtualIdentity`, `IFileMD`, `XrdMgmOfsDirectory`, `Path::DecodeAtomicPath`, `_stat`, `_mkdir`, `_chmod`, `_rename`, `_attr_ls`, `_rem`, `ProcCommand`, and root identity.

Control flow for version creation: `Version()` loads file metadata under read lock, translates fid to path, decodes atomic paths, uses the file owner identity for versioning, captures file ctime, and rejects non-root callers who are not the file owner. It builds `.sys.v#.<basename>/<ctime>.<fidhex>`, optionally returns that path, creates the version directory if missing, ensures owner write permission by chmod as root, then renames the current file into the version path unless `simulate` is true. If `max_versions > 0`, it purges according to policy.

Control flow for purge: `PurgeVersion()` accepts explicit `max_versions`, reads `sys.versioning` from the parent when negative, and returns if no policy exists. If `max_versions == 0`, it recursively removes the whole version directory via `/proc/user` `rm -r` as root to preserve recycle semantics. Otherwise it lists version entries, computes age from the timestamp prefix, keeps at most one oldest entry per age bin, and removes older entries beyond the requested count with `_rem()`.

State and persistence behavior: creates hidden version directories, changes permissions, renames live files into version storage, removes old version files/directories, and may invoke recycle-aware delete paths. `simulate` validates/builds version naming without performing the main rename.

Dependencies and integration points: used by write/commit atomic upload paths and `_rem()` version purge cleanup. Depends on hidden path conventions, root identity for metadata management, existing rename/delete semantics, and directory attribute policy `sys.versioning`.

Risks: version filenames depend on ctime seconds plus fid; collision handling is not in this file but appears in commit helper. Purge ordering uses directory iteration order for `versions` while age keep-set is computed separately, so deletion order may not be strictly chronological unless directory listing is stable. Recursive delete through proc releases control to command infrastructure.

Test signals: owner vs non-owner version permission, version directory creation and chmod, simulate mode, successful rename to `.sys.v#`, max-version purge, `max_versions=0` recursive delete, negative policy read from parent attr, missing policy no-op, age-bin retention, and integration with atomic commit versioning.
