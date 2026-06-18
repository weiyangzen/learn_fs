# Group Research: group_195_9front_sources_os_plan9_9front_sys_src_cmd_vmx_vmx_c_sources_os_plan_79f02e322172

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/vmx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/vmx.c

## Role

`vmx.c` is the main coordinator for 9front's `vmx` virtual machine runner. It opens the Plan 9 `#X` VM device, builds the guest physical memory map, attaches backing segments, loads the kernel, initializes emulated devices, and runs the VM event loop.

## Major Responsibilities

- Opens `#X/clone` and the per-VM `regs`, `map`, and `wait` files.
- Maintains a lazy register cache over the `regs` file through `rget()`, `rpoke()`, `rcflush()`, and typed helpers.
- Creates non-overlapping `Region` records for guest RAM, VGA, reserved BIOS areas, and optional framebuffer regions.
- Maps guest physical regions into a Plan 9 segment, writes the VM memory map to `#X/.../map`, and exposes helpers like `gptr()`, `gpa()`, `gavail()`, and `gend()`.
- Posts guest exceptions with `postexc()`.
- Launches/resumes execution by flushing dirty registers and writing `go` to the control file.
- Runs a three-source event loop: VM exits from `wait`, timer ticks from `sleeperproc`, and deferred main-thread notifications from `sendnotif()`.
- Parses command-line options for RAM size, serial ports, block devices, NICs, framebuffer/VGA mode, 9P service name, shared segment name, debug, and I/O debug masks.
- Initializes CPU ID filtering, PCI, VGA, virtio/IDE devices, optional 9P, optional kernel configuration callback, then enters `runloop()`.

## Key Data And Control Flow

- `mmap` is the global linked list of physical memory `Region` records.
- `segname` and `segrclose` control the host segment backing guest RAM.
- `ctlfd`, `regsfd`, `mapfd`, and `waitfd` are the VM device control surface.
- `waitch`, `sleepch`, and `notifch` serialize VM exits, periodic device clock work, and callback execution into the main loop.
- `getexit` tracks outstanding VM executions so the event loop knows when it can relaunch.

## Notable Limitations And Risk Areas

- `mkregion()` rejects overlap and alignment problems eagerly; callers must build the physical map in correct order.
- The register cache stores pointers into static load buffers for existing register names and direct string pointers for newly poked names; lifetime expectations matter.
- `rcflush(1)` formats dirty registers into a command-line fragment for `go`, while `rcflush(0)` writes newline-separated updates to `regsfd`.
- Timer behavior depends on `nanosec()` and a polling fallback interval; device timers are advanced cooperatively.
- `sendnotif()` runs callbacks immediately on the main thread and otherwise queues them, so callbacks must be safe under the VM event-loop locking model.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/vmx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/vmxgdb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/vmxgdb.c

## Role

`vmxgdb.c` is a small GDB remote serial protocol bridge for an already-mounted `vmx` instance. It reads GDB packets from standard input/output and answers a minimal set of register and memory queries by reading `/n/vmx/xregs` and `/n/vmx/mem`.

## Protocol Behavior

- `rpack()` waits for `$...#csum` packets, handles escaped bytes, validates checksums unless no-ack mode is active, and sends `+` or `-` acknowledgements.
- `wpack()` emits escaped response packets and retransmits on `-` unless no-ack mode is active.
- Supports `qSupported` with `PacketSize=4096;QStartNoAckMode+`.
- Supports `QStartNoAckMode`.
- Supports `?` with a fixed `S00`.
- Supports `g` by returning the x86 register packet.
- Supports `mADDR,LEN` memory reads, capped at 65536 bytes.
- Treats `H` thread-selection packets by reinterpreting the second byte as a simple packet.

## Register And Memory Mapping

- `regpacket()` maps GDB i386-style register order to `ax`, `cx`, `dx`, `bx`, `sp`, `bp`, `si`, `di`, `pc`, `flags`, `cs`, `ss`, `ds`, `es`, `fs`, and `gs`.
- Segment register values are forced to zero in the emitted packet.
- `memread()` parses hexadecimal address/count pairs, clears the sign bit to avoid negative Plan 9 file offsets, reads from `memfd`, and hex-encodes bytes.

## Notable Limitations And Risk Areas

- The implementation is read-only: no register writes, memory writes, continue, step, breakpoints, or thread model.
- It assumes `vmxroot` is `/n/vmx`.
- `memread()` reverses through the read buffer when hex-encoding in place; this relies on the destination allocation being twice the requested count.
- Unsupported packets get an empty response, which is acceptable for many GDB feature probes but limited for active debugging.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/vmxgdb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/x86.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/x86.c

## Role

`x86.c` provides guest virtual-memory access and a partial x86 instruction decoder/interpreter used by `vmx` for emulating guest memory operations, especially around EPT/MMIO fault handling in adjacent VM-exit code.

## Address Translation

The file implements several translator paths selected by guest control registers:

- Flat translation when paging is disabled.
- 32-bit non-PAE page-table walking, including 4 MiB pages when `Cr4Pse` is set.
- 64-bit PML4/PDP/PD/PT walking, including 1 GiB and 2 MiB large pages.
- PAE translation is stubbed and reports that it is not implemented.

`vmemread()` and `vmemwrite()` marshal virtual memory reads/writes through `sendnotif()` so the actual translation and physical memory access run in the VM main-thread context.

## x86 Access Semantics

`x86access()` combines:

- Address-size truncation.
- Segment base/limit/permission checks.
- Canonical-address checks in 64-bit address mode.
- Page translation and page-fault synthesis.
- User/supervisor and writable-page enforcement.
- Optional TLB caching for repeated accesses.
- Fast direct host-memory load/store for contiguous mapped regions.
- Slow per-byte access across physical pages or MMIO-backed `Region` callbacks.

It posts `#gp`, `#ss`, or `#pf` exceptions unless called with `ACCSAFE`.

