# Group Research: group_1514_plan9_sources_os_plan9_plan9_sys_src_cmd_cwfs_con_c_sources_os_plan_c31a37e51bdf

Scope checked: `Docs/research_subset_a.md` includes `sources/os/plan9/plan9`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/con.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/con.c

Console command dispatcher for the cached-WORM file server. It owns the in-memory command table, console flag table, initial console session setup, and many administrative commands exposed on the server console.

Key responsibilities:
- `consserve()` initializes command handlers, runs initial commands (`cfs`, `users`, `version`), optionally touches the cw superblock, then starts `consserve1`.
- `cmd_install()` and `flag_install()` append entries, sort them by command/flag name, and return bit flags for per-channel/global tracing.
- `cmd_exec()` tokenizes a single console command line into up to 10 argv slots and dispatches the matching command.
- Admin commands include `halt`, `sync`, `help`, `who`, `hangup`, `stats`, `stata`, `flag`, `cfs`, `version`, `profile`, `files`, `noattach`, `allow`, `disallow`, and user/file maintenance commands.
- File repair helpers include `walkto()`, `cmd_fstat()`, `cmd_create()`, `cmd_clri()`, `cmd_remove()`, `cmd_clean()`, `doclean()`, and `ckblock()`.
- `number()` parses signed integer strings into `vlong`, preserving support for large block numbers.

Important interactions:
- Uses console 9P wrappers from `console.c` (`con_attach`, `con_clone`, `con_walk`, `con_create`, etc.).
- Uses global `cons`, `chans`, `files`, `mainlock`, `mballocs`, `tagnames`, and permission toggles such as `wstatallow`, `writeallow`, `duallow`, `noattach`.
- Installs flags used elsewhere: `attachflag`, `chatflag`, `errorflag`, `whoflag`, `authdebugflag`, `authdisableflag`.

Research notes:
- The command table has fixed capacity (`command[100]`) and flag table fixed capacity (`flag[35]`, with hard limit `i >= 32` in `flag_install`).
- `cmd_time()` builds a command string from argv and measures elapsed time with `time(nil)`/`TK2MS`, but this server defines `HZ` as 1, so timing granularity is coarse.
- `cmd_clean()` can print and optionally rewrite direct or indirect block pointers in a file's `Dentry`; it refuses mutation on `Devro`.
- `walkto()` uses console fids `FID1` and `FID2`, clones from the current root, then walks slash-separated path components.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/con.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/config.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/config.c

Configuration parser and boot-time system initialization for cwfs. It parses compact device expressions, reads/writes the on-disk configuration block, supports interactive configuration commands, and provides copy/recovery utilities.

Key responsibilities:
- Parses device expressions through `iconfig()`, `config()`, `config1()`, and `cnumb()`.
- Device grammar supports:
  - `w`, `r`, `l` for wren, worm, labelled worm devices.
  - `c` for cache/worm devices.
  - `j` for jukebox devices.
  - `f` for fake WORM wrappers.
  - `o` for read-only side of last cw.
  - `p` for percentage partitions.
  - `x` for byte-swapping device wrappers.
  - `(...)`, `[...]`, `{...}` for concatenation, interleave, and mirror groups.
  - `<n-m>` numeric iterators.
- `devcmpr()` compares device trees structurally for mapping and identity checks.
- `map()` applies optional wren-to-file or wren-to-device mappings from `devmap`.
- `mergeconf()` parses the on-disk config text block, merging service name, filsys declarations, and filesystem parameter declarations.
- `cmd_printconf()` prints NVRAM config and active config block, suppressing obsolete `ip*` commands.
- `sysinit()` reads config, writes missing config parameters, compiles each `Filsys` device tree, initializes/reams/recovers devices, then optionally runs copy operations.
- `arginit()` implements interactive boot-time commands such as `config`, `nvram`, `filsys`, `ream`, `recover`, `service`, `copyworm`, `copydev`, `noauth`, `readonly`, and `resetparams`.

Copy/recovery utilities:
- `wormof()` handles fake-WORM special cases.
- `writtensize()` probes for last readable WORM block.
- `dowormcopy()` copies written WORM blocks from `main` to optional `output`.
- `dodevcopy()` copies one arbitrary configured device to another, bounded by smaller size.

Important interactions:
- Uses `nvrgetconfig()`/`nvrsetconfig()` for persistent config string storage.
- Reads/writes block 0 of `confdev` as `Tconfig`.
- Uses `Fspar fspar[]` to track compiled-in disk-layout parameters: `blocksize`, `daddrbits`, `indirblks`, `dirblks`, `namelen`.
- Calls `devream`, `devrecover`, `devinit`, `getbuf`, `settag`, `checktag`, and `querychanger`.

Research notes:
- This file preserves obsolete network config keywords to keep old config blocks parseable.
- If config parameters are absent, `sysinit()` writes defaults back into the config block and restarts config reading.
- `userabort()` is currently a stub returning 0, so long copy operations are not actually interruptible through that hook.
- The parser stores newly allocated `Device` nodes on `f.devlist`, but this list is used as an ownership/debug chain rather than a deallocation path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/config.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/console.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/console.c

Console-side wrappers around the 9P1 request handlers, plus console-only `fstat` and `clri` operations.

Key responsibilities:
- `fcall9p1()` validates a 9P1 request type, enters `mainlock`, runs the appropriate `call9p1[]` handler under the channel ref lock, and records an error in the reply.
- Provides simple helpers: `con_session`, `con_attach`, `con_clone`, `con_walk`, `con_open`, `con_read`, `con_write`, `con_remove`, `con_create`.
- `doclri()` forcibly clears a directory entry after checking parent and target phase conditions.
- `f_fstat()` prints a selected file's dentry fields, direct block list, indirect block pointers, qid, size, and times.
- `f_clri()` wraps `doclri()` as a console operation.
- `con_clri()` and `con_fstat()` call the custom console handlers directly under locks instead of going through `call9p1`.

Important interactions:
- Uses `9p1.h` `Fcall` and `call9p1[]`.
- Uses console-global `cons.uid` and `cons.gid` as an explicit "beyond ugly" side channel for `con_create`.
- Uses dentry/block functions: `getbuf`, `getdir`, `checktag`, `accessdir`, `freewp`, `freefp`.

