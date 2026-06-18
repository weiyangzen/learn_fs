# Group Research: FreeBSD newfs, newfs_msdos, nfsiod, nos-tun, and nvmecontrol subset

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/newfs/mkfs.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/newfs/mkfs.c

Implements the low-level UFS/FFS filesystem builder used by `newfs.c`. `mkfs()` computes and validates superblock geometry, block/fragment sizes, cylinder-group layout, inode density, summary areas, feature flags, metadata check hashes, soft updates, gjournal, multilabel, TRIM, and volume label state before writing the initial filesystem image.

Key behaviors:
- Converts frontend globals from `newfs.h` into `struct fs` and `struct uufsd` disk state.
- Supports UFS1 and UFS2 paths, including UFS1 legacy fields and UFS2 recovery metadata.
- Writes backup superblocks, cylinder-group maps, initialized inode blocks, root directory, and optional `.snap` directory.
- Uses `Nflag` dry-run mode, `Rflag` deterministic timestamps/randoms for regression testing, and `Xflag` failure injection exits.
- Contains bitmap helpers for fragment availability (`isblock`, `setblock`, `clrblock`) and first-cylinder-group allocation helpers for root bootstrap objects.

Important dependencies:
- FreeBSD UFS/FFS headers: `ufs/ufs/dinode.h`, `ufs/ufs/dir.h`, `ufs/ffs/fs.h`.
- `libufs` disk operations exposed through `struct uufsd`, `bread`, `bwrite`, `sbwrite`, `cgwrite`, `getinode`, and `putinode`.
- Frontend global options declared in `newfs.h`.

Research notes:
- This is the core on-disk UFS layout constructor; bugs here affect superblock validity, fsck recovery, snapshot support, and first mount behavior.
- The `part_ofs` offset workaround means direct `bread()`/`bwrite()` calls must consistently account for file-backed partition offsets.
- The cylinder-group sizing logic is intentionally conservative because `CGSIZEFUDGE` preserves compatibility with older validators.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/newfs/mkfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/newfs/newfs.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/newfs/newfs.c

Command-line frontend for building UFS filesystems. It parses `newfs` options, resolves device or file-backed targets, obtains sector/media size and optional disklabel data, normalizes defaults, then calls `mkfs()`.

Key behaviors:
- Defines all global configuration consumed by `mkfs.c`, including UFS version, block sizes, fragment sizes, inode density, minfree, soft updates, journal flags, volume label, erase/TRIM, and regression/fault-injection flags.
- Accepts both character devices and regular files; file mode can use a BSD label partition offset via `-p`.
- Uses `ufs_disk_fillout_blank()` and `ufs_disk_write()` for device setup unless operating on a plain file.
- Applies default soft updates for UFS2 unless gjournal is requested.
- After `mkfs()`, optionally executes `tunefs -j enable` for soft updates journaling.

Important dependencies:
- `libufs`, `libutil` `expand_number`, disk ioctls `DIOCGSECTORSIZE` and `DIOCGMEDIASIZE`, and BSD disklabel helpers.
- `mkfs()` from `mkfs.c`.

Research notes:
- This file owns user input validation; downstream geometry assumptions in `mkfs.c` rely on this normalization.
- `-R` is important for reproducible filesystem images in the included regression scripts.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/newfs/newfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/newfs/newfs.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/newfs/newfs.h

Shared declarations for the UFS `newfs` frontend and builder. It defines default fragment and block sizes, cylinder-group and inode-density defaults, and extern declarations for all option globals shared by `newfs.c` and `mkfs.c`.

Key contents:
- Defaults: `DFL_FRAGSIZE` 4096 and `DFL_BLKSIZE` 32768.
- `MAXBLKSPERCG`, `MAXBLKPG()`, and `NFPI` sizing policy constants.
- Externs for filesystem sizing, sector sizing, flags, tuning knobs, volume label, and `struct uufsd disk`.
- Documents the `part_ofs` workaround for file-backed partition offsets and libufs `bwrite()` limitations.
- Declares `void mkfs(struct partition *, char *)`.