## Instruction Decode And Execution

The decoder is table-driven for a subset of x86 instructions that matter for memory and simple ALU emulation:

- Prefix handling for lock, repeat, operand-size, address-size, and segment override.
- ModRM/SIB/displacement/immediate parsing.
- Register, segment, immediate, and memory operand decoding.
- Implemented operations include `mov`, string `stos/lods/movs`, arithmetic/logical `add/adc/sub/sbb/cmp/and/or/xor`, and `push/pop`.
- `alu()` computes common status flags for arithmetic and logic.
- Unsupported instructions are disassembled through the Plan 9 `mach` layer in `giveup()` and reported as unimplemented.

## Important Dependencies

- Register access is delegated to `rget()`, `rset()`, `rgetsz()`, and `rsetsz()` from the VM core.
- Physical mappings use `gptr()`, `regptr()`, and `Region.mmio`.
- Exception injection uses `postexc()`.
- Register names and segment indexes are declared in `x86.h` and defined elsewhere in the VMX subsystem.

## Notable Limitations And Risk Areas

- PAE paging is not implemented.
- `x86step()` currently fixes `step.mode` to 4-byte mode, so 64-bit instruction semantics are not fully decoded even though 64-bit page translation exists.
- The instruction subset is intentionally incomplete; unsupported operations fail back through `giveup()`.
- Memory permissions and exception codes are synthesized manually, so subtle architectural differences may matter for unusual guests.
- The decoder prints each stepped instruction, which is useful for diagnostics but noisy in normal emulation paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/x86.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/x86.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/x86.h

## Role

`x86.h` defines small x86 architectural constants and helpers shared by the VMX x86 emulation code.

## Contents

- GDT descriptor construction macros for type, limit, base, and privilege level.
- GDT attribute constants for readable/writable/executable descriptors, TSS, accessed, expand-down/conforming, present, 64-bit, 32-bit, and granularity bits.
- Control-register feature bits used by translation: paging, PSE, PAE, OSXSAVE, and EFER long-mode enable.
- External register-name arrays `x86reg[16]` and `x86segreg[8]`.
- EFLAGS condition bits for carry, parity, auxiliary carry, zero, sign, and overflow.

## Notable Limitations And Risk Areas

- It is a constants header only; correctness depends on the adjacent code using the descriptor and flag bit positions consistently.
- The comment beside `GDTRW` appears malformed, but the macro value itself is still syntactically usable.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vmx/x86.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/auth.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/auth.c

## Role

`auth.c` implements RFB/VNC version negotiation and authentication for both the VNC viewer and server programs.

## Client-Side Behavior

- `vnchandshake()` reads the server version banner, accepts RFB 3.3, 3.7, 3.8, Darwin 3.889, and 4.0 as compatible variants, then responds as RFB 3.8.
- `vncauth()` negotiates authentication according to the selected protocol version.
- For RFB 3.3 it reads a single authentication type; for newer versions it scans the offered list and selects the highest supported type up to VNC auth.
- Supports no-auth and classic VNC challenge-response.
- Uses Plan 9 factotum via `auth_respond()` and `auth_getkey` with `proto=vnc role=client`.

## Server-Side Behavior

- `vncsrvhandshake()` sends an RFB 3.3 banner and reads the client banner.
- `vncsrvauth()` creates a VNC challenge with `auth_challenge()`, writes the challenge, reads the response, validates it through factotum, and sends VNC auth status.

## Notable Limitations And Risk Areas

- Server-side negotiation is fixed to RFB 3.3 style.
- Client-side auth chooses only no-auth or VNC auth, ignoring stronger modern security types.
- TLS, when used by callers, is outside this file.
- Authentication errors are propagated with `werrstr()` or fatal server messages depending on side.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/chan.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/chan.c

## Role

`chan.c` implements a user-space subset of Plan 9 kernel channel and canonical-name management for the VNC server's synthetic device filesystem.

## Core Behavior

- `newchan()` allocates and initializes a `Chan`.
- `cclose()` decrements channel references, calls the owning device's close method on last close, and frees the channel.
- `cclone()` clones a channel by issuing a zero-element device walk and sharing the canonical name.
- `Ref` helpers `incref()` and `decref()` provide lock-protected reference counting.
- `newcname()`, `cnameclose()`, `addelem()`, and `cleancname()` manage copy-on-write path names.
- `isdir()` validates directory channels and raises `Enotdir`.

## Notable Limitations And Risk Areas

- This is a narrow compatibility layer, not the full Plan 9 kernel name system.
- `cclone()` depends on each `Dev.walk` correctly supporting a zero-name clone operation.
- `addelem()` only normalizes on `..`, so callers rely on earlier path parsing discipline for other cases.
- Device close errors are swallowed after `waserror()`, matching kernel-like cleanup expectations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/chan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/color.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/color.c

## Role

`color.c` chooses the viewer-side pixel format advertised to the VNC server and installs conversion functions when the local Plan 9 display format is not directly usable over RFB.

## Main Behavior

- Converts Plan 9 draw channel descriptors into VNC `Pixfmt` fields.
- Supports 24-bit local screens by requesting 32 bpp from the server and dropping the unused byte.
- Supports CMAP8 displays in two emulation modes:
  - 12-bit RGB packed into 16 bpp with `RGB12` and a lookup table to CMAP8.
  - 8-bit BGR332 with a lookup table to CMAP8.
- Sets `cvtpixels` when a per-pixel conversion is needed.
- Sends an `MPixFmt` message to the server after selecting the format.

## Notable Limitations And Risk Areas

- Only byte-aligned local depths are accepted.
- Failure to discover red, green, and blue channels is fatal.
- CMAP conversion intentionally loses precision in the BGR332 path.
- Conversion is designed for little-endian VNC pixel streams.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/color.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/compat.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/compat.c

## Role