Research notes:
- `doclri()` refuses read-only devices and requires a valid parent `Wpath`.
- `f_fstat()` is diagnostic output only; it does not pack a protocol stat reply.
- `con_read()`/`con_write()` return 0 on protocol error, making short read/write indistinguishable from error for callers unless they inspect command output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/console.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/cw.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/cw.c

Core cached-WORM device implementation. It manages the cache map, cache states, WORM dump copy, filesystem dumps, recovery, cw reaming, read-only dump roots, and cw-specific console diagnostics.

Key data:
- `struct Cw` is private runtime state for a `Devcw`: cache/worm/ro devices, dump cursor, copy counters, traversal state, path name buffer, and dump recursion flags.
- Cache entry states persisted on disk:
  - `Cnone`, `Cdirty`, `Cdump`, `Cread`, `Cwrite`, `Cdump1`, `Cerror`.
- Opcodes passed to `cwio()`:
  - `Oread`, `Owrite`, `Ogrow`, `Odump`, `Orele`, `Ofree`, plus `Onone`.

Key responsibilities:
- `cwinit1()` allocates `Cw`, installs commands (`dump`, `statw`, `cwcmd`), installs `ro` flag, and initializes child devices.
- `cwinit()` validates cache map bucket tags and updates cache time/known WORM size.
- `cwio()` is the central state machine for reads, writes, allocation growth, dump marking, release, and free operations.
- `dumpblock()` copies one pending `Cdump` cache block to WORM, with retry/reread logic and `wmax` updates.
- `cwgrow()` extends filesystem size by `ADDFREE` blocks, marks new blocks dirty in cache, and adds them to the free list.
- `cwfree()` decides whether freed cw blocks can return to the freelist.
- `cacheinit()` lays out and initializes cache header and bucket map on cache device.
- `cwream()` initializes a fresh cw filesystem with cache header, superblock, cw root, ro root, and initial dump-marked blocks.
- `cwrecover()` scans WORM superblock chain and rebuilds cache metadata from the last good dump.
- `cfsdump()` performs a filesystem dump: recursively copies dirty live tree blocks, updates cw and ro roots, appends date-named dump entries, writes a new superblock, updates cache header, rewalks active fids, and extends locks by dump duration.
- `cwrecur()` recursively walks `Tsuper`, `Tdir`, and indirect blocks to split dirty/written blocks into immutable dump blocks.
- `rewalk()`/`rewalk1()`/`rewalk2()` update active `File.addr` paths after dump root relocation.
- `roread()` reads from cache if the block is dump/read state, otherwise from WORM.
- Diagnostic/maintenance commands under `cmd_cwcmd()` include `mvstate`, `prchain`, `searchtag`, `touchsb`, `savecache`, `loadcache`, `morecache`, `blockcmp`, `startdump`, `allflag`, `storesb`, `acct`, `clearacct`, and `test`.

Important interactions:
- Depends heavily on `Cache`, `Bucket`, `Centry`, `Superb`, `Dentry`, `Wpath`, and tags from `portdat.h`.
- Uses generic block/device operations from `sub.c`.
- Uses directory traversal/allocation from `dentry.c`.
- Uses console helpers for `/adm/cache` save/load.
- `wormcopy()` in `main.c` repeatedly invokes `dumpblock()` for each cw filesystem.

Research notes:
- `oldcachefmt` changes cache-data address calculation; `-c` in `main.c` sets it to 0 for the newer layout.
- `Cdump1` is a fallback state when write-induced dump preservation fails.
- `isdirty()` treats indirect blocks conservatively: any cached non-`Cnone` indirect block may force recursion.
- `cfsdump()` writes both partial and final super/cache updates; it uses `Bimm` to force critical metadata writes.
- `storesb()` is a specialized repair helper with a hard-coded default block number (`4168344`) and sanity relationship checks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/cw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/cwfs/conf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/cwfs/conf.c

Generic old-cw build configuration.

Key responsibilities:
- Defines `fs_mktime` from `DATE`.
- Sets `startsb` for `main` to block `2`.
- `localconfinit()` sets cwfs-specific defaults:
  - `conf.nfile = 40000`
  - dumps enabled
  - `conf.firstsb = 13219302`
  - `conf.recovsb = 0`
  - `conf.nlgmsg = 100`
  - `conf.nsmmsg = 500`
- Exposes both `serve9p1` and `serve9p2` in `fsprotocol[]`.

Research notes:
- This variant is paired with `cwfs/dat.h`, which selects 16K blocks and 32-bit layout.
- `conf.firstsb` is preseeded to a specific superblock address, likely for an existing old-cw deployment.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/cwfs/conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/cwfs/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/cwfs/dat.h

Build-time data layout header for the generic old-cw variant.

Key responsibilities:
- Defines `RBUFSIZE` as `16*1024` unless already defined.
- Includes `32bit.h`, selecting 32-bit on-disk/address layout.
- Sets `FIXEDSIZE = 1`, assuming jukebox discs are uniform size.
- Includes shared `portdat.h`.
- Defines user-mode fake memory-bank structures:
  - `MAXBANK = 2`
  - `Mbank`
  - `Mconf`
  - external `mconf`.

Research notes:
- The comments emphasize `RBUFSIZE` cannot be runtime-variable because it shapes on-disk arrays such as freelist blocks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/cwfs/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/data.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/data.c

Static error and tag-name tables for cwfs.

Key responsibilities:
- Defines `errstr9p[MAXERR]`, mapping internal error codes to human-readable 9P/server messages.
- Defines `wormscode[0x80]`, mapping optical/SCSI WORM sense-like codes to text.
- Defines `tagnames[]`, mapping block tag constants to diagnostic names.

Important interactions:
- `errstr9p` is used by `console.c`/protocol code for chat/error output.
- `tagnames` is used by diagnostics in `iobuf.c`, `cw.c`, and `sub.c`.

Research notes:
- Some error strings are operationally specific to 9P1-era behavior (`wstat`, `attach`, `walk`, etc.).
- `tagnames` is conditional on `COMPAT32` for higher indirect tags.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/data.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/dentry.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/dentry.c

