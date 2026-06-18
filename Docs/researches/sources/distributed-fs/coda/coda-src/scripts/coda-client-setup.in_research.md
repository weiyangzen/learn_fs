# sources/distributed-fs/coda/coda-src/scripts/coda-client-setup.in

Purpose: initializes a Coda client installation by writing `venus.conf`, creating cache/log/runtime directories, arranging kernel module/device setup, and marking the cache for initialization.

Control flow: validates arguments differently for Cygwin and Unix, sets realm and cacheblocks via `codaconfedit`, reads generated `venus.conf`, applies default paths, creates parent directories with a custom mode-preserving `makedir`, loads the Linux `coda` kernel module and boot autoload configuration for udev systems, handles Cygwin drive mapping and private mapping config, creates the mountpoint and `NOT_REALLY_CODA`, attempts `/dev/cfs0`/`/dev/coda/0` creation via `MAKEDEV`, then touches `$cachedir/INIT`.

State/persistence: modifies `/etc/coda`-style config through `codaconfedit`, system module config (`/etc/rc.modules` or `/etc/modules`), `/dev`, mountpoint contents, Cygwin symlink `/coda`, and client cache/log/runtime directories.

Dependencies, risks, tests: requires root-like privileges, `codaconfedit`, platform tools, and correct config paths. Risks include unquoted path uses in a few places, host-specific init-system assumptions, direct edits to `/etc/modules`, and destructive Cygwin `/coda` removal. Test on Linux with existing/new directories, missing kernel device, Cygwin drive-letter validation, custom `venus.conf` paths, and idempotent rerun.
