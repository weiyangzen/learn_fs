# sources/distributed-fs/lizardfs/src/mount/fuse/main.cc

## Purpose
This is the `mfsmount` executable entrypoint and libfuse low-level session bootstrap. It wires either the normal LizardFS mount operations or the meta/trash filesystem operations into `fuse_lowlevel_ops`, parses command line and config-file options, initializes client-side master/chunkserver subsystems, daemonizes when requested, and owns orderly teardown after the FUSE loop exits.

## Important APIs, Types, And Functions
`init_fuse_lowlevel_ops()` maps FUSE callbacks to `mfs_*` or `mfs_meta_*` functions, conditionally enabling POSIX and BSD-style locks when `gMountOptions.filelocks` is set. `mfs_fsinit()` applies FUSE connection flags such as `FUSE_CAP_DONT_MASK`, POSIX ACL support on FUSE 3, and disables `FUSE_CAP_ATOMIC_O_TRUNC`. `setup_password()` converts a plaintext mount password to an MD5 digest or parses a supplied digest, then zeroes the original option buffer. `mainloop()` performs runtime setup, client initialization, FUSE session creation/mounting, signal handler registration, loop execution, unmount, session destruction, and subsystem termination. `read_masterhost_if_present()` supports the positional `HOST[:PORT]:[PATH]` syntax, while `make_fsname()` builds a FUSE `fsname`/`subtype` option with comma escaping depending on libfuse version.

## Control Flow
`main()` builds separate default and user `fuse_args`, reads positional master syntax, stage-1 parses only config-file options, optionally loads the default config, stage-2 parses defaults then user arguments, parses FUSE 3 connection options, validates cache and sugid modes, fills defaults for master host/port/subfolder, clamps cache sizes and worker counts, appends standard mount options, creates the FUSE-visible fs name, parses the final command line, prompts for passwords if requested, validates the mountpoint, and then either calls `mainloop()` directly or through `daemonize_and_wait()`. `mainloop()` initializes `LizardClient` for a normal mount; in meta mode it initializes `masterproxy`, symlink cache, master connection, and I/O threads manually before selecting the meta operation table.

## State And Persistence
The file mutates process-global `gMountOptions`, `gDefaultMountpoint`, FUSE argument vectors, syslog/stderr logging sinks, resource limits, process priority/session state, password option buffers, and FUSE session state. It does not persist repository data, but it opens long-lived network state through master connections, I/O threads, read/write caches, symlink cache, and master proxy state that must be terminated on each failure path.

## Dependencies And Integration Points
It integrates `mount_config.*`, `mfs_fuse.*`, `mfs_meta_fuse.*`, `LizardClient`, `mastercomm`, `masterproxy`, `readdata`, `writedata`, `stats`, `symlinkcache`, libfuse 2/3 APIs, daemonization helpers, syslog, MD5 helpers, and default protocol constants. Compile-time `FUSE_VERSION` branches significantly change startup, mount, command-line, and cleanup behavior.

## Risks And Test Signals
Risk centers on option lifetime and manual memory ownership, version-specific FUSE paths, duplicate or partially failed subsystem initialization, and unsupported FUSE 3 rename flags being ignored. The mountpoint non-empty check is local to FUSE 3. Test signals should include option parsing permutations, password zeroing behavior, FUSE 2/3 builds, meta vs normal startup failure cleanup, cache-mode validation, and daemon/foreground flows.