Directory entry and file block addressing helpers, including direct/indirect block mapping, readahead, and truncation.

Key responsibilities:
- `getdir()` returns the `Dentry` slot within an `Iobuf`.
- `accessdir()` updates access/modification times, mutator uid, qid version, and marks buffers dirty for non-read-only devices.
- `preread()` queues readahead requests using `Rabuf` and `raheadq`.
- `rel2abs()` maps a relative file block number to an absolute disk block, allocating direct or indirect blocks if a tag is supplied.
- `dbufread()` implements simple sequential read-ahead strategy.
- `dnodebuf()` and `dnodebuf1()` fetch a file data/dir block by relative block number.
- `indfetch()` reads/allocates indirect block entries.
- `ibbpow()` and `ibbpowsum()` compute indirect fanout powers.
- `dtrunclen()` truncates to an arbitrary length, preserving and zeroing the partial final block.
- `dtrunc()` truncates a file to zero, freeing indirect and direct blocks in reverse order.

Important interactions:
- Uses `NDBLOCK`, `NIBLOCK`, `INDPERBUF`, `BUFSIZE`, and tags from `portdat.h`.
- Calls allocation/free helpers `bufalloc()` and `buffree()` from `sub.c`.
- Readahead is consumed by `rahead()` in `main.c`.

Research notes:
- `rel2abs()` supports variable indirect depth based on `NIBLOCK`; if exhausted it prints that one deeper level is not implemented.
- `dtrunclen()` uses `Truncstate` to free in forward order for partial truncations, while full truncation keeps historical reverse freeing.
- `trunczero()` currently calls `dnodebuf(..., Tfile, ...)`, so truncating can allocate the last block to zero-fill it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/dentry.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/emelie/conf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/emelie/conf.c

Emelie deployment-specific cwfs configuration.

Key responsibilities:
- Defines `fs_mktime`.
- Sets `startsb` for `main` and `old` to `SUPER_ADDR`.
- `localconfinit()` sets:
  - `conf.nfile = 40000`
  - `conf.nodump = 1`, indicating jukebox is read-only
  - `conf.recovsb = 0`
  - `conf.nlgmsg = 100`
  - `conf.nsmmsg = 500`
- Exposes both `serve9p1` and `serve9p2`.

Research notes:
- A commented `conf.firstsb = 13219302` suggests shared lineage with the generic old-cw config but disabled here.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/emelie/conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/emelie/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/emelie/dat.h

Build-time data layout header for the Emelie variant.

Key responsibilities:
- Defines `RBUFSIZE` as 16K.
- Includes `32bit.h`.
- Sets `FIXEDSIZE = 1`.
- Includes shared `portdat.h`.
- Defines `Mbank`/`Mconf` fake memory-bank structures and `extern Mconf mconf`.

