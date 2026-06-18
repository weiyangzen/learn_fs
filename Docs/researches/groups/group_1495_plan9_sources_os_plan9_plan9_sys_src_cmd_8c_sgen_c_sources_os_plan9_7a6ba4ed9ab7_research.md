# Group Research: group_1495_plan9_sources_os_plan9_plan9_sys_src_cmd_8c_sgen_c_sources_os_plan9_7a6ba4ed9ab7

Scope confirmed against `Docs/research_subset_a.md`: all files are under included source tree `sources/os/plan9/plan9`. I read every listed source file completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/sgen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/sgen.c

Purpose: 386 C compiler backend expression addressability and complexity analysis.

Key behavior: `xcom` recursively annotates AST nodes with `addable` classes and register complexity, folds address arithmetic, rewrites power-of-two multiply/divide/modulo into shifts/masks, and normalizes compare/immediate operands. `indexshift` and `indx` recognize x86 scaled-index forms. `noretval` emits pseudo uses for integer/FPU return registers.

Integration notes: feeds code generation in `txt.c`/`cgen.c`; its `addable` values are consumed by `naddr`, `gins`, and indexed addressing setup. Important edge cases are side-effect avoidance before forming `OINDEX`, 64-bit expression handling via `com64`, and register-pressure estimates for calls and division.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/sgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/swt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/swt.c

Purpose: 386 C compiler support routines for switches, bitfields, object output, history records, and ABI alignment.

Key behavior: `swit1` emits linear or binary-search switch compare/jump chains. `bitload`/`bitstore` extract and update C bitfields. `outstring`, `gextern`, `outcode`, `zname`, and `zaddr` serialize compiler `Prog` streams and symbol references into Plan 9 object format. `outhist` writes source-history records. `align` and `maxround` implement 386 stack/struct/argument layout.

Integration notes: object encoding here is decoded by `8l/obj.c`; changes to `zaddr`/symbol table caching must remain compatible with linker `zaddr`. Alignment decisions drive generated ABI layout and stack frame sizes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/swt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/txt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/txt.c

Purpose: main 386 C compiler text/code emission layer.

Key behavior: `ginit` initializes target identity, pseudo nodes, register state, type widths, and 64-bit support; `gclean` emits globals and final `AEND`. Register helpers allocate/free integer, FPU, and register-pair nodes. `naddr` converts AST address nodes into 8.out operands. `gmove`, `fgopcode`, and `gopcode` map C operations/conversions to 386/x87 instructions. `gins`, `gbranch`, `patch`, and `gpseudo` create instruction records.

Integration notes: consumes `xcom`/`OINDEX` state from `sgen.c`, serializes via `swt.c`, and relies on `8.out.h` opcodes recognized by `8l`. High-risk areas are x87 rounding-control conversion sequences, unsigned integer/float conversions, stack temporary allocation, and `idx` global use for indexed operands.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8c/txt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8l/asm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8l/asm.c

Purpose: final executable/data writer for the 386 linker.

Key behavior: provides endian output helpers, `entryvalue`, `asmb`, `cflush`, `datblk`, and `rnd`. `asmb` emits text instructions, data blocks, optional symbols/line tables/dynamic relocation data, then writes one of several headers: old Unix, COFF, Plan 9, DOS COM/EXE, or ELF. `datblk` materializes initialized data, constants, string data, and address relocations.

Integration notes: called after layout in `span.c` and data placement in `pass.c`. Dynamic-module mode routes address initializers through `dynreloc`. Header constants must agree with command-line `HEADTYPE`, `INITTEXT`, `INITDAT`, and `INITRND`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8l/asm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8l/compat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8l/compat.c

Purpose: compatibility allocation and filesystem helpers for the linker.

Key behavior: implements a bump-pointer `malloc` over linker hunks, no-op `free`, zeroing `calloc`, aborting `realloc`, `mysbrk`, no-op `setmalloctag`, and `fileexists`.

Integration notes: linker code assumes arena allocation and does not support general realloc/free behavior. `fileexists` is used for library path and `$ccroot` validation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8l/compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8l/elf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8l/elf.c

Purpose: generic ELF32/ELF64 header, program-header, and optional section-header emission for Plan 9 linkers.

Key behavior: `elfident` writes ELF identity; `elf32` and `elf64` choose endian writers, emit executable headers, three default program headers for text/data/symbol payloads, optional caller-supplied program sections, and optional section tables under debug `S`.

