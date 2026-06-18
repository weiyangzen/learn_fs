# Group Research: group_1634_plan9_sources_os_plan9_plan9_sys_src_cmd_vl_noop_c_sources_os_plan9_0e79610f1115

Scope checked against `Docs/research_subset_a.md`: all requested files are under `sources/os/plan9/plan9`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vl/noop.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vl/noop.c

MIPS linker cleanup and scheduling-preparation pass for `vl`.

Key responsibilities:
- Strips assembler `ANOP` nodes while preserving label marks.
- Marks labels, branches, sync points, leaf functions, and scheduling boundaries.
- Computes per-TEXT frame and `BECOME` sizes, then defines `ALEFbecome`.
- Synthesizes function prologues and return/`BECOME` epilogues around MIPS stack/link-register conventions.
- Splits schedulable blocks and invokes `sched()`.
- Contains optional MIPS 24K erratum workaround logic to avoid three consecutive stores and keep stores out of delay slots.

Important behavior:
- Leaf functions with no frame avoid stack/link-save setup.
- Non-leaf returns restore link through register 2 and jump indirectly.
- Moves to/from machine or floating-control registers are forced into sync/nop-protected regions.
- `addnop()` emits the canonical MIPS zero-register `NOR` nop.

Risks:
- This is global mutable linker state; correctness depends on mark bits being maintained consistently across earlier passes.
- The 24K workaround is compiled disabled by `Mips24k = 0`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vl/noop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vl/obj.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vl/obj.c

Main driver, option parser, object/archive loader, symbol manager, profiling injector, and endian/floating helper code for the Plan 9 MIPS linker `vl`.

Key responsibilities:
- Parses linker flags, selects output profile/header type, creates the output file, and runs the linker pipeline: `patch`, profiling, `dodata`, `follow`, `noops`, `span`, `asmb`, `undef`.
- Supports big-endian `v.out` and little-endian `0.out` mode.
- Loads plain Plan 9 object files and Plan 9 archives, including symbol-table-driven archive member extraction for unresolved externals.
- Decodes object records into `Prog`, `Adr`, `Sym`, `Auto`, history, data, global, dynamic, init, and text state.
- Tracks autolibs through `AHISTORY`, expands `$O`/`$M`, and searches configured lib directories.
- Interns symbols by name/version, allocates linker hunks, and creates `Prog` nodes.
- Converts floating constants into data literals for `AMOVF`/`AMOVD`.
- Adds optional profiling or embedded tracing calls.

Important behavior:
- Default entry is `_main` or `_mainp` unless overridden with `-E`.
- `-H` supports several MIPS output layouts: Unix simple, Plan 9, boot images, COFF, ELF, 64-bit ELF, and headerless.
- Duplicate `TEXT` can be skipped when marked `DUPOK`.
- `ASUB`/`ASUBU` constants are canonicalized into negative adds.
- Errors remove the partial output file.

Risks:
- Parser assumes trusted Plan 9 object/archive layout and uses fixed-size buffers.
- Archive loading loops until no unresolved symbols are satisfied, so symbol-state corruption can cascade.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vl/obj.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vl/optab.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vl/optab.c

Instruction selection table for `vl` MIPS code generation.

Key contents:
- Defines `Optab optab[]`, mapping abstract assembler opcodes and operand classes to encoding templates, instruction sizes, and default base registers.
- Covers TEXT, integer moves, arithmetic, shifts, floating point ops, small/large SB/SP/zero-relative memory forms, constants, branches, jumps, HI/LO, floating-control registers, TLB/system ops, CASE, and WORD.
- Uses representative opcodes so `span.c` can clone ranges for equivalent instructions with `buildop()` and `buildrep()`.

Important behavior:
- Table entries encode both size decisions and assembler case numbers later consumed by the output backend.
- Small versus large addressing classes are central to code size and literal decisions.

