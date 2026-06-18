
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/index/common.go

- Purpose: common constants, flags, and package checks for BeeGFS Hive Index commands.
- Important APIs: `beeBinary`, `indexConfig`, package-level `path`, `commonIndexFlags`, and `checkBeeGFSConfig`.
- Control flow/state: validates external binary `/opt/beegfs/python/index/bee` and config `/etc/beegfs/index/config`; common flags translate CTL names to Hive Index CLI flags.
- Dependencies/integration: uses `bflag` and global config wrappers for mount point, worker count, and debug.
- Risks/tests: global `path` is shared by stat/stats commands and could be confusing; existence checks ignore non-ENOENT stat failures. No direct tests found.