Integration notes: `8l/asm.c` calls `elf32(I386, ELFDATA2LSB, ...)` for `HEADTYPE 5`. Physical data address is inferred from `INITTEXT`/`INITTEXTP`; section headers are mainly diagnostic/debug support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8l/elf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8l/elf.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8l/elf.h

Purpose: local ELF constants and prototypes shared by linker ELF emitters.

Key behavior: defines ELF header sizes, identity/type/machine/program-header/section-header constants, permissions, `Putl`, and prototypes for `elf32`, `elf64`, and header-writing helpers.

Integration notes: included by `l.h`; constants are copied from Plan 9 libmach and used directly by `asm.c` and `elf.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8l/elf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8l/l.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8l/l.h

Purpose: central 386 linker header.

Key behavior: declares core structs `Adr`, `Prog`, `Sym`, `Auto`, `Optab`; symbol classes; operand classes; instruction encoding forms; global linker state; output-buffer macro `cput`; and function prototypes across all linker passes.

Integration notes: defines the contracts among object loading, pass/layout, span/encoding, listing, and final assembly. Any structural change affects nearly every `8l` file and the Plan 9 object format.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8l/l.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8l/list.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8l/list.c

Purpose: formatting and diagnostics for 386 linker instructions, operands, registers, and strings.

Key behavior: installs formatters; `Pconv` prints full instructions; `Dconv` prints addressing forms including branches, symbols, constants, indirection, and index registers; `Rconv` maps register numbers; `Sconv` escapes string constants; `diag` reports errors with current text symbol context.

Integration notes: used heavily by debug modes and error paths in `obj.c`, `pass.c`, `span.c`, and `asm.c`. `Dconv` temporarily rewrites `D_ADDR` during formatting, so callers rely on restoration.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8l/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8l/obj.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8l/obj.c

Purpose: 386 linker entry point, command-line setup, object/archive loader, symbol table, profiling instrumentation, and dynamic import/export setup.

Key behavior: `main` parses header/output/library/profiling/dynamic flags, sets default memory layout, loads objects/libraries, runs passes, and emits output. `objfile` loads files or archive members; `ldobj` decodes Plan 9 object records, symbols, history, data, text, floating literals, and branch offsets. Helpers manage autolibs, history paths, arena objects, symbols, profiling insertion, endian tables, IEEE conversion, imports, exports, and undefineds.

Integration notes: decodes object format emitted by `8c/swt.c`; produces `Prog` and `Sym` streams consumed by `pass.c`, `span.c`, and `asm.c`. Dynamic module support uses `SIMPORT`, `SEXPORT`, `SUNDEF`, relocation indexes, and generated `_exporttab`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8l/obj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8l/optab.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8l/optab.c

Purpose: 386 instruction encoding table.

Key behavior: declares operand-pattern tables (`y*`) and `optab[]`, mapping each 8.out opcode to accepted operand classes, prefix mode, and raw opcode bytes/extension fields. Covers integer, branch, stack, segment/control/debug/task register, string, and x87 instructions.

Integration notes: consumed by `span.c` `doasm`. Table order must match opcode enum values checked in `obj.c`; incorrect patterns alter instruction size and can destabilize branch span convergence.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8l/optab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8l/pass.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8l/pass.c

Purpose: linker transformation passes before final instruction sizing.

Key behavior: `dodata` lays out SDATA/SBSS and defines `bdata`, `edata`, `end`. `patch` resolves call/branch destinations and undefined calls. `follow`/`xfol` reorder basic blocks and invert branches to reduce jumps. `dostkoff` inserts stack adjustments and rewrites auto/param offsets. Also handles branch-chain compression, numeric parsing, imports, exports, and dynamic export table data synthesis.

Integration notes: runs between object loading and `span`. Stack adjustment pseudo-op `AADJSP` is later rewritten by `span`. Data layout directly controls `INITDAT`-relative addresses emitted by `asm.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8l/pass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8l/span.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/8l/span.c

Purpose: instruction sizing, final text address assignment, 386 machine-code encoding, symbols/line tables, and dynamic relocation table emission.

Key behavior: `span` iterates until branch instruction sizes stabilize, aligns data base, defines `etext`, and records function PCs. `asmsym`/`asmlc` emit symbol and line tables. `oclass`, `asmidx`, `asmand`, `doasm`, and `asmins` classify operands and encode ModR/M, SIB, immediates, branches, calls, x87, and special MOV forms. `dynreloc`/`asmdyn` collect and serialize dynamic relocations/imports.

