# sources/distributed-fs/ceph-client/fs/nfs/nfsroot.c

## Purpose

`sources/distributed-fs/ceph-client/fs/nfs/nfsroot.c` prepares the device string and text mount options used when the kernel mounts its root filesystem over NFS. It combines early IP autoconfiguration state, DHCP/BOOTP root path data, and the `nfsroot=` kernel command-line option into the `server:/export` and option strings consumed by the normal NFS mount path. The source was read as a complete 316-line file for this report.

## Important APIs, Types, and Functions

The exported entry point is `int __init nfs_root_data(char **root_device, char **root_data)`, which validates the selected server address, calls the internal parser, and returns pointers to the prepared static buffers.

Early-boot setup functions are `nfs_root_setup`, registered with `__setup("nfsroot=", nfs_root_setup)`, and, under `NFS_DEBUG`, `nfs_root_debug`, registered with `__setup("nfsrootdebug", nfs_root_debug)`. Helper functions are `root_nfs_copy`, `root_nfs_cat`, `root_nfs_parse_options`, and the internal `root_nfs_data`.

Important file-level state includes `nfs_root_parms`, `nfs_root_options`, `servaddr`, `nfs_export_path`, and `nfs_root_device`. Defaults are `NFS_ROOT` (`/tftpboot/%s`) and `NFS_DEF_OPTIONS`, which selects an NFS protocol version based on kernel configuration and always includes TCP plus 4096-byte read/write sizes.

## Control Flow

During command-line parsing, `nfs_root_setup` marks `ROOT_DEV` as `Root_NFS`. If the option begins like an absolute path, comma option list, or IPv4 address, it copies the line directly. Otherwise it treats the line as a hostname-like token and interpolates it into the default `/tftpboot/%s` path template. It then calls `root_nfs_parse_addr`, which may remove a leading `server-ip:` component from `nfs_root_parms` and stores the address in the global `root_server_addr`.

At mount-root time, `nfs_root_data` copies `root_server_addr` into `servaddr`, rejects `INADDR_NONE`, invokes `root_nfs_data`, and returns the static device/options buffers to the caller.

`root_nfs_data` starts with a temporary copy of the default root path. If DHCPv4 option 17 populated `root_server_path`, it parses that first. If the kernel command line supplied `nfsroot=`, it parses that next so command-line path/options override DHCP-derived values. It appends mandatory `nolock,addr=<server-ip>` options last so they override earlier text options. Finally it substitutes `utsname()->nodename` into the selected export path template and formats `nfs_root_device` as `<server-ip>:<export-path>`.

`root_nfs_parse_options` splits an incoming string at the first comma. A nonempty, non-`default` first field becomes the export path; the remaining comma-separated text is appended to the global options buffer. `root_nfs_cat` inserts a comma separator when needed and rejects truncation.

## State and Persistence Behavior

All storage is `__initdata` and used only during early boot. `nfs_root_parms` holds the raw or transformed command-line parameter, `nfs_root_options` accumulates defaults plus DHCP/command-line/mandatory options, `servaddr` holds the selected server IPv4 address, `nfs_export_path` holds the final export path after `%s` substitution, and `nfs_root_device` holds the mount device string.

There is no file-backed persistence. Once the root mount data is handed to the NFS mount interface, later NFS mount state is owned by the standard NFS superblock/client code. The temporary allocation in `root_nfs_data` is freed before return.

## Dependencies and Integration Points

The file depends on kernel init command-line parsing (`__setup`), root device selection (`ROOT_DEV`, `Root_NFS`), IP autoconfiguration state from `<net/ipconfig.h>` such as `root_server_addr` and `root_server_path`, NFS mount internals declared by `"internal.h"`, and UTS nodename populated by ipconfig.

It integrates with the generic NFS text mount parser by returning strings rather than building binary mount data locally. It also relies on `root_nfs_parse_addr` to strip a leading server address and on normal NFS mount code to interpret options such as `vers=`, `tcp`, `rsize`, `wsize`, `nolock`, and `addr=`.

## Risks and Edge Cases

Buffer sizing and truncation handling are central. Path and device buffers are bounded by `NFS_MAXPATHLEN + 1`; options are limited to 256 bytes. Helper functions return `-1` on `strscpy`, `strlcat`, or `snprintf` overflow, and user-visible errors distinguish allocation failure, option overflow, and device-name overflow.

The `%s` substitution in the export path is intentionally late so DHCP/ipconfig can set the nodename, but it means path strings are interpreted as `snprintf` format strings. Existing behavior expects `%s` use for nodename substitution; unexpected format tokens would be risky if not constrained by boot-time trusted input assumptions.

Override order matters. DHCP option 17 is parsed before command-line `nfsroot=`, and mandatory `nolock,addr=` is appended last. Changing this order can alter real boot behavior. The special path value `default` preserves the currently selected default path while still allowing options to be appended.

Only IPv4 server formatting is used (`%pI4`, `INET_ADDRSTRLEN`, `__be32`). IPv6 root-over-NFS behavior is outside this code path. A missing server address is fatal even if an export path is available.

## Test Signals

Useful test signals include boot tests with `root=/dev/nfs` and `nfsroot=` variants covering plain path, `server-ip:path`, options-only strings, `default,<opts>`, hostname-token transformation, and DHCP option 17; overflow tests for long export paths and long option strings; confirmation that command-line values override DHCP path/options while `nolock,addr=` remains last; debug boot tests with `nfsrootdebug`; and regression boots across `CONFIG_NFS_V2`, `CONFIG_NFS_V3`, and v4-only builds to confirm default `vers=` selection.