Research notes:
- This header is the contract tying CLI option state to the UFS layout engine.
- The `part_ofs` comment is architecturally important because it explains a deliberate libufs bypass/hack.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/newfs/newfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/newfs/runtest00.sh -->
# File Research: sources/os/bsd/freebsd-src/sbin/newfs/runtest00.sh

Small regression script for UFS `newfs`. It creates malloc-backed md devices of multiple sizes, labels each, runs `./newfs -R`, and prints an MD5 hash of the resulting partition.

Key behaviors:
- Tests sizes: `1m`, `4m`, `60m`, `120m`, `240m`, `1g`.
- Uses fixed md unit `99`.
- Always attempts cleanup with `mdconfig -d`.
- `-R` ensures deterministic output suitable for hash comparison.

Research notes:
- This validates reproducibility across filesystem sizes, not functional mount behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/newfs/runtest00.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/newfs/runtest01.sh -->
# File Research: sources/os/bsd/freebsd-src/sbin/newfs/runtest01.sh

Regression script checking deterministic image creation. It creates two 1 MB malloc-backed md devices, labels both, runs `./newfs -R` on both, and compares the resulting raw partitions.

Key behaviors:
- Uses md units `99` and `98`.
- Passes if `cmp /dev/md99c /dev/md98c` succeeds.
- Cleans up both md devices before and after.
- Returns shell exit code based on comparison result.

Research notes:
- This specifically exercises the deterministic timestamp/random path in `mkfs.c`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/newfs/runtest01.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/newfs_msdos/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/newfs_msdos/Makefile

Builds the `newfs_msdos` utility.

Key contents:
- Program: `newfs_msdos`.
- Sources: `newfs_msdos.c` and `mkfs_msdos.c`.
- Manual page: `newfs_msdos.8`.
- Package: `runtime`.
- Enables tests via `HAS_TESTS` and `SUBDIR.${MK_TESTS}+= tests`.
- Lowers warnings on ARM with a comment marking this as undesirable.

Research notes:
- The utility is split into CLI wrapper and reusable FAT filesystem construction engine.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/newfs_msdos/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/newfs_msdos/mkfs_msdos.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/newfs_msdos/mkfs_msdos.c

Implements the FAT12/FAT16/FAT32 filesystem construction engine used by `newfs_msdos.c` and also conditionally by `makefs`.

Key behaviors:
- Defines packed on-disk boot-sector, BPB, FAT32 extended BPB, volume label, and directory-entry structures.
- Supports standard floppy formats and inferred geometry from devices, files, disklabels, floppies, or explicit options.
- Validates FAT type, bytes per sector, sectors per cluster, reserved sectors, FAT count, media descriptor, bootstrap file format, FAT32 info/backup sectors, and volume labels.
- Selects FAT12/16/32 automatically when not explicit, computes cluster count, FAT size, root directory sectors, and optional cluster alignment.
- Writes boot sector, BPB, FAT/FAT32 metadata, FSInfo sectors, root directory, and optional volume-label directory entry.
- Supports `no_create` dry-run mode and `create_size` regular-file image creation.
- Uses chunked writes based on `KERN_MAXPHYS`/`MAXPHYS`.
- Provides `SIGINFO` progress reporting while writing metadata sectors.

Important dependencies:
- FreeBSD disk, mount, floppy, disklabel, and sysctl APIs when not compiled as `MAKEFS`.
- `mkfs_msdos.h` option structure.
- Endian packing helpers implemented as local macros (`mk1`, `mk2`, `mk4`).

Research notes:
- This file is the authoritative FAT layout algorithm for FreeBSD `newfs_msdos`.
- The code carefully distinguishes FAT32-only options from FAT12/16-only root directory behavior.
- The `MAKEFS` mode changes device assumptions and requires `create_size`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/newfs_msdos/mkfs_msdos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/newfs_msdos/mkfs_msdos.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/newfs_msdos/mkfs_msdos.h