Risks:
- Comment says several 64-bit and floating double move cases are unfinished.
- Any class/template mismatch reports “illegal combination” during `oplook()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vl/optab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vl/pass.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vl/pass.c

Middle linker passes for data layout, undefined checking, code following, branch patching, and numeric parsing.

Key responsibilities:
- `dodata()` validates data initializers, lays out small data, regular data, BSS, and linker-generated literal pools.
- Converts large constants and data addresses into literal data entries when they cannot fit direct encodings.
- Defines standard linker symbols: `setR30`, `bdata`, `edata`, `end`, `etext`.
- `undef()` reports unresolved `SXREF` symbols.
- `follow()`/`xfol()` reorder control flow to favor fall-through paths and invert simple branches when profitable.
- `patch()` resolves branch/jump/return symbol targets into `Prog.cond` pointers and collapses jump chains.
- `mkfwd()` builds skip pointers for faster pc-to-`Prog` lookup.
- `atolwhex()` parses decimal, octal, and hex signed constants; `rnd()` rounds alignment.

Important behavior:
- Data symbols with zero size are diagnosed and forced to size one.
- String constants can be moved into text when debug flag `t` is set.
- Branches to undefined text symbols are redirected to `exit` after a diagnostic.

Risks:
- Layout mutates symbol types in several passes; later code relies on those exact transitions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vl/pass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vl/sched.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vl/sched.c

MIPS instruction scheduler for bounded basic blocks.

Key responsibilities:
- Builds a side array of scheduling records containing copied `Prog`, register/memory/condition dependencies, memory offsets, sizes, and compound-instruction flags.
- Classifies instructions through `regsused()`, including integer regs, floating regs, HI/LO, FCR/MCR, SB/SP/general memory, loads, branches, and floating compares.
- Reorders loads and independent filler instructions to cover load, branch, and floating compare delay slots.
- Inserts nops when no legal filler is available.
- Adds extra nops for HI/LO use followed by HI/LO set.
- Writes scheduled instructions back into the original linked list.

Important behavior:
- Memory dependencies distinguish general memory, SB-relative memory, and SP-relative memory, allowing non-overlapping SB/SP references to pass each other.
- Compound instructions and non-4-byte encodings are kept more conservatively.
- Register zero is masked out as a set target.

Risks:
- Correctness depends on exact `aclass()` and `oplook()` classifications.
- Memory overlap is size/offset based and conservative for unknown/global memory.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vl/sched.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vl/span.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vl/span.c

Address assignment, operand classification, branch-range repair, and optab lookup support for `vl`.

Key responsibilities:
- `span()` assigns final text PCs from `INITTEXT`, computes instruction sizes through `oplook()`, updates text symbol values, and computes `textsize`/`INITDAT`.
- Works around early MIPS 4000 page-boundary delay-slot bugs by inserting a nop before vulnerable branch/jump instructions.
- Rewrites too-far short conditional branches into longer branch-around-jump sequences.
- Optionally places string constants into text.
- `aclass()` maps addresses to codegen classes and computes `instoffset`.
- `oplook()` finds or caches the matching `Optab`.
- `buildop()` sorts and indexes `optab`, creates opcode aliases, and builds fast operand-class cross tables.
- `xdefine()` sets linker symbols if undefined.

Important behavior:
- Extern/static data addressing is biased by `BIG` for small-data addressing.
- `D_CONST` classification distinguishes zero, signed short, unsigned short, upper-half, add, and full long constants.
- Branch class starts as short; long forms are selected or synthesized later.

Risks:
- Class cache invalidation is manual; transformations must call `nocache()`.
- Branch expansion changes the instruction stream while span is iterating.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vl/span.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/auth.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/auth.c

RFB 3.3 handshake and VNC challenge-response authentication.

Key responsibilities:
- Sends or receives the fixed `RFB 003.003\n` version string for client/server roles.
- Implements VNC DES challenge encryption, including VNC’s bit-reversed DES key bytes.
- Uses Plan 9 auth/factotum for client responses and server-side challenge validation.
- Falls back to an interactive `/dev/cons` password prompt for clients without suitable factotum keys.
- Sends server-side VNC auth challenge and final OK/failure response.

Important behavior:
- Client auth supports no-auth, failure-with-reason, and VNC auth.
- Client key lookup uses `proto=vnc role=client server=...`.
- Server challenge uses `proto=vnc role=server user=...`.

Risks:
- Protocol is old RFB 3.3 VNC auth, not modern secure authentication.
- Password fallback reads raw console input and zeroes only the local password buffer afterward.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/chan.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/chan.c

User-space emulation of core Plan 9 `Chan`, reference, and canonical-name helpers for the VNC file-server environment.

Key responsibilities:
- Allocates, clones, closes, and frees `Chan` structures.
- Dispatches close to the owning device table.
- Implements locked `Ref` increment/decrement.
- Manages reference-counted `Cname` strings with copy-on-write extension.
- Cleans canonical names, including special `#` device paths.
- Provides directory assertion via `isdir()`.