Research notes:
- Structurally matches `cwfs/dat.h`; behavioral differences are in `emelie/conf.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/emelie/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/fs/conf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/fs/conf.c

`fs` deployment-specific cwfs configuration using 4K blocks and 32-bit layout.

Key responsibilities:
- Defines `fs_mktime`.
- Sets `startsb` for `main` to `810988`, with comment noting a discontinuity before superblock `696262`.
- `localconfinit()` sets:
  - dumps enabled
  - `conf.dumpreread = 1`
  - `conf.firstsb = 0`
  - `conf.recovsb = 0`
  - `conf.nlgmsg = 1100`
  - `conf.nsmmsg = 500`
- Exposes both `serve9p1` and `serve9p2`.

Research notes:
- The larger large-message buffer count is annotated as for packets at 8576 bytes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/fs/conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/fs/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/fs/dat.h

Build-time data layout header for the `fs` variant.

Key responsibilities:
- Defines `RBUFSIZE` as 4K.
- Includes `32bit.h`.
- Sets `FIXEDSIZE = 1`.
- Includes shared `portdat.h`.
- Defines fake memory-bank structures `Mbank` and `Mconf`.

Research notes:
- This 4K block size changes all derived on-disk constants in `portdat.h`, including directory entries per block and indirect fanout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/fs/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/fs64/conf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/fs64/conf.c

64-bit cwfs configuration.

Key responsibilities:
- Defines `fs_mktime`.
- Sets `startsb` for `main` to block `2`.
- `localconfinit()` sets:
  - dumps enabled
  - `conf.dumpreread = 1`
  - `conf.firstsb = 0`
  - `conf.recovsb = 0`
  - `conf.nlgmsg = 1100`
  - `conf.nsmmsg = 500`
- `fsprotocol[]` exposes only `serve9p2`.

Research notes:
- The file explicitly comments that 64-bit file servers cannot correctly serve 9P1 because `NAMELEN` is too large.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/fs64/conf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/fs64/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/fs64/dat.h

Build-time data layout header for the `fs64` variant.

Key responsibilities:
- Defines `RBUFSIZE` as 8K.
- Includes `64bit.h`, selecting 64-bit on-disk/address layout.
- Sets `FIXEDSIZE = 1`.
- Includes shared `portdat.h`.
- Defines fake memory-bank structures `Mbank` and `Mconf`.

Research notes:
- The combination of 8K blocks and 64-bit offsets changes both maximum file size and protocol compatibility.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/fs64/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/fworm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/fworm.c

Fake WORM device wrapper implemented on top of a writable backing device.

Key responsibilities:
- `fwormsize()` reserves trailing blocks as a bitmap, returning usable WORM blocks.
- `fwormream()` initializes trailing bitmap blocks with `Tvirgo` tags and zeros them.
- `fworminit()` initializes the backing device.
- `fwormread()` checks the bitmap bit before reading; unread/unwritten blocks return error.
- `fwormwrite()` checks the bitmap bit before writing; already-written blocks return error, new writes set the bit and write backing data.

Important interactions:
- Uses `FDEV(d)` as wrapped device.
- Uses `BUFSIZE*8` bits per bitmap block.
- Uses reserved buffer flag `Bres` when accessing bitmap blocks.

Research notes:
- This wrapper simulates write-once behavior by tracking written blocks in a bitmap stored at the end of the underlying device.
- Bounds checks panic if logical block numbers exceed fake-WORM usable size.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/fworm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/io.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/io.h

SCSI support constants and `Target` structure declaration.

Key responsibilities:
- Defines controller/target limits:
  - `MaxScsi = 4`
  - `NTarget = 16`
  - `Maxnets = 8`
- Defines SCSI status codes such as `STok`, `STcheck`, `STblank`, `STtimeout`, `STharderr`, and others.
- Defines `Target`, containing:
  - `Scsi *sc`
  - controller/target identifiers
  - inquiry/sense buffers
  - qlock
  - id string
  - availability flag.

Research notes:
- Included by SCSI, jukebox, main, and memory/buffer code where SCSI target state or networking limits are needed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/iobuf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/iobuf.c

Hash/LRU buffer cache for filesystem blocks.

Key responsibilities:
- `getbuf()` looks up an `(Device*, addr)` buffer in a hash bucket, moves hits to the front, locks and maps the buffer, and reads from device on misses if `Brd` is set.
- Miss replacement selects the oldest unlocked, non-reserved entry in the hash line.
- Dirty victims are synchronously written before reuse.
- `syncblock()` writes at most one dirty block per hash line and reports whether more work remains.
- `sync()` repeatedly calls `syncblock()` up to `10*nhiob` passes.
- `putbuf()` handles immediate writes (`Bimm`), unmaps, and unlocks.
- `checktag()` validates the block trailer tag and qpath, flushing invalid clean buffers from cache and warning on mismatch.
- `settag()` writes tag and qpath into the block trailer and marks modified.
- `iobufql()` diagnoses whether a `QLock` belongs to a cached buffer.

Important interactions:
- Uses `devread`/`devwrite` dispatch from `sub.c`.
- `Bres` prevents replacement of pseudo/reserved buffers that may recursively call buffer-cache code.
- `checktag()` calls `cwfree()` when a bad tag is found on a `Devcw` block.

Research notes:
- The hash function mixes block address with the `Device*` pointer.
- `getbuf()` loops until it can lock and map a stable matching buffer; this handles races where a buffer is reused between lookup and lock.
- `checktag()` returns `2` for tag mismatch, `0` for accepted path mismatches in one branch, and `0` for success, matching existing caller expectations rather than normal boolean style.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/iobuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/juke.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/juke.c

HP optical-disc jukebox and WORM side driver. It manages robotic media movement, side discovery, labelled WORM validation, read/write I/O through sd data files, and console jukebox operations.

Key data:
- `Side` tracks one disc side: element number, loaded drive, status, rotation/backside, ordinal label, timing, native block geometry, and Plan 9 block capacity.
- `Juke` tracks robotics, sides, drives, SCSI geometry, fixed-size mode, offline drives, robot handle, and global jukebox list.

Key responsibilities:
- `querychanger()` opens robotics via `openscsi`, registers SCSI target, reads changer geometry, builds side table, reads positions, and initializes drive table.
- `jukeinit()` attaches changer and drive devices, installs console commands, and assigns `Juke*` private pointers to side devices.
- `geometry()` reads SCSI mode pages for element address assignment and transport geometry.
- `positions()`/`element()` read element status and move any discs found in drives back to shelves.
- `wormunit()` ensures a requested side is loaded, spinning/ready, and has known geometry.
- `wormlabel()` validates or writes labelled-WORM label blocks and checks ordinal matches.
- `wormsize()` returns side capacity, hiding the label block for `Devlworm`.
- `wormsizeside()` and `wormsidestarts()` compute side sizes/start offsets in composite device trees.
- `wormread()` and `wormwrite()` perform block I/O to the loaded drive fd.
- `bestdrive()` selects a drive, preferring empty drives or the other side of the same platter, otherwise unloading an old side.
- `wormprobe()` periodically unloads inactive sides.
- Console commands include `wormreset`, `wormeject`, `wormingest`, `wormoffline`, and `wormonline`.

Important interactions:
- Uses SCSI helpers from `scsi.c` for robotics commands (`move medium`, `mode sense`, `read element status`).
- Uses `sdof()`, `inqsize()`, `dataof()`, and normal file I/O for drive data paths.
- Label format is `Label` from `portdat.h`, using `Labmagic`.

Research notes:
- The code supports double-sided media via `rot` and duplicates side entries offset by `nse`.
- `FIXEDSIZE` lets a deployment assume all discs are same size to avoid expensive probing.
- `wormlabel()` may offer to write a new label if the label block is unreadable or magic is bad.
- `wormwrite()` has a typo in an error string (`wormwrwite`) but behavior is unaffected.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/juke.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/lrand.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/lrand.c

Thread-safe pseudo-random number generator.

Key responsibilities:
- Implements the D. P. Mitchell and J. A. Reeds lagged Fibonacci-style generator.
- `isrand()` initializes state using Park-Miller parameters.
- `srand()` seeds under a lock.
- `lrand()` lazily initializes if needed, advances tap/feed pointers, stores the new value, and returns a 31-bit positive `long`.

Research notes:
- Uses a global `Lock lk`, so calls are serialized.
- `NORM` is defined but unused in this file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/lrand.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/main.c

User-mode cwfs entry point, process setup, memory/config initialization, server loops, readahead worker, dump worker, sync worker, and utility functions.

Key responsibilities:
- Provides console output helpers (`puts`, `putstrn`, `prflush`), `panic()`, and `okay()`.
- `mapinit()` reads a device map file mapping source device expressions to files or alternate devices.
- `confinit()` sets default resource sizes, calls `localconfinit()`, derives `nwpath`, `nauth`, and `gidspace`, and loads device mappings.
- `maxsize()` computes maximum representable file size from direct/indirect fanout with overflow checks.
- `printsizes()` reports block size, max file size, indirect fanout, cache bucket entries, and structure sizes.
- `main()` parses flags:
  - `-a` announce address
  - `-c` new cache layout
  - `-f` configure first
  - `-m` device map
  - one required config-device expression.
- Initializes queues, message buffers, networking, SCSI, file table, path table, uid/gid tables, auth, iobufs, config, system devices, and worker processes.
- `rahead()` consumes sorted readahead requests and warms block cache.
- `serve()` receives network 9P messages, detects protocol, dispatches protocol handlers, and frees messages.
- `exit()` marks active exiting, prints halt time, posts a note to process group, exits.
- `nextdump()` computes next automatic dump time.
- `wormcopy()` periodically copies pending dump blocks and triggers scheduled automatic dumps.
- `synccopy()` continuously flushes dirty blocks.
- `inqsize()` reads sd ctl geometry to discover sector size.

Important interactions:
- Uses configuration defaults from variant `conf.c`.
- Starts `netstart()`, `serve()`, `rahead()`, `wormcopy()`, `consserve()`, then runs `synccopy()` in the main process.
- Uses `fsprotocol[]` to sniff incoming protocol.

Research notes:
- The program is user-mode but uses old file-server architecture concepts: workers, queues, channels, and server-wide locks.
- `conf.mem = meminit()` uses available user memory estimates from `pc.c`; `iobufinit()` consumes most of it for block buffers.
- `serve()` only calls `cp->protocol(mb)` in the `else` branch after a protocol is already set. On the packet that first detects a protocol, it sets the protocol but does not dispatch in that same branch.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/malloc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/malloc.c

Permanent allocation and buffer-cache memory initialization.

Key responsibilities:
- `ialloc()` wraps `mallocalign`, panics on failure, and zeros memory.
- `prbanks()` prints fake memory bank ranges.
- Installs `memory` console command via `cmd_memory()`.
- `iobufinit()`:
  - Computes total configured memory from `mconf.bank`.
  - Derives number of `Iobuf`s and hash buckets.
  - Allocates `Hiob` hash headers, `Iobuf` array, and contiguous raw buffer storage.
  - Initializes per-buffer qlocks and circular LRU lists per hash bucket.
  - Marks memory as consumed and prints remaining memory.
- `iobufmap()` maps an `Iobuf` by assigning `xiobuf` to `iobuf`.
- `iobufunmap()` marks `iobuf` invalid with `(char*)-1`.

Research notes:
- `HWIDTH = 8` targets eight buffers per hash chain.
- `nhiob` is adjusted upward to a prime number.
- This user-mode version does not actually map/unmap physical memory; mapping is pointer assignment.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/malloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/mworm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/mworm.c

Composite block-device implementations: concatenation, interleaving, partitions, and mirroring.

Key responsibilities:
- `mcat*` implements concatenated devices:
  - initializes children and stores child list.
  - size is sum of child sizes.
  - read/write selects child by cumulative range.
- `mlev*` implements interleaved/striped devices:
  - size is `n * min(child_size)`.
  - read/write dispatches by `b % n` and `b / n`.
- `part*` implements percentage-based partitions:
  - base and size are percentages of parent size.
  - size 0 means remainder/all 100%.
- `mirr*` implements mirrors:
  - size is minimum child size.
  - reads try children until one succeeds.
  - writes recursively write later mirrors first, then earlier/main device.

Important interactions:
- Uses generic `devinit`, `devsize`, `devread`, `devwrite` recursion.
- `Device.cat` union is shared by mcat, mlev, and mirror.

Research notes:
- Mirror write ordering is deliberate: mirrors are written before the main device so a power loss with main updated implies mirrors should already be updated.
- `mirrread()` reports failure only if every mirror read fails.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/mworm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/net.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/net.c

User-mode network transport for 9P messages over Plan 9 network connections.

Key data:
- `Network` tracks listener state for an announce string.
- `Netconn` is per remote address/channel allocation state and reply queue pointer.
- `Conn9p` is per accepted connection fd, with ref count, remote address, and backpointer to `Netconn`.

Key responsibilities:
- `netinit()` announces configured addresses (`annstrs`, default `tcp!*!9fs`).
- `netstart()` starts one network output process and one input listener per configured network.
- `neti()` accepts connections and forks `connection()` processes.
- `connection()` reads 9P messages from one fd, allocates `Msgbuf`s, assigns channel/protocol metadata, and sends to `serveq`.
- `neto()` receives reply `Msgbuf`s from `netoq` and writes them back to the original connection fd.
- `getchan()` reuses or allocates a `Chan` for a remote address, sets send/reply queues and channel metadata.
- `nethangup()` and `chanhangup()` tear down channels/connections and free active fids.
- `size9pmsg()` and `readalloc9pmsg()` frame 9P2000-style messages by 32-bit length.

Important interactions:
- Uses `fs_chaninit`, `fileinit`, `mballoc`, `mbfree`, `fs_send`, `fs_recv`.
- Relies on `Msgbuf.param` to carry `Conn9p*` for replies.
- Uses `getnetconninfo()` to discover remote address.

Research notes:
- The file comments document a major architecture shift from kernel Ethernet/IL packet processing to user-mode per-connection stream processing.
- Connections are grouped by remote address when choosing a `Chan`, which can multiplex sessions from the same caller.
- `Conn9p` references are incremented for both live connection and in-flight packets, then decremented in output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/net.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/pc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/pc.c

User-mode platform support for memory estimation and process creation.

Key responsibilities:
- Defines global `Mconf mconf`.
- `mconfinit()` reads `#c/swap` to estimate available user memory; defaults to 64 MB if unavailable.
- Builds one fake memory bank starting at `0x10000000`.
- `meminit()` initializes memory config and returns memory size.
- `procsetname()` writes process name text to `#p/<pid>/args`.
- `newproc()` forks with `RFPROC|RFMEM|RFNOWAIT`, sets child process name, calls the provided function, and exits if it returns.