Shared interface and option schema for the FAT filesystem builder.

Key contents:
- `ALLOPTS` macro declares all supported CLI/build options with option letter, C type, field name, minimum hint, and help text.
- `struct msdos_options` expands `ALLOPTS` into fields.
- Additional bitfields record whether timestamp, volume ID, media descriptor, and hidden sectors were explicitly set.
- Declares `int mkfs_msdos(const char *, const char *, const struct msdos_options *)`.

Research notes:
- The macro is reused by `newfs_msdos.c` to generate usage text, keeping CLI help synchronized with the options structure.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/newfs_msdos/mkfs_msdos.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/newfs_msdos/newfs_msdos.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/newfs_msdos/newfs_msdos.c

Command-line wrapper for creating FAT filesystems. It parses options into `struct msdos_options`, resolves target path and optional disk type, then calls `mkfs_msdos()`.

Key behaviors:
- Parses FAT type, image creation size, bootstrap path, OEM string, volume label/ID, timestamp, block/sector/cluster sizing, geometry, FAT count, media descriptor, reserved sectors, hidden sectors, and dry-run mode.
- Supports suffix multipliers for offsets and create size: sectors, KB, MB, GB.
- If not creating a regular image and the target has no slash, prefixes `/dev/`.
- Enforces `-A` alignment incompatibility with explicit reserved-sector count.
- Generates usage output from `ALLOPTS`.

Research notes:
- CLI validation is mostly range based; structural FAT consistency is checked in `mkfs_msdos.c`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/newfs_msdos/newfs_msdos.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/newfs_msdos/tests/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/newfs_msdos/tests/Makefile

Connects FreeBSD `newfs_msdos` tests to imported NetBSD ATF shell tests.

Key contents:
- `TESTSRC=${SRCTOP}/contrib/netbsd-tests/sbin/newfs_msdos`.
- Adds `create` as a NetBSD ATF shell test.
- Applies sed substitution from `fsck_msdos` to FreeBSD `fsck_msdosfs`.
- Includes `netbsd-tests.test.mk` and `bsd.test.mk`.

Research notes:
- Test coverage is imported/adapted rather than local C tests.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/newfs_msdos/tests/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nfsiod/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/nfsiod/Makefile

Builds the `nfsiod` utility.

Key contents:
- Program: `nfsiod`.
- Manual page: `nfsiod.8`.
- Package: `nfs`.
- Includes `bsd.prog.mk`.

Research notes:
- Minimal build file; all behavior lives in `nfsiod.c`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nfsiod/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nfsiod/nfsiod.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nfsiod/nfsiod.c

Userland control utility for NFS async I/O daemon counts. It ensures NFS support is present, reads current `vfs.nfs.iodmin`/`iodmax`, and optionally sets the maximum daemon count.

Key behaviors:
- Loads the `nfs` kernel module if `getvfsbyname("nfs")` initially fails.
- Supports `-n num_servers`, clamped to `[1, 20]`.
- With no `-n`, prints current `iodmin` and `iodmax`.
- When lowering below current `iodmin`, updates `iodmin` first, then sets `iodmax`.

Research notes:
- It is a sysctl control shim, not a daemon implementation.
- Uses `atoi`, so malformed numeric input is treated as zero and then clamped to one.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nfsiod/nfsiod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nos-tun/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/nos-tun/Makefile

Builds the `nos-tun` utility.

Key contents:
- Program: `nos-tun`.
- Manual page: `nos-tun.8`.
- `WARNS?= 3`.
- Includes `bsd.prog.mk`.

Research notes:
- Minimal build wrapper for a legacy tunnel utility.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nos-tun/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nos-tun/nos-tun.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nos-tun/nos-tun.c

Legacy IP-over-IP tunnel helper for configuring a `tun` interface and forwarding packets through a raw socket using NOS/Cisco-style encapsulation.