Important behavior:
- `cclone()` delegates to the device walk method with zero names and shares the original channel name.
- `addelem()` elides `.` and canonicalizes after `..`.
- `cclose()` tolerates device close errors through the local `waserror` mechanism before freeing the channel.

Risks:
- Reference lifecycle is manual and shared with device implementations.
- `Cname.ref > 1` copy-on-write reads the ref without locking.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/chan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/color.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/color.c

Pixel-format negotiation and local color conversion for the VNC client path.

Key responsibilities:
- Converts Plan 9 draw channel descriptors into RFB `Pixfmt` masks and shifts.
- Chooses a VNC pixel format matching the local screen.
- Handles 24-bit local screens by requesting 32 bpp and dropping the padding byte.
- Emulates 8-bit `CMAP8` either through 12-bit RGB or compact BGR332 input, converting back to Plan 9 cmap indexes.
- Sends the negotiated pixel format to the server.

Important behavior:
- VNC is kept little-endian.
- Conversion callback `cvtpixels` is set globally for later rectangle decoding.
- Unsupported screen channels or non-byte-aligned depths are fatal.

Risks:
- CMAP conversions are lossy.
- Global conversion state assumes one active VNC display path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/color.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/compat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/compat.c

Compatibility layer that lets selected Plan 9 kernel-style device code run in user space.

Key responsibilities:
- Initializes per-process `Proc` state through `privalloc()` and `newup()`.
- Spawns kernel-style processes with `rfork(RFPROC|RFMEM|RFNOWAIT)`.
- Implements `panic`, `smalloc`, `seconds`, `error`, `nexterror`, and `readstr`.
- Provides Plan 9-style `Rendez` sleep/wakeup using `rendezvous()`.
- Supports interrupting sleeps through `rendintr()` and clearing pending interrupts.
- Tracks and validates error-stack depth.

Important behavior:
- `waserror()`/`poperror()` are implemented in the header using `setjmp`/`longjmp`.
- `openmode()` maps `OEXEC` to `OREAD` and rejects invalid modes.
- `initcompat()` also installs a rendezvous namespace with `rfork(RFREND)`.

Risks:
- Rendezvous uses sentinel values and panics on unexpected pairings.
- Shared-memory forked processes rely on per-process `up` but shared global device state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/compat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/compat.h

Header defining the user-space kernel compatibility ABI used by the VNC device and export code.

Key contents:
- Type declarations for `Block`, `Chan`, `Cname`, `Dev`, `Dirtab`, `Proc`, `Ref`, `Rendez`, and `Walkqid`.
- Kernel-style structs for references, rendezvous waiters, channels, canonical names, device operation tables, directory entries, walk results, and process state.
- Channel flags `COPEN` and `CFREE`, error-stack limit `NERR`, name length `KNAMELEN`, and `DEVDOTDOT`.
- Macro `up` mapped to per-process `privup`.
- `waserror()`/`poperror()` macros over `setjmp`.
- Prototypes for device helpers, channel helpers, rendezvous helpers, exporter, and screen initialization.