Research notes:
- The fake memory-bank abstraction preserves old kernel-file-server allocation patterns in user mode.
- `newproc()` shares memory (`RFMEM`), so global locks and queues coordinate all worker processes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/pc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/portdat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/portdat.h

Central shared data-layout, constants, type declarations, global state, and device/tag/error enumerations for cwfs.

Key contents:
- Fundamental on-disk constants:
  - `SUPER_ADDR = 2`
  - `ROOT_ADDR = 3`
- Fundamental types:
  - `Wideoff`, `Userid`, `Timet`, `Devsize`.
- Derived layout constants:
  - `BUFSIZE = RBUFSIZE - sizeof(Tag)`
  - `DIRPERBUF`, `INDPERBUF`, `FEPERBUF`
  - message buffer sizes
  - cache bucket sizing constants.
- On-disk structures explicitly marked "DONT TOUCH":
  - `Tag`
  - `Qid9p1`
  - `Super1`
  - `Centry`
  - `Dentry`
  - `Fbuf`
  - `Superb`
  - `Cache`
  - `Bucket`
  - `Label`.
- Runtime structures:
  - `Queue`, `Device`, `Chan`, `Filsys`, `Startsb`, `Time`, `Tlock`, `Cons`, `File`, `Wpath`, `Iobuf`, `Uid`, `Conf`, `Msgbuf`, `Command`, `Flag`, `Rtc`, `Truncstate`, `Map`.