Integration notes: depends on `optab.c` patterns and `pass.c` branch targets. Relocation side effects occur through `vaddr`/`put4` when `dlm` is active. Branch-size convergence is capped at 50 iterations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/8l/span.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9660srv/9660srv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9660srv/9660srv.c

Purpose: ISO9660/High Sierra/Joliet/Rock Ridge filesystem implementation behind the 9660 9P server.

Key behavior: `iattach` scans volume descriptors, chooses format, initializes root directory state, and detects Plan 9 extensions, SUSP, and Rock Ridge. Walk/open/read/stat handlers implement read-only filesystem semantics. Directory parsing uses `getdrec`, `rzdir`, continuation areas, Joliet UTF conversion, Plan 9 extension fields, and Rock Ridge PX/NM records. Data reads map ISO extents to cached sectors.

Integration notes: exported as `isosub` for `main.c`. It assumes 2048-byte sectors and contiguous ISO file data. Write/create/remove/wstat all return permission errors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9660srv/9660srv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9660srv/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9660srv/dat.h

Purpose: shared 9660srv data model.

Key behavior: defines sector/name constants; cache structs `Iobuf`/`Ioclust`; underlying device `Xdata`; filesystem operation table `Xfsub`; mounted filesystem `Xfs`; fid state `Xfile`; fid operation modes; and exported error/config globals.

Integration notes: bridges the generic 9P server in `main.c`, cache in `iobuf.c`, fid/device lifetime in `xfile.c`, and ISO implementation in `9660srv.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9660srv/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9660srv/data.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9660srv/data.c

Purpose: global data definitions for 9660srv.

Key behavior: defines common error strings, default service name, default image file pointer, external ISO subsystem symbol, and `xsublist` containing `isosub`.

Integration notes: `main.c` iterates `xsublist` during reset and attach. Adding more filesystem formats would extend this table.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9660srv/data.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9660srv/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9660srv/fns.h

Purpose: shared 9660srv function declarations and error-stack macros.

Key behavior: declares logging, allocation, buffer, device, fid, reference, and stat helper functions. Defines `waserror()` and `poperror()` around the global jump-buffer stack.

Integration notes: used by all 9660srv C files. Error handling is non-local via `longjmp`; callers must balance `waserror`/`poperror`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9660srv/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9660srv/iobuf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9660srv/iobuf.c

Purpose: clustered read cache for ISO image sectors.

Key behavior: `iobuf_init` allocates `nclust` clusters, each with `BUFPERCLUST` sector buffers. `getclust` finds cached clusters or reuses an idle one, reads via `xread`, and tracks busy counts. `putclust` decrements busy count and moves clusters to the LRU head. `getbuf`/`putbuf` expose single-sector buffers; `purgebuf` invalidates device clusters.

Integration notes: tuned for large contiguous ISO reads. `getbuf` errors on short reads beyond cached cluster contents. Multiple mounted images share the global cache.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9660srv/iobuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9660srv/iso9660.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9660srv/iso9660.h

Purpose: on-disk ISO9660/High Sierra structure definitions.

Key behavior: defines volume descriptor sector, endian byte-array aliases, volume descriptor type constants, `Voldesc` union layouts for ECMA `CD001` and High Sierra `CDROM`, `Drec` directory record union, and in-memory `Isofile`.

Integration notes: parsed by `9660srv.c`; fields are raw byte arrays and must be decoded through local little-endian helpers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9660srv/iso9660.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9660srv/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9660srv/main.c

Purpose: 9P server front-end for serving ISO images.

Key behavior: parses options for stdio/service mode, default image, cache clusters, chatty mode, and format-disabling flags. Publishes `/srv/<name>` unless in stdio mode, then handles 9P messages in `io`. Request handlers implement version, attach, walk with partial-walk recovery, open, read, clunk, stat, and read-only rejection for create/write/remove/wstat.

Integration notes: delegates filesystem-specific operations through `Xfsub`. Uses a jump-buffer error stack for per-request errors and `xfile.c` for fid/device lifecycle.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9660srv/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9660srv/xfile.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9660srv/xfile.c

Purpose: 9660srv fid table and underlying image-device reference management.

Key behavior: `getxdata` opens/reuses image files by qid/type/dev identity; `putxdata` closes and purges cache on last reference. `refxfs` manages mounted filesystem references. `xfile` allocates, looks up, cleans, or clunks fid records in hash buckets with a freelist; `clean` releases filesystem and private ISO state.

Integration notes: `doclone`, attach, clunk, and error cleanup all depend on this file. There is a likely type-size typo in allocation of a free `Xdata` slot using `sizeof(Xfs)`, but layout may still be large enough by accident.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9660srv/xfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/9auth.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/9auth.c

Purpose: small host-side helper for manual challenge/response auth files exposed by 9nfs.

Key behavior: parses root/user/debug/delete options, builds `<root>/#<user>`, optionally creates it for deletion/reset, otherwise reads a challenge, prompts for a response, rewinds, and writes the response.