`compat.c` supplies user-space replacements for Plan 9 kernel services used by the VNC server's transplanted device code.

## Main Services

- Initializes process-local `up`, `eve`, rendezvous state, and kernel date with `initcompat()`.
- Provides `newup()` and `kproc()` to create kernel-like process records for child processes.
- Implements `panic()`, `smalloc()`, `seconds()`, `error()`, `nexterror()`, and `readstr()`.
- Maps open modes with `openmode()`.
- Implements `Rendez` sleep/wakeup with Plan 9 `rendezvous()` and interrupt state in `Proc`.
- Provides `rendintr()` and `rendclearintr()` for interrupting blocking pseudo-kernel sleeps.
- Tracks `waserror()` nesting through `errdepth()`.

## Notable Limitations And Risk Areas

- `kproc()` uses `rfork(RFPROC|RFMEM|RFNOWAIT)`, so child processes share memory and require careful locking.
- Error handling depends on `up` being initialized per process before any `waserror()`/`error()` usage.
- Rendezvous code uses sentinel values and panics on mismatches except for the global interrupt tag case.
- `panic()` exits the process instead of attempting recovery.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/compat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/compat.h

## Role

`compat.h` declares the kernel-like compatibility API and data structures used by the VNC server's synthetic Plan 9 devices and 9P exporter.

## Main Definitions

- `Ref`, `Rendez`, `Chan`, `Cname`, `Dev`, `Dirtab`, `Walkqid`, and `Proc`.
- `Dev` function table matching Plan 9 device entry points: reset, init, attach, walk, stat, open, create, close, read, write, remove, and wstat.
- Channel flags such as `COPEN` and `CFREE`.
- Error stack constants and `waserror()`/`poperror()` macros.
- Externs for `up`, `eve`, `devtab`, device helpers, channel helpers, rendezvous helpers, exporter/mounter helpers, shutdown, and screen initialization.

## Notable Limitations And Risk Areas

- It exposes a compact subset of kernel structures, so code ported from kernel space may require adaptation if it expects fields not represented here.
- The `Rendez` name is remapped through a macro to avoid namespace collision.
- `waserror()` increments `nerrlab` before `setjmp`; balancing with `poperror()` is critical.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/compat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/dev.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/dev.c

## Role

`dev.c` implements common Plan 9 device helper routines for the user-space VNC server device filesystem.

## Main Behavior

- `mkqid()` fills `Qid` fields.
- `devno()` maps device character identifiers to entries in `devtab`.
- `devdir()` and `devgen()` build directory entries from `Dirtab` records.
- `devattach()` creates a root channel for a device.
- `devclone()` copies channel metadata for walk operations.
- `devwalk()` implements generic walking through static/generated device directory entries.
- `devstat()` and `devdirread()` implement generic stat and directory read operations.
- `devpermcheck()` and `devopen()` enforce simple owner/eve/other permissions and open-mode constraints.
- Default create, remove, wstat, block read, and block write handlers reject unsupported operations.

## Notable Limitations And Risk Areas

- Permission checking is simplified around `up->user` and `eve`.
- `devdirread()` uses variable-length `convD2M()` entries and returns `-1` when the caller buffer cannot hold the first entry.
- Device-specific generators must follow the expected `-1`, `0`, `1` convention.
- `devwalk()` can return partial walks with no cloned channel, matching 9P walk semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/dev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/devcons.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/devcons.c

## Role

`devcons.c` implements a minimal `/dev/cons`, `/dev/consctl`, and `/dev/snarf` device for the VNC server's private Plan 9 namespace.

## Device Surface

The `consdevtab` exposes:

- Directory root.
- `cons`: writable console output, rendered through `screenputs()`.
- `consctl`: control file placeholder; most behavior is unimplemented.
- `snarf`: shared clipboard buffer.

## Clipboard Handling

- `Snarf snarf` stores the global clipboard buffer, size, and version.
- `setsnarf()` replaces the buffer, increments the version, and updates the directory entry qid version for change detection.
- Opening `snarf` for writing allocates a temporary `Snarf` in `Chan.aux`.
- Closing a write-open snarf file atomically replaces the global snarf buffer with the accumulated data.

## Notable Limitations And Risk Areas

- Reading from `cons` and writing to `consctl` raise placeholder errors.
- `snarf` writes are append-only per open and capped by `MAXSNARF`, but the size check happens before adding the next chunk.
- Ownership and permissions are those supplied through the generic device framework.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/devcons.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/devdraw.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/devdraw.c

## Role

`devdraw.c` implements a user-space Plan 9 `/dev/draw` device over `memdraw`/`memlayer` for the VNC server. It lets the private desktop command use normal Plan 9 draw protocol operations while dirty-screen tracking feeds the VNC update path.

## Device Model

- Exposes `#i/draw/new`, per-client directories, and per-client `ctl`, `data`, `refresh`, and `colormap` files.
- Tracks draw clients in `sdraw.client[]`.
- Tracks images as `DImage` hash chains per client.
- Tracks public/named images through `DName`.
- Tracks screens/windows through `DScreen` and per-client `CScreen` links.
- Keeps the real backing screen image in `screenimage` and installs it as image id 0 for new clients.

## Image And Screen Management

- `makescreenimage()` attaches to the VNC memory screen from `screen.c`, wraps it as a `Memimage`, names it, and creates the root `DImage`.
- `drawinstall()` and `drawuninstall()` add/remove client image ids.
- `drawinstallscreen()` creates or attaches to a `Memscreen`.
- `drawfreedimage()` and `drawfreedscreen()` handle references across images, named images, screen fill images, and window layers.
- `drawaddname()`, `drawlookupname()`, and `drawgoodname()` implement named-image lifetime validation.

## Dirty Tracking And Refresh