- Enumerations:
  - message categories
  - process states
  - devnone pseudo block numbers
  - internal error codes
  - device types
  - block tags
  - `getbuf` flags.
- Defines global instances `Conf conf; Cons cons;`.
- Vararg format pragmas for `%Z`, `%T`, `%I`, `%E`, `%G`.

Important interactions:
- Included by variant `dat.h` files after block size/address width choices are made.
- `Device` union is the backbone for every storage backend.
- Block tag ordering is important; comments note indirect-tag order is exploited by `indirck()` and `isdirty()`.

Research notes:
- The file is disk-layout critical: changing structures or derived constants changes on-disk compatibility.
- `COMPAT32` changes tag assignments for directory and indirect tags.
- `NDBLOCK`, `NIBLOCK`, `NAMELEN`, and `Off` width are imported from `32bit.h`/`64bit.h`, so this file adapts to multiple build variants.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/portdat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/portfns.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/portfns.h

Shared function prototype header for cwfs.

Key contents:
- Prototypes for:
  - auth operations
  - config parsing and device lifecycle
  - console commands and console 9P wrappers
  - cwfs/cached-WORM operations
  - dentry/block allocation/truncation
  - network setup
  - message buffers and queues
  - jukebox/SCSI/WORM operations
  - uid/gid/user commands
  - time/format/random helpers
  - process/locking/platform helpers
- External declarations:
  - `annstrs`
  - `bin`
  - `devmap`
  - `fsprotocol[]`.

Research notes:
- This header gives a concise cross-reference map of cwfs subsystem boundaries.
- It exposes both low-level device APIs (`wrenread`, `wormwrite`, `mcatread`, etc.) and high-level filesystem/admin APIs (`cfsdump`, `cmd_users`, `cmd_check`).
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/portfns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/scsi.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/scsi.c

SCSI command wrapper over Plan 9 `scsi(2)`/`sd(3)` interfaces.

Key responsibilities:
- `scsiinit()` initializes controller/target table, locks, IDs, and inquiry/sense buffers.
- `doscsi()` sends a command via `scsi()`, and on failure issues request-sense via `scsicmd()`.
- `sense2stcode()` maps sense bytes to internal `ST*` status codes.
- `scsiexec()` records failed commands for diagnostics.
- Command helpers: `scsitest`, `scsistart`, `scsiinquiry`, `scsireqsense`.
- `scsiprobe()` tests, spins up if needed, requests sense, runs inquiry, and marks target ok.
- `scsiio()` locks/probes target, retries commands up to 10 times, handles blank reads by zero-filling, and returns status.
- `newscsi()` connects an opened `Scsi*` handle to a `Target`.

Important interactions:
- Used by `juke.c` for robotics commands.
- Device target selection comes from `Device.wren.ctrl`, `.targ`, and `.lun`.