Role:
- This is the contract that makes copied Plan 9 device code compile as a user-space VNC filesystem.

Risks:
- The header redefines `Rendez` as `KRendez`, so include ordering matters.
- Error handling is macro-based and easy to unbalance.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/compat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/dev.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/dev.c

Generic Plan 9 device helper routines for the VNC user-space device filesystem.

Key responsibilities:
- Creates `Qid` values and locates device table entries by device character.
- Fills `Dir` structures from `Dirtab` data.
- Implements generic attach, clone, walk, stat, directory read, permission check, and open operations.
- Provides default deny/panic implementations for create, block I/O, remove, and wstat.

Important behavior:
- `devgen()` expects table entry zero to be the directory itself.
- `devwalk()` supports cloning, partial walks, `.`, `..`, and generator-driven lookup.
- `devstat()` synthesizes a directory stat if no table entry matches a directory channel.
- `devopen()` rejects non-read opens on directories and sets `COPEN`.

Risks:
- Permission checks are simplified to owner/eve/other mapping.
- Directory read has a comment questioning offset handling for skipped entries.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/dev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/devcons.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/devcons.c

Synthetic console device for the VNC environment.

Key responsibilities:
- Provides `/dev/cons`, `/dev/consctl`, `/dev/snarf`, and `/dev/winname` entries.
- Implements fixed-size circular queues for raw keyboard input and processed line input.
- Accepts keyboard runes through `kbdputc()`, encodes them as UTF-8, queues them, and echoes to the screen unless raw mode is active.
- Implements canonical line editing for backspace, control-U, newline, and control-D.
- Supports `rawon`/`rawoff` through `consctl`.
- Maintains the snarf buffer and version, replacing it on close after write.

Important behavior:
- Opening `consctl` increments a control-open count; last close disables raw mode.
- `rawon` writes a NUL wakeup byte to unblock readers.
- Snarf writes append to a temporary per-open buffer and commit on close.

Risks:
- Queues silently stop accepting bytes when full.
- `winname` is present but mode `0000` and not otherwise handled.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/devcons.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/devdraw.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/devdraw.c

Large user-space implementation of Plan 9’s `draw` device over a memory framebuffer used by VNC.

Key responsibilities:
- Exposes `#i/draw`, `new`, per-client directories, `ctl`, `data`, `colormap`, and `refresh`.
- Manages draw clients, image IDs, named images, screens, windows/layers, refresh messages, and reference counts.
- Attaches the VNC framebuffer as image id 0 through `attachscreen()`.
- Parses binary draw protocol messages on `data`.
- Implements image allocation/free, screen allocation/free, named image sharing, repl/clip changes, drawing, lines, ellipses/arcs, polygons, strings/fonts, image read/write, window origin changes, stacking, flush, and compositing op selection.
- Tracks dirty framebuffer rectangles and calls `flushmemscreen()` for VNC update propagation.
- Implements colormap read/write and screen blank/unblank support.

Important behavior:
- Qid path packs file type plus client slot.
- Image reference counts include opens, screens, fills, and named-image derivations.
- Refresh callbacks queue rectangles for clients using `Refmesg`.
- `drawmesg()` validates message lengths and geometry before dispatching memdraw operations.
- Once any draw client has existed, resizing is considered unsupported.

Risks:
- This file is highly stateful and lock-dependent around `sdraw`.
- Binary protocol parsing is manual; bad lengths or IDs produce Plan 9 errors.
- Some comments mark incomplete cleanup/detach and inefficient flush behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/devdraw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/devmouse.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/devmouse.c

Synthetic mouse and cursor device for the VNC environment.