Key behaviors:
- Resolves source/destination/target addresses with `inet_addr()` or `gethostbyname()`.
- Opens a tun device, clears prior interface address, assigns point-to-point source/destination addresses, and marks interface up.
- Opens a raw IPv4 socket with protocol 94 by default or user-provided `-p`.
- Optionally binds a raw socket source address.
- Daemonizes, installs signal handlers, and loops with `select()` over tun and raw socket descriptors.
- Packets from raw socket are accepted only from the configured target, decapsulated by skipping the outer IP header, and written to tun.
- Packets from tun are sent to the connected raw socket target.
- Signal cleanup brings the interface down and removes addresses.

Research notes:
- Uses old IPv4-only APIs (`gethostbyname`, `inet_addr`) and global interface request state.
- Does not robustly validate packet lengths before subtracting IP header length.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nos-tun/nos-tun.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/Makefile

Builds the `nvmecontrol` utility and its module subdirectories.

Key contents:
- Program: `nvmecontrol`.
- Adds command sources including command framework, fabrics, firmware, format, identify, logpage, namespace, passthrough, power, reconnect, reset, reservation, sanitize, selftest, telemetry, and utility files.
- Includes sys NVMe path with `.PATH: ${SRCTOP}/sys/dev/nvme`.
- Links with `nvmf`, `sbuf`, and `util`.
- Uses `-rdynamic`, enabling dynamically loaded modules to resolve symbols in the main executable.
- Descends into `modules`; tests are optional via `SUBDIR.${MK_TESTS}+= tests`.

Research notes:
- The listed group includes core command files and logpage modules, but not every source referenced by the Makefile.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/comnd.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/comnd.c

Implements the generic command registration, dispatch, option parsing, help generation, and dynamic module loading framework for `nvmecontrol`.

Key behaviors:
- Maintains a top-level sorted singly linked list of commands.
- Constructor macros in `comnd.h` call `cmd_register()` before `main`.
- `cmd_dispatch()` selects subcommands by `argv[1]` and prints generated usage on missing/unknown command.
- `arg_parse()` builds `getopt_long()` tables from each command’s `struct opts`, writes parsed values directly to option storage, and handles positional `struct args`.
- Supports argument types for booleans, strings, paths, fixed-width unsigned integers, and size strings via `expand_number`.
- `cmd_load_dir()` loads `.so` modules from a directory with `dlopen(RTLD_NOW | RTLD_GLOBAL)`.

Research notes:
- Option storage uses direct pointers to global/static option fields; comments note future desire to use offsets/context objects.
- Numeric parsing uses `strtoul`/`expand_number` with upper-bound checks but limited malformed-string validation for some integer types.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/comnd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/comnd.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/comnd.h

Header for the `nvmecontrol` command framework.

Key contents:
- Defines `arg_type` enum for supported option/argument value types.
- Defines `struct opts`, `struct args`, and `struct cmd`.
- Provides `CMD_COMMAND` and `CMD_SUBCOMMAND` constructor macros.
- Declares command registration, dispatch, parsing, help, initialization, and module loading APIs.

Research notes:
- The framework is simple and plugin-friendly, but command option state is static/global rather than per-dispatch context despite `ctx_size` existing in `struct cmd`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/comnd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/connect.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/connect.c

Implements NVMe over Fabrics `connect` and `connect-all` commands.

Key behaviors:
- Supports TCP transport only.
- Parses address, SubNQN, controller ID, HostNQN, queue count, queue size, keep-alive timeout, reconnect delay, controller loss timeout, SQ flow control, and TCP header/data digests.
- `connect` establishes admin and I/O queues to a specific NVM subsystem, generates handoff parameters if needed, and hands queues to the kernel via `nvmf_handoff_host()`.
- `connect-all` connects to a discovery controller, fetches discovery log entries, filters for supported TCP/no-security entries, and connects to each advertised NVM subsystem.
- Hardcodes some association settings such as TCP `maxr2t = 1`.