Research notes:
- The comments note that LUNs are not implemented in sd(3), but the code still carries LUN bits in SCSI commands.
- `lastcmd`/`lastcmdsz` are diagnostic globals for failed request-sense output.
- `scsiverbose` is set externally to 1 in `scsiinit()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/scsi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/sub.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/sub.c

Large utility and dispatch module for cwfs. It contains filesystem lookup helpers, fid/path management, permissions, freelist allocation, formatting, queue/message buffers, generic device dispatch, reaming/recovery, and byte swapping.

Key responsibilities:
- Filesystem/channel/fid helpers:
  - `fsstr()`, `dev2fs()`, `fs_chaninit()`, `fileinit()`, `filep()`, `newfp()`, `freefp()`.
- Permissions and locks:
  - `iaccess()` implements owner/group/other/superuser checks.
  - `tlocked()` allocates/checks timed file locks.
  - `newwp()` and `freewp()` manage `Wpath` reference chains.
- Allocation/free:
  - `qidpathgen()` increments superblock qid generator.
  - `buffree()` recursively frees direct/indirect blocks and updates freelist, respecting cw written-block rules.
  - `bufalloc()` pops from free list, grows cw if full, clears/tag-initializes allocated blocks.
  - `addfree()` pushes blocks to freelist, spilling to `Tfree` blocks as needed.
- Formatting:
  - `%Z` formats device trees.
  - `%G` formats block tags.
  - `formatinit()` installs formatters.
- Filesystem initialization:
  - `rootream()` writes root directory block.
  - `superream()` writes superblock and free list.
- Message buffers and queues:
  - `mbinit()`, `mballoc()`, `mbfree()`.
  - `fs_recv()`, `fs_send()`, `newqueue()`.
- Generic device operations:
  - `devread()`, `devwrite()`, `devsize()`, `sdof()`, `superaddr()`, `getraddr()`, `devream()`, `devrecover()`, `devinit()`.
- Byte swapping:
  - `swab2()`, `swab4()`, `swab8()`, and `swab()` for tagged block types.

Important interactions:
- Central dispatch point for all `Device.type` implementations.
- `devwrite()` honors global `readonly` by returning success without writing, mainly for experiments.
- `swab()` knows every on-disk structure and tag type that needs endian conversion.

Research notes:
- `tlocked()` appears to have a suspicious condition: `if(t1 != nil && t->time == 0) t1 = t;` means it never records a free lock while `t1` is nil. Existing behavior may intentionally simulate lock exhaustion, but the code comment suggests free-lock reclamation is expected.
- `mbfree()` sets `mb->magic = 0` after checking it; `mballoc()` restores `Mbmagic`.
- `fs_send()` waits briefly for a reader (`waitedfor`) and aborts if none appears, treating send-before-reader as a bug.
- `devream()` recursively reams child devices, then writes root/super for top-level non-cw devices or calls `cwream()` for cw.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/sub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/time.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/time.c

Time formatting, dump scheduling time computation, and delay wrapper.

Key responsibilities:
- `toytime()` returns `time(nil)`.
- `datestr()` formats a timestamp as `yyyymmdd`.
- `prdate()` prints current time with `%T`.
- `Tfmt()` formats `Timet` into Plan 9-style textual time.
- `nextime()` computes the next timestamp after `t` at a target hour and not on excluded weekdays.
- `delay()` wraps `sleep()` in milliseconds.

Research notes:
- `Tfmt()` prints `The Epoch` for zero time.
- `nextime()` includes adjustment logic for localtime/DST hour anomalies.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/time.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/uidgid.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/uidgid.c

User/group table parsing, lookup, and console editing for `/adm/users`.

Key responsibilities:
- Defines minimal built-in users/groups in `minusers`.
- `cmd_users()` reads `/adm/users` or installs defaults with `default`.
  - First pass parses uid/name rows.
  - Sorts `uid[]` by uid.
  - Second pass parses leaders and group members into `gidspace`.
- `cmd_newuser()` and `do_newuser()` support console operations:
  - create user
  - create group
  - show entry
  - rename
  - set/remove leader
  - add/delete group member
  - rewrite `/adm/users`
  - optionally create `/usr/<name>` for low-numbered users.
- Lookup/conversion helpers:
  - `chkuid()`, `pentry()`, `setminusers()`, `uidpstr()`, `getword()`, `strtouid()`, `uidtop()`, `uidtostr()`.
- Authorization helpers:
  - `ingroup()`
  - `leadgroup()`
  - `byuid()`.
- File reading helpers:
  - `fchar()` reads buffered chunks through console fid.
  - `readln()` reads one logical line.

Important interactions:
- Uses `uidgc.uidlock` for read/write locking around uid table accesses.
- Uses console file operations (`walkto`, `con_open`, `con_read`, `con_write`) to access `/adm/users`.
- Uses global arrays `uid` and `gidspace` allocated in `main.c`.

Research notes:
- User names reject characters in `"?=+-/:"`.
- `strtouid()` returns `-2` for unknown user; other callers often interpret `-1` specially for adm.
- `cmd_users()` requires `conf.nuid` and `conf.gidspace` to be large enough; it prints diagnostics but continues where possible.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/uidgid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/wren.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/wren.c

Normal disk/file-backed block device backend.

Key responsibilities:
- `dataof()` maps a directory path to `<dir>/data`, otherwise duplicates the file path.
- `wreninit()` opens the underlying `/dev/sdXX/data` or mapped file, determines native block size via `inqsize()`, computes native sector count and cwfs block count.
- `wrensize()` returns logical cwfs block count.
- `wrenread()` reads one `RBUFSIZE` block via `pread`.
- `wrenwrite()` writes one `RBUFSIZE` block via `pwrite`.

Important interactions:
- `sdof()` builds `/dev/sd<ctrl><target>` paths for unmapped devices.
- Error counters `cons.nwrenre` and `cons.nwrenwe` are incremented on I/O failures.

Research notes:
- If geometry block size is absent or implausible, it falls back to 512-byte sectors.
- Logical block addressing uses byte offset `b * RBUFSIZE`, independent of native sector multiplier once size is computed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cwfs/wren.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/date.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/date.c

Small Plan 9 `date` command.

Key responsibilities:
- Parses flags:
  - `-n` prints numeric seconds since epoch.
  - `-u` prints UTC via `gmtime()`/`asctime()`.
- Optional single positional argument is parsed as seconds with `strtoul`.
- Without an argument, uses current `time(0)`.
- Default output uses local `ctime()`.

Research notes:
- If both `-n` and `-u` are supplied, numeric output wins because `nflg` is checked first.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/date.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/command.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/db/command.c

Command decoder for the Plan 9 `db` debugger.

Key responsibilities:
- Maintains command state globals: `dot`, `dotinc`, address/count flags, last command, format defaults, and `ditto`.
- `command()` parses an optional address expression, optional count, command verb, and semicolon-separated command list.
- Supported command verbs include:
  - `/`, `?`, `=` for memory/text/literal examination.
  - `>` to assign `dot` to a register.
  - `!` shell escape.
  - `$` trace/status commands.
  - `:` process control commands.
- `acommand()` handles examine/search/write subcommands:
  - `m` map print
  - `l`/`L` source search by 2/4-byte value
  - `w`/`W` write 2/4-byte values
  - otherwise format scan via `scanform()`.
- `cmdsrc()` scans mapped memory for masked 2-byte or 4-byte values.
- `cmdwrite()` writes values to a map and prints before/after-style output.
- `regname()` collects alphanumeric register names.
- `shell()` runs `/bin/rc -c` on the rest of the input line.

Important interactions:
- Uses expression parser from `expr.c`, input from `input.c`, and format execution from `format.c`.
- Uses `Map` operations from libmach helpers (`get2`, `get4`, `put2`, `put4`).
- Process execution commands delegate to `subpcs()`.

Research notes:
- `command()` saves and restores input state when executing a passed-in buffer, enabling recursive command execution.
- `executing` prevents nested `:` process-control execution.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/command.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/defs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/db/defs.h

Common definitions and global declarations for the Plan 9 `db` debugger.

Key contents:
- Includes Plan 9 C, libc, bio, ctype, and mach headers.
- Defines core types:
  - `WORD` as `ulong`
  - `ADDR` as `uvlong`
  - `BOOL` as `int`.
- Defines limits and constants: `MAXOFF`, `INCDIR`, `DBNAME`, `CMD_VERBS`, line/argument/symbol sizes, truth values.
- Defines run modes and breakpoint states.
- Defines `BKPT` structure for breakpoints.
- Declares global debugger state:
  - expression/address/count values
  - dot/dotinc
  - symbol/core file paths and fds
  - process state
  - maps
  - breakpoint list
  - input chars.
- Includes `BADREG` and note handling limits.

Research notes:
- This header is intentionally broad and shared across all `db` modules.
- `CMD_VERBS` is used by input parsing to distinguish file references from command syntax.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/defs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/expr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/db/expr.c

Expression parser for the Plan 9 `db` debugger.

Key responsibilities:
- Parses expressions using recursive routines:
  - `expr()` handles dyadic operators.
  - `term()` handles unary operators and parenthesized expressions.
  - `item()` handles symbols, locals, numbers, dot, registers, file references, character constants, and ditto.
- Supported dyadic operators include `+`, `-`, `#` rounding, `*`, `%`, `&`, `|`.
- Supported unary operators include memory indirection through core map (`*`), symbol map (`@`), negation, bitwise complement, and parentheses.
- `item()` resolves:
  - `file:line` references via `file2pc`.
  - global symbols via `lookup`.
  - local symbols via `localaddr`.
  - current function locals from current PC.
  - `<register` via `rget`.
  - quoted character constants.