- `dstflush()` determines whether a draw destination affects the visible VNC screen and adds a dirty rectangle.
- `addflush()` forwards dirty regions to `flushmemscreen()` with VNC-oriented handling.
- `drawflush()` emits pending dirty rectangles.
- Layer refresh callbacks collect refresh rectangles for clients using refresh messages.
- `drawwakeall()` wakes clients blocked on refresh reads.

## Supported Draw Protocol Messages

`drawmesg()` supports the core Plan 9 draw data protocol, including:

- Allocate image (`b`) and screen (`A`).
- Affine warp (`a`).
- Repl/clip changes (`c`).
- Draw (`d`) with compositing operator state (`O`).
- Ellipse/arc (`e`/`E`), line (`L`), polygon/fill polygon (`p`/`P`), string/stringbg (`s`/`x`).
- Free image/screen (`f`/`F`).
- Font initialization and glyph load (`i`/`l`).
- Attach/name images (`n`/`N`).
- Window origin and stacking (`o`/`t`).
- Image read (`r`) and image load/compressed load (`y`/`Y`).
- Visibility flush (`v`) and debug no-op (`D`).

## Notable Limitations And Risk Areas

- This is a substantial in-process graphics server; reference-count correctness is central to avoiding stale images and leaked layers.
- Named images are invalidated by version checks, and old names produce `Eoldname`.
- Screen resizing is intentionally constrained once draw clients have existed.
- Many operations assume all callers hold `drawlock`; the code mixes blocking refresh waits with lock release/reacquire.
- Dirty rectangle handling is tuned for VNC and differs from a pure bounding-box flush strategy.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/devdraw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/devmouse.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/devmouse.c

## Role

`devmouse.c` implements a minimal `/dev/mouse`, `/dev/cursor`, `/dev/mousein`, and `/dev/mousectl` device for the VNC server's private desktop.

## Device Behavior

- Maintains global `Mouseinfo mouse` and `Cursorinfo cursor`.
- Exposes a default arrow cursor and supports writing cursor image data to `/dev/cursor`.
- Allows only one open reader for `/dev/mouse`.
- `mouseread()` blocks with `rendsleep()` until movement, button, or resize state changes, then returns Plan 9 mouse event records.
- `mousewrite()` on `/dev/mouse` parses warp coordinates and calls `absmousetrack()` and `mousewarpnote()`.
- `absmousetrack()` clamps coordinates to `gscreen->clipr`, updates state, queues button transitions, wakes mouse readers, and turns the cursor on.
- `mouseresize()` marks a resize event and wakes readers.

## Notable Limitations And Risk Areas

- `mousein` and `mousectl` are present but intentionally raise placeholder errors on open.
- Button-transition queue overflow drops extra transition events until a reader drains the queue.
- Cursor updates directly affect the global screen cursor and rely on `screen.c` drawing logic.
- Mouse tracking is ignored before `gscreen` exists.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/devmouse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/draw.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/draw.c

## Role

`draw.c` is the VNC viewer's framebuffer update decoder and local screen updater. It sends preferred encodings and framebuffer update requests, then decodes server-to-client rectangle updates into the Plan 9 draw window.

## Encoding Negotiation And Requests

- `sendencodings()` parses the `encodings` string and sends `MSetEnc`.
- Supported names include raw, copyrect, RRE, CoRRE, hextile, mousewarp, desktopsize, and xdesktopsize.
- `requestupdate()` flushes the local display, optionally sends extended desktop resize state, and requests full or incremental updates.

## Update Decoding

- Maintains decompression buffers `pixbuf` and `linebuf`.
- Handles raw pixel rectangles, copyrect, RRE, CoRRE, hextile, cursor/mouse warp, and desktop-size pseudo-encodings.
- `loadbuf()` reads pixel data, applies conversion through `cvtpixels` if needed, and optionally scales pixels for autoscale mode.
- `updatescreen()` clips to local display size and uses `loadimage()` into the Plan 9 screen.
- `dohextile()` decodes hextile tiles with background, foreground, subrect, and colored-subrect flags.
- Clipboard messages delegate to `writesnarf()`.

## Notable Limitations And Risk Areas

- Bad rectangles or unknown encodings are fatal.
- Autoscale uses simple nearest-neighbor style in-buffer scaling and depends on current screen/window dimensions.
- Pixel buffer sizing follows the remote framebuffer dimensions; large remote screens can allocate large buffers.
- Some resize paths depend on server support for desktop-size pseudo-encodings.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/draw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/error.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/error.h

## Role

`error.h` declares common Plan 9-style error-string globals used by the VNC server compatibility and device layers.

## Contents

It declares errors for mount state, lookup, directory/file type mismatches, permissions, bad arguments, I/O, hung-up channels, resource exhaustion, interrupts, malformed stats, and other kernel-like conditions.

## Relationship To Code

- `compat.c`, `dev.c`, `chan.c`, `devcons.c`, `devmouse.c`, `devdraw.c`, and `exportfs.c` raise these strings through `error()`.
- The definitions live in `errstr.h`.

## Notable Limitations And Risk Areas

- These are global character arrays, not enum codes; callers compare and propagate textual errors.
- The set is only what the user-space VNC device environment needs, not a full kernel error catalog.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/error.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/errstr.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/errstr.h

## Role

`errstr.h` defines the Plan 9-style error strings declared by `error.h`.

## Contents

The file initializes global `char[]` variables for common kernel/device errors such as nonexistence, permission denied, bad argument, I/O error, hung-up channel, no memory, interrupted operation, bad stat buffer, and related conditions.

## Relationship To Code

- Included by `compat.c` to provide exactly one definition site for the error globals.
- Other files include `error.h` to reference them.

## Notable Limitations And Risk Areas

- Because this header contains definitions rather than declarations, it must only be included in one translation unit.
- Error identity is textual; changing these strings can affect user-visible 9P errors and any string comparisons.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/errstr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/exporter.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/exporter.c

## Role