Key responsibilities:
- Provides `/dev/mouse` and `/dev/cursor`.
- Tracks current mouse position, buttons, event counter, timestamp, and a ring buffer of button-change events.
- Enforces a single open reader for `/dev/mouse`.
- Reads mouse events in Plan 9 `m%11d...` text format.
- Reads and writes cursor bitmaps in Plan 9 cursor format.
- Supports mouse warping by writing coordinates to `/dev/mouse`.
- Maintains button remapping infrastructure and cursor redraw scheduling.

Important behavior:
- Button change events are queued; motion-only reads return current state when no queued event exists.
- If the button queue fills, queued events are dropped until the reader catches up.
- Last close resets the cursor to the arrow.
- Cursor updates call `setcursor()`, `cursoroff()`, `cursoron()`, and `mouseclock()`.

Risks:
- `setbuttonmap()` exists but is not wired into exposed control parsing here.
- Mouse reader concurrency assumes only one active reader.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/devmouse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/draw.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/draw.c

VNC client-side framebuffer update decoder and screen updater.

Key responsibilities:
- Sends the requested RFB encoding list.
- Sends framebuffer update requests sized to the local screen and server dimensions.
- Decodes server rectangles for raw, copyrect, RRE, CoRRE, hextile, and mouse-warp encodings.
- Converts incoming pixels through `cvtpixels` when negotiated by `color.c`.
- Loads decoded pixel data into Plan 9 draw images and draws onto the display.
- Handles server messages: framebuffer update, colormap, bell, server ack, and server cut text.

Important behavior:
- `pixbuf` stores a full rectangle in local screen pixel size; `linebuf` supports converted row input.
- Rectangles are clipped when local screen size is smaller than server size.
- Hextile maintains tile-local background/foreground colors.
- After each framebuffer update, it flushes the display and requests an incremental update.

Risks:
- Bad server geometry or encoding is fatal.
- Pixel buffers are allocated for full server dimensions and kept globally.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/draw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/error.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/error.h

Extern declarations for Plan 9-style error string globals used by the VNC compatibility/device code.

Key contents:
- Declares common kernel error strings such as `Enonexist`, `Eperm`, `Ebadarg`, `Einuse`, `Eshort`, `Ebadstat`, and many others.
- Mirrors the definitions in `errstr.h`.

Role:
- Lets device code call `error(Eperm)` and related Plan 9 idioms while linking against user-space string definitions.