- `getnum()` parses numeric constants with base prefixes:
  - `#` for hex
  - `0x` hex
  - `0t` decimal
  - `0o` octal
  - default decimal or leading-zero octal.
- `readsym()` and `readfname()` collect UTF-aware symbol/file tokens.
- `symchar()` defines symbol character rules.
- `round()` implements `#` operator rounding.

Important interactions:
- Uses `lastc`/`readchar()`/`reread()` from `input.c`.
- Uses libmach symbol/local APIs and register map callbacks.

Research notes:
- Floating literals are accepted if a dot appears during number parsing; they are converted to a `float` bit pattern stored in `WORD`.
- Division by zero is handled specially: nonzero numerator yields 1, zero numerator yields 0.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/expr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/db/fns.h

Function prototype header for Plan 9 `db`.

Key contents:
- Declares debugger command, expression, formatting, input, output, process-control, symbol, register, map, breakpoint, and setup functions.
- Includes vararg checking for `dprint`.
- Exposes interfaces split across files not all in this group, including `pcs.c`, `runpcs.c`, `setup.c`, `regs.c`, and output/print modules.

Research notes:
- Useful as the module dependency map for `db`: command parsing, expression parsing, and formatting files in this group call many functions declared here but implemented elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/format.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/db/format.c

Format-string executor for Plan 9 `db` examine commands.

Key responsibilities:
- `scanform()` repeats a full format string for a count, preserving and incrementing `dot`.
- `exform()` executes one format item `fcount` times and advances `dot`.
- Supports address/symbol output formats:
  - `a`, `A`, `p`.
- Supports numeric formats:
  - 16-bit `u d x o q`
  - 32-bit `U D X O Q`
  - 64-bit `Z V Y`.
- Supports byte/char/rune/string formats:
  - `B b c C r R s S`.
- Supports disassembly/instruction formats:
  - `i`, `I`, `M`.
- Supports float formats:
  - `f`, `F`.
- Supports spacing/control:
  - spaces/tabs, `t`, `T`, `n`, `N`, quoted strings, `^`, `+`, `-`, `z`.
- `printesc()` prints escaped non-printable chars.
- `inkdot()` increments `dot` with wraparound detection.

Important interactions:
- Uses `machdata` hooks for disassembly and floating formatting.
- Uses `get1`, `get2`, `get4`, `get8` for memory reads from `Map`.
- Uses `symoff`, `findsym`, and `printsource`.

Research notes:
- On the first pass, instruction formats warn if `dot` is not aligned to `mach->pcquant`.
- Literal mode treats `dot` as the value rather than reading from a map.
- Comments note `f` and `F` literal cases assume `szdouble` fits in a `vlong`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/format.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/input.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/db/input.c

Input buffering and character/rune reading for Plan 9 `db`.

Key responsibilities:
- Maintains global input line buffer `line`, rune pointer `lp`, `peekc`, `lastc`, and `eof`.
- `eol()` recognizes newline and semicolon as command terminators.
- `rdc()` reads next non-space/tab character.
- `reread()` pushes back one character through `peekc`.
- `clrinp()` flushes output and resets input pointer/peek char.
- `readrune()` reads one UTF rune from a file descriptor.
- `readchar()` reads from current line buffer or fills it from `infile`, supporting backslash-newline continuation and interrupt faults.
- `nextchar()` returns next command argument char or 0 at EOL.
- `quotchar()` reads quoted character literal content.
- `getformat()` collects an examine format string, respecting quoted substrings.
- `isfileref()` looks ahead to detect `filename:digits` forms so expression parsing can treat them as file locations.

Important interactions:
- Used by `command.c` and `expr.c`.
- `mkfault` interrupts force `error(0)` during input fill.

Research notes:
- Line input is UTF-aware through `Rune` storage and `runetochar` conversion in callers.
- `getformat()` steps `lp--` after reading terminator so the command loop can see it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/input.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/db/main.c

Main command loop, argument handling, and error/interrupt recovery for Plan 9 `db`.

Key responsibilities:
- Parses flags:
  - `-k` kernel mode
  - `-w` open core writable
  - `-I dir` include/source path
  - `-m machine` machine override.
- Determines `symfil` and `corfil` from optional symbol file and optional pid.
- For a pid without explicit symfile:
  - non-kernel uses `/proc/<pid>/text`.
  - kernel mode guesses kernel path from `$cputype` and `$terminal`.
  - core file is `/proc/<pid>/mem`.
- Initializes output, symbols, `dotmap`, machine selection, and optional core mapping.
- Main loop:
  - prints pending error messages.
  - handles interrupts.
  - reads a command.
  - exits on EOF from stdin.
  - executes command and enforces newline.
- `done()` exits, ending active process control if needed.
- `error()` stores an error message, closes input/output, flushes, deletes breakpoints, and longjmps to the main loop.
- `errors()` formats a two-part error.
- `fault()` handles interrupt notes by seeking current input to EOF and setting `mkfault`.

Important interactions:
- Uses `setjmp`/`longjmp` for debugger error recovery.
- Uses setup functions (`setsym`, `setcor`, `dumbmap`) and process-control cleanup (`delbp`, `endpcs`) declared in `fns.h`.

Research notes:
- `xargc` is retained as a global compatibility variable.
- If `-m` names an unknown machine, it reports but continues with default machine.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/db/main.c -->