`exporter.c` wires the synthetic device table into a mountable 9P service for the VNC server's private namespace.

## Main Behavior

- `mounter()` mounts each exported root onto a target mount point using numeric attach names.
- `exporter()` initializes each requested device, attaches its root channel, creates a pipe, returns both pipe ends, and starts an exporter process.
- `extramp()` runs in a new name group, calls `sysexport()` over the pipe, invokes `shutdown()`, and exits when export ends.

## Notable Limitations And Risk Areas

- `Exporter ex` is stack-allocated in `exporter()` and passed to `kproc()`; this relies on the child using it before the parent stack frame becomes invalid.
- Mounting switches from `MREPL` to `MAFTER` after the first mount to layer multiple roots.
- Export failure eventually triggers global VNC server shutdown.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/exporter.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/exportfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/exportfs.c

## Role

`exportfs.c` implements a compact concurrent 9P2000 server over the VNC server's synthetic `Dev` roots. It translates incoming 9P messages to `Chan` operations.

## Architecture

- `Export` owns the I/O fd, root channels, negotiated iounit, active work list, and fid hash table.
- `Fid` tracks a 9P fid, associated `Chan`, reference count, offset, and attached/clunked state.
- `Exq` is a queued request with message buffer, decoded `Fcall`, response suppression, and slave identity.
- Global `Exwork exq` queues requests across exporters and spawns worker processes as needed.

## Request Handling

- `sysexport()` builds an `Export` and runs `exportproc()`.
- `exportproc()` reads 9P messages, handles `Tflush` specially, queues other work, and starts `exslave()` workers.
- `exslave()` dequeues work, marks it in-progress for flush/shutdown visibility, dispatches through the `fcalls[]` table, encodes responses, and writes them unless flushed.
- `exflush()` can remove unstarted work or mark in-progress work as no-response and interrupt its worker.
- `exshutdown()` removes queued work and interrupts active work when the connection ends.

## Implemented 9P Operations

- `Tversion`: negotiates `9P2000` and clamps message size.
- `Tauth`: rejects auth as not required.
- `Tattach`: attaches to one of the exported roots by numeric attach name.
- `Twalk`: delegates to the device walk method and handles cloned fids.
- `Topen`, `Tcreate`, `Tread`, `Twrite`, `Tstat`, `Twstat`, `Tclunk`, and `Tremove`: delegate to the corresponding device methods with fid lifecycle handling.

## Notable Limitations And Risk Areas

- The fid table uses a small fixed hash size and manual reference bookkeeping.
- `Tread` stores `rpc->offset` in a `long`, so very large offsets are narrowed.
- `Tflush` may suppress a response after the worker has already written; the code accepts this race by design.
- Worker interruption depends on the compatibility-layer rendezvous interrupt mechanism.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/exportfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/kbd.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/kbd.h

## Role

`kbd.h` declares shared keyboard and clipboard state for the VNC server and viewer support files.

## Contents

- Defines `Snarf`, a qlock-protected clipboard buffer with version, byte count, and buffer pointer.
- Defines `MAXSNARF` as 100 KiB.
- Declares global `snarf` and `kbdin`.
- Declares `screenputs()`, `vncputc()`, and `setsnarf()`.

## Notable Limitations And Risk Areas

- `Snarf` ownership is manual: callers must know when `setsnarf()` takes ownership of a buffer.
- `kbdin` is a process-global file descriptor used by VNC key injection.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/kbd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/kbds.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/kbds.c

## Role

`kbds.c` converts incoming VNC/X11 keysyms into Plan 9 keyboard events for the VNC server's private `/dev/kbdin`.

## Main Behavior

- Provides a `vnckeys[]` table for VNC special keysyms in the `0xff00` range.
- Maps common special keys to Plan 9 runes such as arrows, home/end, page up/down, shift/control/alt, delete, escape, and keypad symbols.
- Uses `ksym2utf.h` to map X11 keysyms to Unicode runes.
- `vncputc()` writes null-terminated `r%C` key-down or `R%C` key-up records to `kbdin`.

## Notable Limitations And Risk Areas

- Unknown special keysyms are ignored.
- Mapping coverage is limited to the included tables and explicit special-key table.
- Writes are skipped when `kbdin` is negative.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/kbds.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/kbdv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/kbdv.c

## Role

`kbdv.c` converts local Plan 9 keyboard input into VNC key events for the viewer.

## Main Behavior

- Maps Plan 9 special runes to X11 keysyms through `ktab`.
- Uses `utf2ksym.h` to convert Unicode runes to X11 keysyms where needed.
- `keyevent()` writes `MKey` messages with key symbol and down/up state.
- `readcons()` is a fallback path for systems without `/dev/kbd`; it opens `display->devdir/cons`, enables raw mode, tracks toggled modifiers, and sends key down/up pairs.
- `readkbd()` reads structured `/dev/kbd` records and sends key down/up events based on `k`, `K`, and `c` records.
- `runetovnc()` converts a Plan 9 rune to the keysym value sent to the remote server.

## Notable Limitations And Risk Areas

- Modifier handling differs between `/dev/kbd` and raw console fallback.
- Uppercase and shifted punctuation may synthesize a shift press for compatibility with some servers.
- Control-character handling emits explicit control key press/release sequences.
- The code intentionally suppresses character events when modifier keys are active in the `/dev/kbd` path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/kbdv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/ksym2utf.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/ksym2utf.h

## Role

`ksym2utf.h` is a static lookup table mapping X11/VNC keysyms to Unicode runes for server-side keyboard input conversion.

## Contents

- Defines `static ulong ksym2utf[]`.
- Covers Latin extended characters, Japanese kana, Arabic/Persian, Cyrillic, Greek, mathematical symbols, box drawing, typographic symbols, Hebrew, Thai, Korean Jamo, Armenian, Georgian, Vietnamese, currency symbols, and other X11 keysym ranges.
- Used by `kbds.c` to translate incoming VNC key symbols into Plan 9 runes before writing `/dev/kbdin`.