Risks:
- This header must stay consistent with `errstr.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/error.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/errstr.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/errstr.h

Definitions of Plan 9-style error string globals for the VNC compatibility layer.

Key contents:
- Defines string storage for all errors declared in `error.h`.
- Covers mount, path, permission, I/O, descriptor, process, memory, mouse, stat, and miscellaneous error messages.

Role:
- Provides address-stable global strings so code can pass symbolic error variables to `error()`.

Risks:
- It is a `.h` containing definitions, so it should be included in exactly one C translation unit; here `compat.c` includes it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/errstr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/exporter.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/exporter.c

Helper for exporting synthetic VNC devices over a local 9P connection and mounting them.

Key responsibilities:
- Initializes each supplied `Dev`, attaches its root channel, and gathers roots.
- Creates a pipe pair for 9P traffic.
- Starts an `exporter` kproc that runs `sysexport()` in a private namespace and calls `shutdown()` on exit.
- Provides `mounter()` to mount each exported root on a target mount point using numeric attach specs.

Important behavior:
- Multiple roots are mounted by duplicating the pipe fd and using attach names `"0"`, `"1"`, etc.
- First mount uses the requested mount flag; subsequent `MREPL` mounts become `MAFTER`.

Risks:
- `exporter()` passes a stack `Exporter` struct to a new process sharing memory; it relies on the child consuming it immediately.
- Errors during device attach are converted to `werrstr`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/exporter.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/exportfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/exportfs.c

User-space 9P2000 export server for the synthetic VNC device roots.

Key responsibilities:
- Reads 9P messages, dispatches them to worker kprocs, and writes replies.
- Supports `Tversion`, `Tauth`, `Tattach`, `Twalk`, `Topen`, `Tcreate`, `Tread`, `Twrite`, `Tclunk`, `Tremove`, `Tstat`, `Twstat`, and `Tflush`.
- Maintains per-export fid hash tables with refcounts, attached state, channel pointers, and offsets.
- Queues work globally across exports and starts worker processes on demand.
- Handles flush by removing queued work or interrupting in-progress workers and suppressing their reply.
- Shuts down by draining queued work, interrupting sleepers, and freeing fids/channels.

Important behavior:
- `Tauth` always reports authentication not required.
- Attach spec selects one of the exported root channels numerically.
- Device operations are delegated through `devtab[c->type]`.
- Reads place response data directly in the 9P output buffer after `IOHDRSZ`.

Risks:
- Worker and flush synchronization is subtle: queued, active, responding, and no-response states are separate.
- Directory seek alignment checks are defined but not actually used in `Exread`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/exportfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/kbd.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/kbd.h

Shared keyboard/snarf declarations for the VNC console and keyboard paths.

Key contents:
- Defines `Snarf` as a locked buffer with version, length, and data pointer.
- Sets `MAXSNARF` to 100 KiB.
- Declares global `snarf`.
- Declares Latin compose, keyboard input, screen output, VNC keyboard input, and snarf update functions.

Role:
- Connects `devcons.c`, `kbds.c`, `latin1.c`, and screen output code.

Risks:
- Snarf ownership is transferred by pointer, so callers must follow the close/commit convention.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/kbd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/kbds.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/kbds.c

VNC server-side keyboard input translator from RFB/X keysyms into Plan 9 console runes.

Key responsibilities:
- Maps VNC/X special keysyms to Plan 9 keyboard constants.
- Uses `ksym2utf.h` to map X keysyms to Unicode runes.
- Tracks modifier state: Alt/Latin, caps, control, num, and shift.
- Implements Plan 9 Latin compose collection through `latin1()`.
- Sends resulting characters to the console queue via `kbdputc()`.

Important behavior:
- Key-up events only affect modifier state.
- Control modifies normal characters with `c &= 0x1f`.
- Latin starts compose collection and buffers up to five runes.
- Unknown special keys are ignored.

Risks:
- `shift` and `num` state is tracked but mostly unused in this translator.
- Mapping coverage depends on the generated `ksym2utf` table.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/kbds.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/kbdv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/kbdv.c

VNC client-side keyboard sender from local Plan 9 keyboard input to RFB key events.

Key responsibilities:
- Reads raw keyboard runes from the display console.
- Maps Plan 9 special keys and function keys to X keysyms.
- Uses `utf2ksym.h` to translate Unicode runes to X keysyms when possible.
- Sends RFB key-down/key-up messages.
- Synthesizes modifier events for Alt, Control, Shift, control-letter combinations, uppercase letters, and shifted punctuation.

Important behavior:
- Opens display `cons` and `consctl`, then enables raw mode.
- Modifier keys toggle local state; ordinary keys are sent down then up.
- After a normal key, any active Alt/Ctrl/Shift is released.
- Adds temporary Shift for characters known to need it on some VNC servers.

Risks:
- Modifier state toggling depends on Plan 9 keyboard rune behavior, not physical key up/down.
- Fatal exits on console read failure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/kbdv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/ksym2utf.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/ksym2utf.h

Generated static lookup table converting X11 keysyms to Unicode runes for VNC server-side input.

Key contents:
- Defines `static ulong ksym2utf[]`.
- Sparse designated indexes cover X11 keysym ranges for Latin extended letters, Japanese kana, Arabic/Persian, Cyrillic, Greek, mathematical symbols, box drawing, punctuation, Hebrew, Thai, Korean Jamo, Vietnamese, currency symbols, Armenian, Georgian, and other extended ranges.
- Used by `kbds.c` after special-key handling to convert incoming VNC/X keysyms into Plan 9 runes.

Important behavior:
- The array is indexed directly by keysym when the keysym is within `nelem(ksym2utf)` and the entry is nonzero.
- ASCII keysyms pass through without table lookup.

Risks:
- Sparse table size is determined by the largest designated index, so it is convenient but memory-heavy compared with a compact map.
- Reverse mapping is not perfectly one-to-one for duplicate Unicode values.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/ksym2utf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/latin1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/latin1.c

Plan 9 Latin compose sequence interpreter.

Key responsibilities:
- Builds `latintab[]` from `latin1.h`.
- Supports `Xhhhh` four-hex-digit Unicode input.
- Resolves one-, two-, and three-character compose sequences to runes.
- Returns `-1` for invalid sequence and negative required-length markers when more input is needed.

Important behavior:
- Table assumptions are documented: leader length is one or two, and prefix ordering matters.
- `unicode()` skips initial `X` and parses exactly four hex digits.
- `latin1()` returns `-2`, `-3`, or `-5` to request more keystrokes.

Risks:
- Correct prefix handling depends on table ordering in `latin1.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/latin1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/latin1.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/latin1.h