Research notes:
- This is userland connection bootstrap for kernel-managed NVMe/TCP controllers.
- Unsupported transports, address families, and TCP security modes are skipped or rejected.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/connect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/devlist.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/devlist.c

Implements `nvmecontrol devlist`, listing NVMe controllers and namespaces.

Key behaviors:
- Scans controller unit numbers `0..256`.
- Opens controller devices, reads controller data, and prints model number.
- For fabrics controllers, queries connection status and reconnect parameters to show connected transport/address or disconnected duration.
- Lists active namespaces by repeatedly reading the active namespace list.
- Computes namespace size from `nsze * sector_size`.
- Supports `--human`/`-h` for human-readable sizes.

Research notes:
- Uses connection-status ioctls when available but assumes local/non-fabrics controllers are connected if unsupported.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/devlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/disconnect.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/disconnect.c

Implements NVMe over Fabrics disconnect commands.

Key behaviors:
- `disconnect` accepts controller ID, namespace ID, or SubNQN.
- If the argument is a valid NQN, passes it directly to `nvmf_disconnect_host()`.
- Otherwise opens the device, resolves the controller path/SubNQN via `get_nsid()`, and disconnects that host connection.
- `disconnect-all` calls `nvmf_disconnect_all()`.

Research notes:
- This file delegates actual disconnect logic to libnvmf/kernel interfaces.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/disconnect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/discover.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/discover.c

Implements `nvmecontrol discover` for NVMe over Fabrics discovery controllers.

Key behaviors:
- Supports TCP transport and optional HostNQN.
- Connects to the discovery admin queue using shared fabrics helpers.
- Optional `--verbose` prints discovery controller identify data.
- Fetches and prints the discovery log page.
- Decodes transport type, address family, subsystem type, SQ flow-control requirement, secure-channel requirement, port/controller IDs, NQN, transport address/service ID, and RDMA/TCP-specific fields.

Research notes:
- RDMA fields are decoded for display even though active connection support in this group is TCP-only.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/discover.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/fabrics.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/fabrics.c

Shared NVMe over Fabrics helper implementation used by connect and discover commands.

Key behaviors:
- Generates default HostNQN and hostid from host UUID.
- Parses address strings in forms including `host:port`, `IPv4:port`, `[IPv6]:port`, bare IPv6, and bare host.
- Parses controller IDs `dynamic`, `static`, or numeric static values.
- Resolves TCP endpoints with `getaddrinfo()`, opens sockets, and connects them for libnvmf qpairs.
- Connects to discovery admin queues, enables controller CC.EN, and waits for CSTS.RDY.
- Connects NVM admin queue, configures controller CC fields, waits ready, identifies controller, requests I/O queues, creates I/O qpairs, and handles cleanup on failures.
- Shuts down controllers by setting CC.SHN before freeing admin qpair.

Research notes:
- TCP is the only implemented transport path here.
- Connection setup preserves reserved controller configuration bits while clearing known fields.
- Error paths use sysexits-compatible return codes for callers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/fabrics.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/fabrics.h -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/fabrics.h

Header for shared NVMe over Fabrics command helpers.

Key contents:
- Declares address parsing, controller ID parsing, default HostNQN generation, discovery-log-entry initialization, discovery admin-queue connection, NVM queue connection, and queue disconnect helpers.
- Documents ownership for parsed address buffers via `tofree`.
- Documents that `connect_nvm_queues()` returns sysexits-style failure codes.

Research notes:
- This is the shared interface between user commands and lower-level libnvmf connection setup.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/fabrics.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/firmware.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/firmware.c

Implements `nvmecontrol firmware` for firmware image download and activation.

Key behaviors:
- Options include `--firmware`, `--slot`, and `--activate`.
- Validates slot range, required action, controller firmware support, slot read-only status, and slot count.
- Reads firmware image into memory with maximum size bounded by `INT32_MAX`.
- Downloads firmware in chunks based on controller max transfer size and FWUG granularity.
- Sends `FIRMWARE_IMAGE_DOWNLOAD` and `FIRMWARE_ACTIVATE` passthrough commands.
- Checks for reset-required activation status.
- Prompts the user for explicit `yes`/`no` confirmation before dangerous actions.