## Notable Limitations And Risk Areas

- This is sparse designated-initializer data; unmapped entries default to zero and are treated as unsupported.
- It is not a full Unicode keyboard layout engine; it only maps the keysyms listed.
- Some symbols can have multiple possible X11 keysym origins, so reverse mapping is not always one-to-one.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/ksym2utf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/proto.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/proto.c

## Role

`proto.c` implements shared RFB/VNC binary protocol read/write primitives over Plan 9 buffered I/O.

## Main Behavior

- `vncinit()` initializes `Biobuf` readers/writers and stores network/control fds in `Vnc`.
- `vncterm()` closes buffered streams.
- Provides big-endian readers/writers for bytes, shorts, longs, points, rectangles, compact rectangles, pixel formats, and strings.
- `vncrdstringx()` bypasses `Biobuf` for server-side negotiation cases where later protocol wrappers need direct fd access with no buffered data.
- `vncflush()`, `vncrdbytes()`, and `vncwrbytes()` detect I/O failure and call `vnchungup()`.
- `vnclock()` and `vncunlock()` serialize writes through the embedded `QLock`.
- `vncgobble()` discards a fixed number of incoming bytes.

## Notable Limitations And Risk Areas

- Most read/write failures are converted into `vnchungup()` rather than returned as errors.
- `vncrdstring()` allocates `len+1` without a local maximum; callers trust protocol sizes.
- `vncrdstringx()` asserts no buffered input before direct reads.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/proto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/rlist.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/rlist.c

## Role

`rlist.c` maintains a compact list of dirty rectangles for VNC framebuffer updates.

## Main Behavior

- `growrlist()` expands the rectangle array and enforces a global `tot` cap of 10000 allocated rectangle slots.
- `addtorlist()` adds a rectangle to an `Rlist` while trying to merge, trim, or split against existing rectangles.
- Handles covered rectangles, covering rectangles, aligned merges, edge subtraction, corner overlap splitting, and band splitting.
- Maintains `bbox` as the overall bounding box.
- `freerlist()` releases storage and updates the global allocation counter.

## Notable Limitations And Risk Areas

- Complex overlaps outside the handled cases call `abort()`.
- The rectangle budget is global, not per-client.
- `bbox` is updated before the merge/split process and may remain a conservative bounding box.
- The debug `main()` is only compiled under `REGION_DEBUG`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/rlist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/rre.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/rre.c

## Role

`rre.c` implements VNC server-side framebuffer rectangle encoders: raw, RRE, CoRRE, and hextile.

## Encoding Paths

- `sendraw()` sends uncompressed pixel data from the backing `Memimage`.
- `sendrre()` and `sendcorre()` split large rectangles into bounded tiles, choose a background color, encode uniform-color subrectangles, and fall back to raw if compressed form would exceed the budget.
- `sendhextile()` splits into 16x16 tiles, selects background/foreground reuse flags, emits raw tiles when compact encoding is not beneficial, and handles colored-subrect hextile mode.
- `count*()` functions estimate how many RFB rectangles each encoding path will emit.

## Core Algorithms

- `findback()` samples pixels to estimate the most common background color.
- `hexcolors()` determines whether a hextile tile has background only, background plus one foreground, or multiple foreground colors.
- `encrre()` greedily finds tall, maximally wide uniform-color rectangles, marks covered pixels, and writes encoder-specific rectangle records.
- `eqpix8()`, `eqpix16()`, and `eqpix32()` compare pixels for supported depths.

## Notable Limitations And Risk Areas

- Only 8, 16, and 32 bpp get compressed encoders; other depths fall back to raw.
- Encoding is heuristic, not optimal.
- Raw fallback is used on allocation failure or when encoded rectangle budgets are exceeded.
- The code assumes image stride can be expressed cleanly in whole pixels for the selected depth.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/rre.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/screen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/screen.c

## Role

`screen.c` implements the VNC server's in-memory screen, console text rendering, cursor rendering, and screen attachment hooks used by `/dev/draw`.

## Screen Setup

- `screeninit()` initializes `memdraw`, allocates `gscreen` with the requested size and channel, creates cursor mask images, builds a cursor color image, initializes a console window, and installs the arrow cursor.
- `screenwin()` draws a simple Plan 9 console area with a title and initializes cursor/text positions.
- `attachscreen()` exposes the `gscreen` `Memdata`, channel, depth, width, rectangle, and softscreen flag to `devdraw.c`.

## Cursor Handling

- `setcursor()` copies cursor bitmaps and increments `cursorver`.
- `cursorrect()` computes the visible cursor rectangle from `cursorpos` and offset.
- `cursordraw()` converts cursor bitmaps into `Memimage` masks and composites cursor set/clear masks onto a destination.
- `cursoron()` tracks current mouse position; `cursoroff()` moves it offscreen.

## Console Rendering

- `screenputs()` decodes UTF-8 fragments, serializes through `drawlock`, calls `screenputc()`, and flushes dirty regions.
- `screenputc()` handles newline, carriage return, tab, backspace, null, and printable runes.
- `scroll()` scrolls the console text area by eight font heights.
- Dirty regions are accumulated in `flushr` and sent through `flushmemscreen()`.

## Notable Limitations And Risk Areas

- `getcolor()` and `setcolor()` are stubs, so colormap operations are effectively inert for this screen implementation.
- Console rendering is basic and primarily supports command output in the private VNC desktop.
- Cursor drawing depends on shared globals from `devmouse.c`.
- `screeninit()` raises compatibility-layer errors rather than returning error codes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/screen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/screen.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/screen.h

## Role

`screen.h` declares the VNC server in-memory screen, cursor, mouse, and draw-device integration surface.

## Contents