Compose table data included into `latin1.c`.

Key contents:
- Defines initializer rows mapping compose leaders and final character sets to output rune strings.
- Covers accented Latin letters, Greek, Cyrillic, math symbols, arrows, fractions, punctuation, currency, chess symbols, Hebrew-like/private symbols, and other Plan 9 compose sequences.
- Includes both one-character leaders and two-character leader prefixes.

Role:
- Data source for `latin1()`; each row maps `ld` plus a selected character in `si` to the corresponding rune at the same offset in `so`.

Risks:
- This is included as raw initializer rows, not a standalone header with guards.
- Sequence validity and “need more input” behavior depend on row order.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/latin1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/proto.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/proto.c

Low-level RFB/VNC protocol I/O helpers.

Key responsibilities:
- Initializes and terminates `Vnc` Bio input/output state.
- Reads and writes big-endian chars, shorts, longs, points, rectangles, CoRRE rectangles, pixel formats, byte blocks, and strings.
- Provides a special unbuffered `vncrdstringx()` for negotiation steps that must bypass Bio.
- Flushes output and handles hung-up connections through `vnchungup()`.
- Serializes writes with `vnclock()`/`vncunlock()`.
- Provides debug hex dump and `vncgobble()` discard helper.

Important behavior:
- RFB numeric byte order is encoded manually.
- Read/write failures call `vnchungup()` rather than returning errors.
- `vncrdstring()` allocates NUL-terminated memory for protocol strings.

Risks:
- Allocation uses `assert`, so malformed huge string lengths can terminate the process or exhaust memory.
- Most helpers are fatal-on-error rather than recoverable.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/proto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/rlist.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/rlist.c

Rectangle-list union and simplification utility for VNC update regions.

Key responsibilities:
- Grows and frees dynamic rectangle lists.
- Adds rectangles while merging adjacent/aligned rectangles and eliminating covered rectangles.
- Splits overlapping rectangles using edge, corner, and stride subtraction helpers.
- Maintains a bounding box and optional verbose diagnostics.
- Includes a `REGION_DEBUG` standalone test harness.

Important behavior:
- `addtorlist()` starts with the new rectangle in a temporary list, then iteratively intersects existing rectangles and may add split leftovers back to the temporary queue.
- Aborts on unhandled overlap decomposition.
- Global `tot` limits total allocated rectangles and fatally stops above 10000.

Risks:
- Region algorithm is handcrafted and sensitive to rectangle edge cases.
- Uses global accounting across all lists.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/rlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/rre.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/rre.c

VNC server-side rectangle encoders for raw, RRE, CoRRE, and hextile.