Research notes:
- Firmware changes are intentionally interactive and guarded.
- Assumes full file read after one `read()` and treats short reads as fatal.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/firmware.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/format.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/format.c

Implements `nvmecontrol format` for NVMe Format NVM and secure erase settings.

Key behaviors:
- Supports LBA format, metadata settings, protection information, protection information location, secure erase setting, user-data erase, and cryptographic erase.
- Ensures only one erase mode is selected.
- Resolves namespace device to controller device because Format NVM is an admin command.
- Checks controller support for format and cryptographic erase.
- Enforces controller limitations for per-namespace format/erase.
- Defaults unspecified namespace parameters from current namespace data; global format defaults to zero.
- Sends `NVME_OPC_FORMAT_NVM` passthrough command.

Research notes:
- No interactive confirmation appears in this file, unlike firmware; callers must treat it as destructive.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/format.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/identify.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/identify.c

Implements `nvmecontrol identify` command and namespace identify printing.

Key behaviors:
- Supports hex output, verbose full-table hex output, and explicit NSID override.
- Resolves namespace device to controller device before issuing admin identify commands.
- Prints controller identify data through `nvme_print_controller()` from `identify_ext.c`.
- Prints namespace data including size/capacity/utilization, thin provisioning, LBA formats, metadata capabilities, data protection, multipath/reservation capabilities, deallocate behavior, optimal I/O fields, NVM capacity, NGUID, EUI64, and per-format details.
- In non-verbose hex mode truncates output before reserved trailing fields.

Research notes:
- This file owns namespace human-readable formatting; controller formatting is separated into `identify_ext.c`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/identify.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/identify_ext.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/identify_ext.c

Provides `nvme_print_controller()`, the human-readable controller identify formatter shared by identify and discovery verbose output.

Key behaviors:
- Prints controller identity, serial/model/firmware strings, OUI, multipath capabilities, transfer limits, sanitize capabilities, controller type, keep-alive, max commands, and version.
- Prints admin command set attributes, firmware slots, error log entries, power states, NVM capacity, firmware update granularity, and host memory buffer sizes.
- Prints NVM command set attributes such as queue entry sizes, namespace count, supported I/O commands, fused operations, format attributes, volatile write cache, and NVM subsystem name.
- Prints fabrics attributes when present: capsule sizes, in-capsule data offset, controller model, max SGL descriptors, and disconnect support.

Research notes:
- This is display-only but depends heavily on NVMe bitfield macros for correct decoding.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/identify_ext.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/logpage.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/logpage.c

Implements `nvmecontrol logpage`, common log-page readers, built-in log-page formatters, and the log-page plugin registry.

Key behaviors:
- Registers `logpage` command with options for binary, hex, page ID, LSP, LSI, RAE, vendor formatter, and target device.
- Maintains a sorted SLIST of `struct logpage_function` entries populated by `NVME_LOGPAGE` constructor macros from core and vendor modules.
- Provides `read_logpage()` using `NVME_OPC_GET_LOG_PAGE` passthrough command with NUMD, RAE, LSP, LSI, LPO, CSI, OT, and UUID index fields.
- Supports raw binary output, hex output, or pretty printers.
- Built-in printers include error information, SMART/health, firmware slots, changed namespace list, command effects, reservation notification, sanitize status, and device self-test status.
- Computes variable error log size from controller `elpe`.
- Restricts namespace-level log access to per-namespace SMART when supported.

Research notes:
- Vendor modules extend this registry dynamically or at link/load time.
- Unknown log pages fall back to hex output with default size.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/logpage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/Makefile

Builds vendor-specific `nvmecontrol` module subdirectories.

Key contents:
- Subdirectories: `intel`, `micron`, `samsung`, `wdc`.
- Includes `bsd.subdir.mk`.