Integration notes: standalone Unix-style utility using libc/POSIX headers rather than Plan 9 `all.h`. Works with `NETCHLEN` fixed-size challenge/response records.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/9auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/9p.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/9p.c

Purpose: 9P client message helper and fid LRU manager for the NFS bridge.

Key behavior: `xmesg` sends a 9P request on a `Session`, waits for the matching tag, handles `Rerror`, and validates response type. Fid helpers allocate/recycle 9P fids, keep active fids in MRU order, clunk stale/evicted fids, and update fid expiry timers.

Integration notes: core dependency for mount/NFS request translation. `messagesize` is negotiated in `srvinit`. Stale fid cleanup is driven by `mnttimer`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/9p.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/all.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/all.h

Purpose: umbrella include for 9nfs.

Key behavior: includes Plan 9 base libraries, auth/fcall/regexp, local `dat.h`, `fns.h`, `rpc.h`, and `nfs.h`, and vararg format checks for logging helpers.

Integration notes: most 9nfs implementation files include this single header to share all protocol and utility definitions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/all.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/auth.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/auth.c

Purpose: disabled/stubbed NFS authentication-file hooks.

Key behavior: `xfauth` returns nil; read/write/remove handlers log and return empty or failure results.

Integration notes: comments state NFS authentication is disabled. `nfsserver.c` still contains paths for root `#user` auth files, but this implementation makes those paths inert.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/authhostowner.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/authhostowner.c

Purpose: hostowner authentication proxy from remote 9P auth fid to local factotum.

Key behavior: decodes `AuthInfo`, drives `AuthRpc` with retry-on-key-needed behavior, proxies auth reads/writes over 9P `Tread`/`Twrite`, and attempts `Tauth` plus authenticated `Tattach` as local `getuser()`.

Integration notes: used by `srvinit`; if remote auth is not needed, `Tauth` failure path can be treated as success. Cleans temporary auth and attach fids by clunking through `xmesg`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/authhostowner.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/chat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/chat.c

Purpose: logging, runtime chat control, and panic handling for 9nfs services.

Key behavior: `chatsrv` publishes a `/srv` control file and forks a shared-memory control process to update `chatty`, `rpcdebug`, and `conftime`. `chat` writes verbose logs, `clog` writes stderr or syslog depending on settings, and `panic` logs and exits.

Integration notes: service files use `chat`/`clog` extensively. Negative/zero `chatty` routes logs through syslog; high chatty levels enable RPC debug.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/chat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/dat.h

Purpose: shared protocol/session/xfile data model for 9nfs.

Key behavior: defines RPC call/reply/auth structs, NFS file handles, uid/gid mapping structs, cached xfile and per-user xfid state, fid LRU records, sessions with 9P message buffers and fid pool, challenge state, and global configuration declarations.

Integration notes: central contract between RPC server, mount service, NFS service, auth, name mapping, 9P session management, and xfile cache.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/fns.h

Purpose: shared function prototypes for 9nfs.

Key behavior: declares RPC, NFS, auth, session, fid, xfile, name mapping, string table, server, logging, and utility functions.

Integration notes: complements `dat.h`; signatures show the main subsystem boundaries even for files not in this group, such as `server.c`, `xfile.c`, and uid-map readers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/listalloc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/listalloc.c

Purpose: fixed-size freelist allocator helper.

Key behavior: rounds element size to `ulong` alignment, allocates `n` elements, and links them by storing next pointers in each slot.

Integration notes: returns a raw freelist head; callers must know element layout and manage allocations themselves.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/listalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/mport.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/mport.c

Purpose: diagnostic RPC client for querying a remote portmapper and mount daemon.

Key behavior: dials UDP portmapper, enables header mode, extracts remote host/port, calls `PMAPPROC_GETPORT` for mount, pings mount null, then requests and prints exports. Optional `-m` creates AUTH_UNIX credentials.

Integration notes: standalone test/tool using shared RPC codec. Exercises `rpcS2M`, `rpcM2S`, and mount export parsing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/mport.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/nametest.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/nametest.c