Key responsibilities:
- Sends raw rectangles directly from the framebuffer.
- Encodes hextile updates by tiling into 16x16 blocks and choosing background, foreground, colored-subrect, or raw tile forms.
- Encodes RRE/CoRRE by splitting large rectangles and generating uniform-color subrectangles against a guessed background color.
- Falls back to raw encoding when compression would exceed raw size or allocation/classification fails.
- Counts expected rectangle splits for RRE/CoRRE/hextile.
- Implements pixel equality and pixel write helpers for 8-, 16-, and 32-bpp modes.

Important behavior:
- Background is estimated by sampling common colors.
- `encrre()` finds maximal same-color rectangles and marks covered pixels in a `done` array.
- CoRRE uses one-byte coordinates and smaller split dimensions.
- Hextile caches previous background/foreground colors but resets around raw/colorful cases for client compatibility.

Risks:
- Only 8/16/32 bpp are compressed; other depths fall back to raw.
- Compression is heuristic, not optimal.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/rre.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/screen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/screen.c

In-memory framebuffer, cursor, and text console backing for the VNC environment.

Key responsibilities:
- Initializes a `Memimage` screen with requested dimensions and channel.
- Creates cursor mask images and default arrow cursor state.
- Draws an initial Plan 9 console window using the default memory font.
- Implements `attachscreen()` for `devdraw.c`.
- Provides stub color map operations and blanking hook.
- Converts Plan 9 cursor bitmaps into memory images and draws cursor overlays.
- Tracks cursor position, offscreen hiding, and cursor version.
- Implements console text output with newline, carriage return, tab, backspace, wrapping, scrolling, and dirty rectangle flushing.

Important behavior:
- `screenputs()` locks draw state while rendering UTF-8 runes.
- Console scroll moves the window contents up by eight font heights.
- Cursor “on” updates cursor position from `mousexy()`; cursor “off” moves it offscreen.

Risks:
- `getcolor()`/`setcolor()` are stubs, so colormap behavior is limited.
- `flushmemscreen()` is external and central to VNC update propagation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/screen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/screen.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/screen.h

Shared screen, cursor, draw-lock, and framebuffer declarations for VNC device code.

Key contents:
- Defines `Cursorinfo` as a `Cursor` plus lock.
- Declares global cursor state, arrow cursor, framebuffer image, cursor version, and cursor position.
- Declares mouse, cursor, framebuffer flush, draw lock, colormap, screen blanking, screen initialization, mouse tracking, and `attachscreen()` functions.
- Defines `TK2SEC(x)` as `0`.
- Declares `fsinit()`.

Role:
- Connects `screen.c`, `devdraw.c`, `devmouse.c`, and related VNC server code.

Risks:
- `TK2SEC` is a stub, so code depending on real tick conversion would not get useful timing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/screen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/utf2ksym.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/utf2ksym.h

Generated static lookup table converting Unicode runes to X11 keysyms for VNC client-side keyboard output.

Key contents:
- Defines `static ulong utf2ksym[]`.
- Sparse designated indexes cover many of the same script and symbol ranges as `ksym2utf.h`: Latin extended, Japanese kana, Arabic/Persian, Cyrillic, Greek, math, box drawing, punctuation, Hebrew, Thai, Korean Jamo, Vietnamese, currency, Armenian, Georgian, and private/special symbols.
- Used by `kbdv.c` to send keysyms that VNC servers expect instead of raw Unicode code points where a mapping exists.

Important behavior:
- Indexed directly by Unicode rune when the rune is within `nelem(utf2ksym)` and the entry is nonzero.
- ASCII and unmapped runes are sent as their rune value.

Risks:
- Reverse mapping loses duplicates: when several keysyms map to one rune, only one designated rune entry can be used.
- Sparse Unicode-indexed array is simple but memory-heavy.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/vnc/utf2ksym.h -->