Research notes:
- These modules provide vendor log-page decoders loaded by the `nvmecontrol` plugin mechanism.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/Makefile.inc -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/Makefile.inc

Common Makefile settings for `nvmecontrol` vendor modules.

Key contents:
- Package: `nvme-tools`.
- Sets `NVMECONTROLDIR`.
- Disables install library metadata with `MK_INSTALLLIB=no`.
- Adds include path to the main `nvmecontrol` directory.
- Default shared library name is `${LIB}.so`.
- Installs modules under `/lib/nvmecontrol`.

Research notes:
- Shared modules rely on symbols exported by the main binary, matching `nvmecontrol/Makefile` use of `-rdynamic`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/intel/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/intel/Makefile

Builds the Intel `nvmecontrol` vendor module.

Key contents:
- `LIB=intel`.
- `SRCS=intel.c`.
- Includes `bsd.lib.mk`.

Research notes:
- Relies on module-wide common settings from the parent include path/build environment.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/intel/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/intel/intel.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/intel/intel.c

Vendor-specific Intel NVMe log-page formatter module.

Key behaviors:
- Formats Intel temperature statistics log.
- Formats Intel read and write latency histogram logs.
- Formats Intel additional SMART data log using key/value decoding and special handling for wear leveling, media wear, temperature, power, thermal throttle, and raw counters.
- Formats Intel drive marketing name log.
- Registers log pages via `NVME_LOGPAGE` for vendor name `"intel"`.

Research notes:
- Comments note that some SMART keys are shared by Samsung/Micron but may have model-specific meanings.
- Uses little-endian decode helpers for packed vendor log buffers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/intel/intel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/micron/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/micron/Makefile

Builds the Micron `nvmecontrol` vendor module.

Key contents:
- `LIB=micron`.
- `SRCS=micron.c`.
- Includes `bsd.lib.mk`.

Research notes:
- Simple module build definition.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/micron/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/micron/micron.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/micron/micron.c

Vendor-specific Micron NVMe SMART log formatter.

Key behaviors:
- Decodes vendor unique SMART log page `0xca`.
- Handles NAND writes/reads in GiB, thermal throttle status, temperature max/min/current, power consumption, power-loss protection, and generic key/value counters.
- Registers vendor log page under vendor name `"micron"`.

Research notes:
- Uses 12-byte SMART key records and stops after 150 bytes, matching the Intel-style additional SMART layout.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/micron/micron.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/samsung/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/samsung/Makefile

Builds the Samsung `nvmecontrol` vendor module.

Key contents:
- `LIB=samsung`.
- `SRCS=samsung.c`.
- Includes `bsd.lib.mk`.

Research notes:
- Simple shared-library module definition.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/samsung/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/samsung/samsung.c -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/samsung/samsung.c

Vendor-specific Samsung extended SMART log formatter.

Key behaviors:
- Defines packed `struct samsung_log_extended_smart`.
- Decodes the initial SMART key/value region, including program/erase fail counts, wear leveling, end-to-end errors, CRC errors, media wear, host read percentage, workload timer, thermal throttle, and lifetime write counters.
- Prints Samsung-specific extended fields including write amplification, lifetime user/NAND writes, lifetime reads, retired block count, current temperature, capacitor health, reserved erase blocks, read reclaim count, uncorrectable ECC count, reallocated blocks, power-on hours, power-off counts, and performance indicator.
- Registers page `0xca` under vendor `"samsung"`.

Research notes:
- Combines generic 12-byte SMART records with a larger Samsung-specific packed tail.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/samsung/samsung.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/wdc/Makefile -->
# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/wdc/Makefile

Builds the WDC `nvmecontrol` vendor module.

Key contents:
- `LIB=wdc`.
- `SRCS=wdc.c`.
- Includes `bsd.lib.mk`.

Research notes:
- The requested group includes only the Makefile, not `wdc.c`; behavior of the WDC module is therefore out of this file’s scope.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sbin/nvmecontrol/modules/wdc/Makefile -->