- Declares `Cursorinfo`, global `cursor`, `arrow`, `gscreen`, `cursorver`, and `cursorpos`.
- Declares cursor operations, screen flush/attach/delete/reset operations, color hooks, blanking, mouse tracking, and `fsinit()`.
- Declares global `drawlock` and `drawactive()`.
- Defines `TK2SEC(x)` as zero and `ishwimage(i)` as zero for this user-space softscreen environment.

## Notable Limitations And Risk Areas

- Some declarations are compatibility placeholders for code adapted from kernel/drawterm contexts.
- `ishwimage()` always false, so draw paths avoid hardware-image special behavior except where guarded separately.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/screen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/utf2ksym.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/utf2ksym.h

## Role

`utf2ksym.h` is a static lookup table mapping Unicode runes to X11/VNC keysyms for viewer-side keyboard event generation.

## Contents

- Defines `static ulong utf2ksym[]`.
- Covers many of the same character families as `ksym2utf.h`: Latin extended, Japanese kana, Arabic/Persian, Cyrillic, Greek, symbols, Hebrew, Thai, Korean Jamo, Armenian, Georgian, Vietnamese, and currency symbols.
- Used by `kbdv.c` to convert Plan 9 keyboard runes into the keysyms expected by remote VNC servers.

## Notable Limitations And Risk Areas

- The reverse mapping cannot preserve all duplicates from `ksym2utf.h`; where multiple keysyms map to one rune, one mapping wins.
- Unmapped runes are sent as their rune value or through explicit special-key tables.
- This is static keysym conversion, not locale-aware keyboard layout processing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/utf2ksym.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/vnc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/vnc.h

## Role

`vnc.h` is the shared public header for the VNC viewer/server protocol code.

## Main Definitions

- `Colorfmt`, `Pixfmt`, and `Vnc`.
- `Vnc` embeds a `QLock`, network/control fds, input/output `Biobuf`s, framebuffer dimensions, pixel format, client-side server metadata, resize capability, and one screen descriptor.
- Defines RFB constants for version length, auth types/statuses, message types, encoding numbers, pseudo-encodings, and hextile flags.
- Defines `Color` as a byte-storage comparison type.
- Declares auth, handshake, protocol read/write, string, rectangle, pixel-format, flush, lock, and hangup functions.

## Notable Limitations And Risk Areas

- The `Vnc` struct is shared by both viewer and server code; some fields are only meaningful on one side.
- Protocol constants include legacy and pseudo-encoding values with signed negative encodings represented as enum constants.
- Callers must hold `vnclock()` for multi-field writes that need to remain contiguous.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/vnc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/vncs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/vncs.c

## Role

`vncs.c` is the main VNC server program. It creates a private Plan 9 desktop, exports synthetic draw/mouse/cons devices into `/dev`, launches a command inside that namespace, listens for VNC clients, and streams framebuffer updates.

## Startup Flow

1. Parses options for certificate/TLS mode, display number, geometry, pixel format, network mount point, no-auth mode, kill mode, and verbosity.
2. Backgrounds into a new process/name/fd/note context.
3. Initializes compatibility state and creates the in-memory screen.
4. Exports `draw`, `mouse`, and `cons` devices through `exporter()` and mounts them before the real `/dev`.
5. Launches a child command, defaulting to interactive `rc`, after starting and synchronizing `kbdfs`.
6. Opens `/dev/kbdin` for keyboard injection.
7. Announces a VNC TCP service and accepts clients.

## Client Lifecycle

- `vncaccept()` forks a handler per client, optionally wraps the data fd in TLS, performs handshake/auth, handles shared/non-shared policy, sends initial framebuffer dimensions and pixel format, and forks reader/writer paths.
- `clientreadproc()` processes client messages: pixel format, colormap, encoding preferences, framebuffer requests, desktop resize, key events, mouse events, and cut text.
- `clientwriteproc()` periodically sends clipboard changes and framebuffer updates when the client has outstanding update requests.
- `vncclose()`, `killclients()`, `killall()`, `shutdown()`, and note handling coordinate cleanup.

## Framebuffer Update Model

- `flushmemscreen()` adds dirty rectangles to every client.
- `updateimage()` copies dirty screen regions into the client's pixel-format image, overlays cursor when needed, sends resize pseudo-rectangles, encoded framebuffer rectangles, and mouse-warp pseudo-rectangles.
- Encoding functions are selected from raw, RRE, CoRRE, or hextile based on the client's preference list.
- Clipboard is synchronized through the shared `snarf` version.

## Pixel Format Handling

- `chan2fmt()` converts Plan 9 channels to VNC pixel format for initial server advertisement.
- `fmt2chan()` converts client-requested `Pixfmt` back into a Plan 9 channel descriptor, including ignored padding bits where possible.
- Client image buffers are recreated when size or channel changes.

## Notable Limitations And Risk Areas

- Authentication defaults to VNC challenge-response unless `-A` disables it; stronger security depends on TLS option and external certificate setup.
- Pixel format changes are effectively expected once; comments note missing locking for repeated changes.
- Shared global `shared` is assigned from each client and also used as option state.
- The private desktop and client handlers are process-shared memory via `rfork(RFMEM)`, so locks around clients, draw state, and VNC writes are essential.
- Resizing rewrites `gscreen->clipr`, redraws the console, and resets the draw screen image; active draw clients constrain resizing behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/vncs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/vncs.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/vncs.h

## Role

`vncs.h` declares VNC server-side session and dirty-region structures plus encoder entry points.

## Main Definitions

- `Rlist`: dirty rectangle list with bounding box, capacity, count, and rectangle storage.
- `Vncs`: embeds `Vnc` and adds client list linkage, remote/net path strings, encoding callbacks, copyrect/warp/resize flags, update request counter, dirty region list, process lifecycle counters, cursor/snarf tracking, and per-client converted framebuffer image.

## Declared Functions