Purpose: interactive/test utility for Unix id/name mapping.

Key behavior: reads maps or ids, supports commands to reload maps, translate id-to-name/name-to-id, print current server/client pair, and switch between user/group maps.

Integration notes: depends on `readunixids`, `readunixidmaps`, `pair2idmap`, `id2name`, and `name2id` implemented outside this file group.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/nametest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/nfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/nfs.c

Purpose: NFS handle/session translation and NFS attribute conversion helpers.

Key behavior: `rpc2xfid` decodes NFS file handles, authenticates AUTH_UNIX credentials, maps client ids to Plan 9 users, locates cached xfiles, and returns per-user xfids. `setuser`, `xfstat`, `xfopen`, `xfwalkcr`, `xpclear`, and `xp2fhandle` manage 9P fid state and NFS handles. `dir2fattr` converts Plan 9 `Dir` to NFS v2 fattr; `convM2sattr` parses NFS setattr payloads.

Integration notes: core bridge between stateless NFS handles and stateful 9P fids. File handles embed `starttime`, session pointer bits, qid path, and qid type, making them process-lifetime scoped.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/nfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/nfs.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/nfs.h

Purpose: NFS v2 constants.

Key behavior: defines NFS status codes, file types, mode bits, and `NOATTR`.

Integration notes: used by NFS server and attribute conversion paths. Based on RFC 1094.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/nfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/nfsmount.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/nfsmount.c

Purpose: NFS mount protocol service and 9P backend session initialization.

Key behavior: `mntinit` parses backend service options, initializes sessions, reloads uid maps, and configures stale-fid timeout. `srvinit` connects to 9P service/file/fd, negotiates version, authenticates, attaches as `none`, and records root xfile. Mount procedures implement null, mount, dump, unmount, unmount-all, export, and root lookup.

Integration notes: paired with `nfsserver.c` in one program map. `noauth` is forcibly set to 1 in the file, disabling auth despite option parsing. Mount replies hand out NFS handles generated by `xp2fhandle`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/nfsmount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/nfsserver.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/nfsserver.c

Purpose: NFS v2 server procedure implementation over a Plan 9 9P backend.

Key behavior: registers mount and NFS program maps, installs timer reload/stale-fid cleanup, and implements getattr, setattr, lookup, read, write, create, remove, rename, mkdir, rmdir, readdir, statfs, plus stubs for root/readlink/link/symlink/writecache. Operations decode NFS arguments, resolve `Xfid`s via `rpc2xfid`, perform 9P operations, translate errors/status, and serialize NFS replies.

Integration notes: relies on `nfs.c` for handle/fid/attribute conversion and on `9p.c` for actual 9P messages. Readdir converts Plan 9 stat records into NFS directory entries and tracks per-xfid offsets.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/nfsserver.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/pcnfsd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/pcnfsd.c

Purpose: PC-NFS daemon RPC service.

Key behavior: registers PCNFSD v1/v2 program maps, initializes facilities and uid maps, implements null, info, v1 auth, and v2 auth. Auth requests descramble ID/password fields but do not validate passwords; they map username to uid/gid or fall back to uid 1 and return canned home/comment data.

Integration notes: listens on port 1111 via shared `server`. Intended compatibility service, not strong authentication.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/pcnfsd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/portmapper.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/portmapper.c

Purpose: minimal SunRPC portmapper service for 9nfs-related programs.

Key behavior: static map advertises NFS v2 and mount on UDP 2049, PCNFSD v1/v2 on UDP 1111. Implements null, set/unset, getport, dump, and callit. `set` always returns false; `unset` true; `callit` only responds for proc 0 with port and empty result.

Integration notes: runs on port 111 and uses shared RPC server/codec. It is static, not a general dynamic portmapper.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/portmapper.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/rpc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/rpc.c

Purpose: SunRPC/XDR-ish marshal/unmarshal helpers and common RPC reply utilities.

Key behavior: `rpcM2S` decodes UDP header-prefixed RPC calls/replies into `Rpccall`; `rpcS2M` serializes them back. `auth2unix` decodes AUTH_UNIX, `string2S` decodes counted strings into interned strings, `rpcprint` and `showauth` log decoded calls, and `garbage`/`error` build failure replies.

Integration notes: uses big-endian network integer macros and Plan 9 UDP header layout. `string2S` allocates temporary NUL-terminated storage and interns it through `strstore`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/9nfs/rpc.c -->