- RRE/raw/hextile/CoRRE count and send functions from `rre.c`.
- `addtorlist()` and `freerlist()` from `rlist.c`.

## Notable Limitations And Risk Areas

- `Vncs` is shared between multiple rforked processes for one client, so fields like `ndead`, `nproc`, and update state depend on locking discipline.
- Encoder callbacks must keep count/send results consistent; `vncs.c` disconnects the client if counts mismatch.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/vncs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/vncv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/vncv.c

## Role

`vncv.c` is the main VNC viewer program. It connects to a VNC server, negotiates protocol/authentication, opens a Plan 9 draw window, then runs separate loops for server updates, clipboard, keyboard, and mouse.

## Startup Flow

- Parses options for autoscale, CMAP8 12-bit mode, encodings, shared mode, TLS, verbosity, key pattern, and clipboard charset.
- Builds a network address from `host[:display]`, defaulting to TCP 5900 plus display or TLS base 35729.
- Dials the server and optionally wraps the data fd with `tlsClient()`.
- Runs client handshake and auth.
- Reads initial framebuffer size, pixel format, and desktop name.
- Initializes a draw window, chooses local/remote color format, sends encoding preferences, and opens mouse input.
- Forks worker processes for reading server updates, checking snarf, and reading keyboard; the main process reads mouse events.

## Shutdown

- Global `shutdown()` hangs up/ closes connection fds and posts notes to sibling processes.
- `vnchungup()` treats protocol closure as fatal.
- `pids[]` tracks the process group created by the viewer.

## Notable Limitations And Risk Areas

- TLS certificate verification is noted as a TODO and not enforced.
- `netmkvncaddr()` mutates the input server string when parsing `:display`.
- Viewer uses shared memory among worker processes, so `vnclock()` protects protocol writes.
- No reconnect behavior is implemented.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/vncv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/vncv.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/vncv.h

## Role

`vncv.h` declares viewer-side globals and cross-module functions.

## Contents

- Color conversion: `choosecolor()`, `cvtpixels`, `settranslation()`.
- Update handling: `sendencodings()`, `requestupdate()`, `readfromserver()`.
- Shared globals: `zero`, `charset`, `encodings`, `autoscale`, `bpp12`, `vnc`, and `mousefd`.
- Window/input/clipboard hooks: `adjustwin()`, `readkbd()`, `initmouse()`, `mousewarp()`, `readmouse()`, `senddim()`, `writesnarf()`, and `checksnarf()`.

## Notable Limitations And Risk Areas

- Some declarations, such as `settranslation()` and `senddim()`, are not implemented in the files in this group, suggesting compatibility leftovers or external/conditional definitions.
- The header exposes process-global viewer state used across rforked processes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/vncv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/wsys.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/wsys.c

## Role

`wsys.c` handles viewer-side integration with the local Plan 9 window system: resizing, mouse input, mouse warping, cursor display, and clipboard synchronization.

## Window And Mouse

- `adjustwin()` resizes the local window to fit the remote framebuffer or current screen bounds.
- `resized()` reacquires the draw window, adjusts size when appropriate, and requests a full update.
- `initmouse()` opens the local window mouse file.
- `readmouse()` installs a dot cursor, reads local mouse events, handles resize records, applies autoscale coordinate conversion, sends VNC mouse events, and releases wheel buttons after wheel motion.
- `mousewarp()` writes a local mouse warp request to the mouse file.

## Clipboard

- `tcs()` runs `/bin/tcs` for charset conversion when the configured charset is not UTF-8, falling back to fd duplication or `/bin/cat`.
- `gotsnarf()` tracks `/dev/snarf` qid version.
- `writesnarf()` receives remote cut text and writes local snarf through optional charset conversion.
- `getsnarf()` reads local snarf through optional conversion.
- `checksnarf()` polls once per second and sends `MCCut` when local snarf changes.

## Notable Limitations And Risk Areas

- Clipboard polling is periodic rather than event-driven.
- Charset conversion forks helper processes and uses `waitpid()` afterward.
- Autoscale coordinate conversion uses floating-point ratios and truncation.
- Mouse event parsing depends on fixed Plan 9 event record width.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vnc/wsys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vt/cons.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/vt/cons.h

## Role

`cons.h` declares shared terminal-emulator console state and screen/host I/O functions for the 9front `vt` command.

## Main Definitions

- `Consstate` tracks escape-state parser fields, argument buffer, saved cursor position, and key-state fields.
- Mode constants for newline/other and cooked/raw.
- Escape/parser state enum values such as base state, escape, CSI, OSC, charset, and title-related states.
- `ttystate` flags for ANSI and cursor-key behavior.
- `funckey` maps terminal key numbers to output strings, with external function-key tables for ANSI, application ANSI, VT220, and xterm modes.

## Declared Shared State

- Cursor and screen dimensions: `x`, `y`, `xmax`, `ymax`, `olines`.
- Parser state: `peekc`, `attribute`, `term`, `yscrmin`, `yscrmax`, `attr`, `defattr`.
- Color state: foreground/background images and normal/high color arrays.
- Runtime flags: `cursoron`, `nocolor`, and `bracketed`.
- OSC 7 current-directory buffer `osc7cwd`.

## Declared Operations

- Terminal emulation and input: `emulate()`, `host_avail()`, `nextchar()`, `sendnchars()`.
- Screen editing: `clear()`, `newline()`, `shift()`, `scroll()`, `backup()`, `drawstring()`.
- UI helpers: `ringbell()`, `pt()`, `pos()`, `funckey()`, `rewound()`, `setdim()`, and `mountcons()`.

## Notable Limitations And Risk Areas

- This header centralizes many globals used across `vt` implementation files, so state coupling is high.
- Multiple terminal behavior modes are selected by global tables and flags rather than per-instance objects.
- Correctness depends on implementation files keeping cursor bounds, scroll region, color state, and parser state synchronized.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/vt/cons.h -->