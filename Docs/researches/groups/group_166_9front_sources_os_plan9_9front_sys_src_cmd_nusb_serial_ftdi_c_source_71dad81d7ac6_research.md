# Group Research: group_166_9front_sources_os_plan9_9front_sys_src_cmd_nusb_serial_ftdi_c_source_71dad81d7ac6

Scope checked against `Docs/research_subset_a.md`: all files are within `sources/os/plan9/9front`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/serial/ftdi.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/serial/ftdi.c

## Role

Implements the FTDI USB serial backend for `nusb/serial`. It probes a large VID/PID table, identifies FTDI chip families, configures FTDI-specific USB control requests, and adapts FTDI packet framing to the generic `Serialops` interface.

## Main Behavior

The file defines extensive FTDI and FTDI-compatible product IDs, command constants, chip type constants, flow-control flags, status bits, packet header bits, and bit-bang/JTAG settings.

`ftprobe` matches the device with `ftinfo`, then calls `ftgettype` to infer chip type from device release number, number of interfaces, USB speed packet size, and product string. Multi-interface parts are treated as FT2232/FT4232 class devices, and devices whose product string contains `jtag` expose interface 0 as JTAG.

`ftsetparam` programs line data format, flow control, and baud divisor. Baud divisor calculation is split between SIO fixed baud codes, FT8U232AM-style divisors, and FT232BM/newer fractional divisors. Special 38400-baud custom divisor handling exists for Tira and USB-UIRT devices.

FTDI incoming data has a two-byte status header per USB packet. `cpdata` strips these headers and feeds modem/error status into the `Serialport`. For old SIO-style output headers, `ftsetouthdr` prepends the port/length byte.

## Concurrency And Data Path

`ftinit` resets the port, optionally configures JTAG latency/MPSSE bit mode, and starts `statusreader`. `statusreader` creates a buffered channel and starts `epreader`, which reads the bulk-in endpoint, strips FTDI headers, recovers from transient read failures, and pushes packets to waiters.

`wait4data` synchronizes with the reader using `w4data`/`gotdata` channels and serves buffered bytes to generic serial reads. `wait4write` writes through the bulk-out endpoint with any required FTDI output header.

## Integration Points

The exported `ftops` table supplies:

- initialization and endpoint max-packet setup
- generic endpoint discovery
- parameter setting
- pipe purge/reset
- modem line control
- flow control
- break control
- custom read/write wait handlers

## Notable Details

The implementation uses `ser->maxrtrans`, `ser->maxwtrans`, `ser->inhdrsz`, `ser->outhdrsz`, and `ser->baudbase` to communicate FTDI framing and timing constraints back to `serial.c`.

The JTAG path reuses the serial device framework but marks the port as `isjtag`, suppressing normal serial control handling in the generic layer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/serial/ftdi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/serial/prolific.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/serial/prolific.c

## Role

Implements the Prolific PL2303 USB serial backend for `nusb/serial`.

## Main Behavior

The file defines PL2303 chip revisions, class/vendor request constants, status bits, device control register values, pipe reset requests, and a broad VID/PID table for Prolific chips and rebadged phone/GPS/serial cables.

`plprobe` matches the device ID, marks that an interrupt endpoint is required, and installs `plops`.

`plinit` classifies the chip as H, HX, or unknown using revision ID and Linux-derived heuristics, runs the vendor initialization sequence, initializes DCR registers, reads line parameters, and starts a status reader process.

`plgetparam` and `plsetparam` use CDC line coding requests to read/write baud, stop bits, parity, and data bits. Unsupported 1.5 stop-bit state is reported as a warning.

## Status And Recovery

The interrupt endpoint is read by `statusreader` through `plreadstatus`. Status bytes update DCD, DSR, CTS, ring, and framing/parity/overrun counters. Non-timeout read errors call `serialrecover`.

`plclearpipes` uses vendor pipe reset requests for HX devices and endpoint unstalling for older variants.

## Integration Points

`plops` provides initialization, get/set parameters, pipe clearing, line control, hardware flow control, break control, max-packet setup, and generic endpoint discovery.

## Notable Details

The implementation distinguishes hardware flow-control bit patterns for H and HX variants. It also limits endpoint max packet size to 256 bytes because of output size encoding constraints.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/serial/prolific.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/serial/serial.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/serial/serial.c

## Role

Provides the generic `nusb/serial` 9P server and hardware-independent USB serial framework. Chip-specific backends plug in through `Serialops`.

## Main Behavior

`threadmain` opens the USB device, allocates `Serial`, probes supported backends in order (`ucons`, `ftdi`, `silabs`, `prolific`, `ch340`, `acm`), opens endpoints for each serial interface, initializes ports, names them `eiaU...` or `jtag...`, creates read/write request queues, and posts a share service named `<devid>.serial`.

The exposed file tree contains two files per port: a data file and a `ctl` file. Reads and writes on data files are queued and processed by `procread` and `procwrite`; `ctl` reads dump serial state and `ctl` writes parse Plan 9 serial control commands.

## Control Path

`serialctl` parses compact commands for baud, data bits, parity, stop bits, RTS/DTR, modem flow control, breaks, flushing, wait timer, and XON/XOFF writes. It drains output before parameter changes when needed, delegates hardware-specific operations through `Serialops`, and resets recovery state on success.

`serdumpst` formats current settings and error counters.

## Endpoint Handling

`findendpoints` finds bulk in/out endpoints and an optional interrupt endpoint. `openeps` opens endpoint devices, sets timeout/debug controls, applies backend endpoint tuning, and opens data file descriptors in read/write mode.

## Error Handling

`serialrecover` handles detached devices, endpoint unstalling, fatal channel closure, whole-device reset, and backend reset escalation based on the recovery counter. `serialreset` drains all ports and calls the backend reset hook.

## Integration Points

The server depends on backend-provided hooks for initialization, parameter handling, pipe recovery, line control, breaks, endpoint discovery, and optional custom read/write paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/serial/serial.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/serial/serial.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/serial/serial.h

## Role

Defines shared data structures, constants, and helper prototypes for the `nusb/serial` framework and its chip backends.

## Main Structures

`Serialops` is the backend operation table. It includes hooks for endpoint setup/discovery, initialization, get/set parameters, pipe clearing, reset, line control, modem control, break control, status reads, and custom read/write waiting.

`Serialport` stores per-port state: endpoint devices, control-line state, baud/format settings, modem state, error counters, interface number, read buffering, and 9P request queues.

`Serial` stores per-device state: USB device, backend driver name/type, recovery counter, operation table, number of interfaces, JTAG interface index, transfer sizes, FTDI-style header sizes, and baud base.

`Cinfo` is a simple VID/PID match entry with an optional backend-assigned ID.

## Constants And Prototypes

Defines shared buffer/interface limits, software flow control bytes, DTR/RTS bits, `serialdebug`, debug print macro, and helpers such as `serialrecover`, `serialreset`, `findendpoints`, `openeps`, `serdumpst`, and `matchid`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/serial/serial.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/serial/silabs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/serial/silabs.c

## Role

Implements the Silicon Labs CP210x USB serial backend.

## Main Behavior

`slprobe` matches CP210x VID/PID pairs and installs `slops`.

The backend wraps vendor/interface USB control transfers with `slread`, `slwrite`, and `slput`. `slinit` records driver name `silabs`, reads the chip type, enables the port, reads current parameters, and retains the USB device reference.

`slgetparam` reads baud and line-control register fields, decoding data bits, parity, and stop bits. `slsetparam` writes the line-control register and baud value.

`slmodemctl` programs Silicon Labs flow-control registers for either CTS/RTS hardware flow control or direct DTR/RTS control. `slsendlines` updates DTR and RTS through `Setctrl`.

## Data Path

The backend uses generic endpoint discovery but overrides `wait4data` with a direct blocking read loop that temporarily drops the serial device lock and ignores zero-length reads.

## Integration Points

`slops` supplies initialization, parameter get/set, line control, modem control, custom data wait, and endpoint discovery.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/serial/silabs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/serial/ucons.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/serial/ucons.c

## Role

Provides a minimal USB console-style serial probe shim.

## Main Behavior

The file matches two device families: Ajays Net20DC USB debug cable and Huawei E220. The matched `cid` value is used as `ser->nifcs`, so the probe can expose one or more interfaces.

`uconsprobe` checks VID/PID with `matchid`, sets the interface count, installs `uconsops`, and otherwise leaves behavior to the generic serial framework.

## Integration Points

`uconsops` only provides `.findeps = findendpoints`, relying on generic endpoint handling and default read/write paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/serial/ucons.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/usbd/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/usbd/dat.h

## Role

Defines private data structures and constants for `nusb/usbd` hub management.

## Main Contents

The file declares hub descriptor constants for USB2 and USB3 hubs, hub/port feature selector values, port status bits, port state values, timing constants, attach-loop throttling constants, and embedded-driver match flags.

`Hub` stores hub configuration and runtime state: power mode, compound flag, power delay, max current, TT settings, LED support, packet size, port count, port array, failure state, backing `Dev`, and linked-list pointer.

`Port` tracks each hub port: state, last status, attach timing/counter, removable/power-control flags, attached device, and child hub pointer.

`DHub` and `DSSHub` model USB2 and superspeed hub descriptors, including variable-length removable-port bitmaps.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/usbd/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/usbd/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/usbd/fns.h

## Role

Declares cross-file functions and globals for the `nusb/usbd` implementation.

## API Surface

The header exposes the global hub list and functions for attach/detach events, hub polling work, hub creation, stable-name hashing, stable-name assignment, idle checking, and hub port feature control.

It is the small connection point between `hub.c`, `usbd.c`, and `hname.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/usbd/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/usbd/hname.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/usbd/hname.c

## Role

Generates compact stable USB hardware-name prefixes.

## Main Behavior

`hname` SHA1-hashes the caller-provided identity string, derives a 20-bit value from the first three digest bytes, and overwrites the input buffer with a five-hex-digit name.

`assignhname` in `usbd.c` uses this as the base name and appends collision suffixes when needed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/usbd/hname.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/usbd/hub.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/usbd/hub.c

## Role

Implements USB hub configuration, polling, port state tracking, device enumeration, detach handling, and child hub management for `nusb/usbd`.

## Hub Setup

`newhub` creates either a root hub from `/dev/usb/...` controller state or a normal hub from USB hub descriptors. USB2 setup parses `DHub`, port power/removable maps, TT fields, and optionally enables multi-TT mode. USB3 setup parses `DSSHub` and sets hub depth.

After setup, each port is powered, optional indicators are enabled, the hub is added to the global hub list, and data I/O is opened.

## Enumeration

`work` loops forever, holding `hublock`, polling every hub and port in list order. Enumeration is intentionally serialized so default-address USB enumeration cannot race.

`enumhub` compares current and prior port status, handles suspend resume, detects attach, detach, lost-enable reconnects, and user-requested resets, then calls `portattach`, `portdetach`, or `portfail`.

`portattach` throttles repeated attach loops, resets non-USB3 ports, creates the kernel device with `newdev`, opens endpoint zero, assigns address, reads max packet size, configures descriptors, assigns stable hardware name, sets configuration 1, recursively handles hubs, and posts non-hub devices through `attachdev`.

## Failure Handling

`hubfail` detaches all ports and marks a hub failed. `closehub` removes a hub from the global list, detaches children, closes the device, and frees state. `portfail` detaches and disables or warm-resets the port depending on USB generation.

## Notable Details

The code does not use hub interrupt endpoints; it polls because root hubs must be polled anyway. Attach-loop throttling prevents unstable devices from repeatedly consuming enumeration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/usbd/hub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/usbd/usbd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/usbd/usbd.c

## Role

Implements the `usbd` 9P service, USB attach/detach event stream, hub control file, stable device naming, and daemon startup.

## 9P Interface

The service exposes:

- `usbevent`: read-only attach/detach event stream.
- `usbhubctl`: write-only hub port control.

Readers of `usbevent` are ordered and each event is claimed by one reader at a time using `Dev->aux`. On open, existing non-hub configured devices are enumerated into the reader’s event chain.

`usbhubctl` accepts commands for `portpower` and `portindicator`, finds hubs by hardware name or numeric id, validates port and capability support, then calls `portfeature`.

## Event Model

`pushevent` appends events with device references. `procreqs` advances readers, claims devices, and fulfills pending reads. `detachdev` and `attachdev` publish formatted events of the form `attach/detach id vid did csp hname`.

## Device Naming And Startup

`assignhname` builds a stable identity string from VID, DID, device revision, class/subclass/protocol, and serial string, hashes it through `hname`, and resolves collisions with numeric suffixes.

`main` initializes formatting, creates root hubs from `/dev/usb` or explicit arguments, creates `/env/usbbusy`, and posts the service. The service start hook forks `work` to run hub polling.

## Notable Details

`attachdev` creates default configuration endpoint files before publishing the attach event. `checkidle` removes `/env/usbbusy` once event readers have consumed initial enumeration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/nusb/usbd/usbd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/os.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/os.c

## Role

Runs a command through a remote command service mounted at `/mnt/term/cmd`.

## Main Behavior

The program opens the remote `clone` control file, reads the per-command directory name, opens `wait`, and optionally opens foreground `data` and `stderr` streams. It can set remote directory and nice level, enables `killonclose` for foreground jobs, and writes an `exec` command with quoted arguments.

Foreground mode forks copy processes for stdin, stdout, and stderr, plus a wait-reader process. Background mode skips the data stream copying.

## Options

Supports selecting mount point, explicit remote directory, background mode, and nice value. If no directory is given, it tries to translate the current directory relative to `/mnt/term` or `/mnt/term/root`.

## Process Handling

Interrupt, hangup, and kill notes are caught and translated to a remote `kill` control write. Local copy processes are tracked so the stdin copier can be killed at exit.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/os.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/p.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/p.c

## Role

Implements a simple pager that prints fixed-size chunks and waits for console input between chunks.

## Main Behavior

The default chunk length is 22 lines, with an optional `-N` style argument to change it. Files are printed in order; stdin is used when no files are given.

`printfile` uses Bio buffered I/O, writes lines to stdout without adding an extra newline after the last line in a page, flushes output at page boundaries, then reads a command from `/dev/cons`.

## Commands

`q` or EOF exits. A command starting with `!` runs the rest through `/bin/rc -c`, then returns to the prompt. Any other line advances to the next chunk.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/p.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/page.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/page.c

## Role

Implements Plan 9’s graphical document/image viewer. It can open images, directories, archives, compressed files, PostScript/PDF/troff/text/html/dvi/doc inputs through filters, and EPUB-like directory trees.

## Page Model

`Page` forms a recursive tree with parent, child, sibling, tail, and LRU links. A page can have an opener function, backing fd/path/filter data, loaded `Image`, extension command, and delimiter used in page addresses.

The viewer tracks current page, read-ahead direction, image memory limit, view generation, zoom/resize/rotate settings, and an affine warp matrix for pan/zoom display.

## Input And Decoding

`popenfile` detects directories, EPUB container metadata, and file types using Plan 9 `file -m`. It dispatches formats to:

- `popenimg` for image converters.
- `popengs`/`popenpdf` for Ghostscript and PDF page extraction.
- `popentape` for archive mounting through zip/tar filesystems.
- `popenfilter` for decompression filters.
- `popenepub` for EPUB spine expansion.

Non-seekable or changing streams are spooled to temporary files.

## Rendering And Caching

`openpage` applies rotate/resize filters before `readimage`. `loadpages` reads ahead from the current page while respecting an LRU image memory limit. `unloadpages` frees images from the LRU tail.

Drawing uses affine warp operations to render the current image, draws a frame, and fills background differences. Pan/zoom mutate `warpmat`; fit-width/fit-height reload through image resize filters.

## UI

Mouse buttons support drag panning, command menu, page menu, and scrolling. Keyboard commands support original size, zoom, fit, rotate, next/previous, snarf page address, write bitmap, open external decoder, clone view, and quit.

The program also listens on the `image` plumb port to show files or inline data and supports page-address jumps.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/page.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/paint.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/paint.c

## Role

Implements a small graphical bitmap editor.

## Drawing Model

The editor maintains a possibly unbounded canvas image, current screen/canvas origin, zoom factor, ink/background images, a 16-color palette initialized to a C64-style palette, brush size, and circular undo buffer.

Strokes draw lines with disc endpoints; the largest brush slot is a flood-fill tool. Canvas expansion preserves existing pixels and fills new areas with the background.

## Display

`zoomdraw` renders source image pixels at integer zoom, handling alpha/background and avoiding overwriting toolbar/palette regions. Coordinate helpers convert between screen and canvas coordinates. `drawpal` draws the palette and brush selector at the bottom of the window.

## Editing

Mouse left draws with ink, middle draws with background, right pans the canvas. Palette clicks select ink, set background, or edit a palette color by hex value. Keyboard controls include zoom, clear, undo, fill brush, numeric brush selection, and command prompt.

The flood-fill implementation builds a GREY1 mask by recursively scanning same-colored runs and then draws the fill color through that mask.

## File And Filter Commands

The command prompt supports read/write, shell input/output filters, and pipe-through-image-filter operations. Images are read/written with Plan 9 `readimage`/`writeimage`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/paint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/paqfs/mkpaqfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/paqfs/mkpaqfs.c

## Role

Builds a `paqfs` archive from a file or directory tree.

## Archive Construction

`paqfs` writes a header, recursively packs the root as either file or directory, writes the root directory entry block, and appends a trailer.

Files are split into fixed-size data blocks. A pointer block stores 32-bit block offsets. The original file length is preserved in the directory entry, while the final data block is padded to full block size.

Directories are packed recursively. Directory entries are serialized into directory blocks, with a pointer block listing those directory blocks.

## Encoding And Integrity

Each block has a `PaqBlock` header with type, encoded size, encoding, and Adler-32 of unencoded block data. Unless `-u` is used, `writeBlock` attempts deflate compression and stores compressed data only when smaller.

`outWrite` updates a running SHA1 digest over archive bytes. `writeTrailer` stores the root offset and final digest.

## Format Serialization

The file provides big-endian serializers for headers, blocks, trailers, directory entries, integers, shorts, and length-prefixed strings. It supports alternate “big” header/block forms when block size or encoded size exceeds 16-bit limits.

## Options

Supports uncompressed mode, compression level, block size with optional `k` suffix, output path, and label.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/paqfs/mkpaqfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/paqfs/paqfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/paqfs/paqfs.c

## Role

Mounts a `paqfs` archive as a read-only 9P filesystem.

## Startup

`main` parses mount/service/auth/cache/message-size/verify options, calls `init`, then serves 9P over stdio or a pipe mounted at `/n/paq` or posted in `/srv`.

`init` reads and validates the archive header, optionally verifies all blocks and trailer SHA1, initializes an LRU-ish block cache, loads the root `PaqDir`, and handles the special case where the archive root is a regular file by fabricating a directory root containing that file.

## 9P Operations

Implements version, attach, walk, open, read, clunk, stat, and read-only errors for create/write/remove/wstat. Permissions are checked against stored uid/gid/mode, with `-a` allowing no-auth owner/group checks.

Directory reads traverse pointer blocks and directory blocks, packing `Dir` records with `convD2M`. File reads map offsets through the file’s pointer block and load data blocks.

## Archive Access

`blockLoad` caches decoded blocks by byte address, using an age counter and reference counts. `blockRead` seeks to a block, validates magic/type/size, inflates if needed, and checks Adler-32.

The file includes deserializers for archive headers, blocks, trailers, directory entries, strings, and integers.

## Notable Details

The filesystem is strictly read-only. `-v` verifies the entire archive digest before serving; otherwise it seeks directly to the trailer based on file length.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/paqfs/paqfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/paqfs/paqfs.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/paqfs/paqfs.h

## Role

Defines the `paqfs` on-disk format shared by the archive builder and filesystem server.

## Main Contents

Constants define header, block, trailer magic values, serialized sizes, version, block-size bounds, minimum directory entry size, block types, and encodings.

Structures include:

- `PaqHeader`: magic, version, block size, creation time, label.
- `PaqBlock`: magic, stored size, type, encoding, Adler-32 of unencoded data.
- `PaqTrailer`: magic, root block offset, SHA1 digest.
- `PaqDir`: qid, mode, mtime, length, pointer block offset, name, uid, gid.

## Format Notes

Blocks are typed as directory, data, or pointer blocks. Encodings are none or deflate. Multi-byte fields are serialized manually in big-endian order by the implementation files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/paqfs/paqfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/patch.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/patch.c

## Role

Applies unified diff patches.

## Parsing

`parse` scans for `---`/`+++` file headers and `@@` hunk headers. `fileheader` supports path component stripping and `/dev/null`. `hunkheader` parses old/new line numbers and counts, normalizing to zero-based offsets except for empty files.

Each hunk stores original text, old text, new text, paths, line counts, and source patch line number. Reverse mode swaps old/new paths, counts, offsets, and buffers after parsing. Hunks are sorted by old path and line.

## Applying

`apply` groups hunks by target file, slurps each file into memory with line-offset indexing, searches for hunk old text near the expected line with up to 250 lines of fuzz, appends unchanged and replacement text into a new output buffer, and schedules file replacement.

`blat` writes changes to temporary files, creates missing parent directories, handles `/dev/null` creation/deletion cases, and records pending changes. `finish` commits temp files by rename or removes them on failure/dry-run.

## Rejections

If a reject file is requested, failed hunks are written there in unified form and processing continues. Without a reject file, an unfound hunk is fatal.

## Options

Supports dry-run, reverse, path stripping, reject file, and changing working directory before applying.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/patch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pbd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pbd.c

## Role

Prints the basename of the current working directory.

## Main Behavior

`main` calls `getwd`, finds the last slash, selects the final path component, falls back to `???` on failure, writes the result to stdout, and exits.

It does not append a newline.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pbd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pc.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pc.y

## Role

Defines the grammar and implementation for an arbitrary-precision integer calculator.

## Number Model

`Num` embeds `mpint`, stores an output base hint, and uses reference counting. Copy-on-write helpers allow expression operations to mutate when uniquely owned and duplicate when shared.

Base selection can be weak or strong. Literals can use current input base or explicit binary/octal/decimal/hex prefixes. Output honors explicit output base or a number’s strong base.

## Grammar

The yacc grammar supports statements separated by newlines or semicolons, variable assignment, last-result access through `@`, base/control statements, numeric literals, symbols, function calls, unary operators, arithmetic, bitwise operators, comparisons, logical operators, exponentiation, shifts, conditional `?:`, and sign-extension via `$`.

Division/modulo semantics are controlled by `divmode`, with adjusted behavior for negative remainders in the default mode.

## Built-In Functions

Registered functions include base coercion (`hex`, `dec`, `oct`, `bin`, `pb`), numeric transforms (`abs`, `round`, `floor`, `ceil`, `trunc`, `xtend`), bit helpers (`clog`, `ubits`, `sbits`, `nsa`, `rev`, `cat`), number theory (`gcd`, `minv`), and random generation (`rand`).

## Lexer And UI

The lexer recognizes multi-character operators, numbers with underscores, identifiers including non-ASCII bytes, and prompts when stdin is `/dev/cons`.

`numprint` can emit digit group separators and optional bit-position headers for binary/octal/hex output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pc.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pcc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pcc.c

## Role

Acts as an APE C compiler driver, wrapping Plan 9 architecture-specific compiler, linker, and preprocessor commands.

## Main Behavior

`findoty` reads `$objtype` and selects tool names/extensions from `objtype[]`. The driver builds command lists for `cpp`, the architecture compiler, and linker.

C sources are preprocessed through `/bin/cpp` and piped to the compiler. Object/library inputs are accumulated for the linker. Unless compile-only mode is selected, the linker is invoked with the selected output name and APE support library.

## Options

Handles common compile/link/preprocess flags including `-c`, `-o`, `-l`, `-D`, `-I`, `-U`, verbose mode, preprocessor-only modes, profiling, assembler-output variants, and several compiler pass-through flags. Wrong-architecture object arguments are ignored with a warning.

## Process Handling

`doexec` runs a single command and checks wait status. `dopipe` connects preprocessor output to compiler input and waits for both children. Verbose mode prints the composed command lines.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pcc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/arcgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pic/arcgen.c

## Role

Generates `pic` arc objects and computes their bounding boxes.

## Main Behavior

`arcgen` interprets attributes for text, arrow heads, invisibility, arrow dimensions, radius/diameter, clockwise mode, from/to/at positions, direction, and fill. It computes default arc center/end based on current direction and radius, or derives a center from explicit endpoints and radius.

Clockwise arcs swap start/end roles and adjust arrow-head placement. The generated object records start, end, radius, arrow dimensions, fill, and flags.

## Bounding Box

`arc_extreme` computes extrema for a circular arc by considering start/end points and quadrant boundary points that lie on the swept arc. `quadrant` classifies vectors around the center.

## State Updates

The global current point is advanced to the arc endpoint according to direction and clockwise handling. `extreme` is called with computed bounds.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/arcgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/blockgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pic/blockgen.c

## Role

Implements `pic` block handling for bracketed object groups and brace-local movement groups.

## Block Stack

`leftthing` saves current position, direction, bounds, and symbol context when entering `[...]`; it resets local coordinates and creates a `BLOCK` object. For `{...}`, it saves position/direction on a separate stack.

`rightthing` restores saved state. For `]`, it creates a `BLOCKEND`, links begin/end object indices, stores local bounding box information, and restores outer bounds. For `}`, it emits a `MOVE`.

## Block Generation

`blockgen` applies attributes such as height, width, `with`, explicit position, invisibility, and text. It computes final block placement, updates global extrema, stores size and original local center, advances current position, copies block metadata to the end marker, and calls `blockadj`.

`blockadj` shifts all enclosed objects by the block placement delta, including absolute coordinate fields for lines, splines, and arcs.

## Limits

Nested `[...]` and `{...}` depth is bounded by fixed stack sizes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/blockgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/boxgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pic/boxgen.c

## Role

Generates `pic` box objects.

## Main Behavior

`boxgen` reads default box height/width, applies attributes for size, `same`, `with` corner/edge anchoring, `at`, invisibility, no edge, dotted/dashed outline, fill, and text.

If no explicit position is provided, the box is placed relative to the current point and current direction. `with` adjusts the anchor so a named side/corner lands at the current point.

The object stores width, height, drawing attributes, dash/dot value, and fill value. Bounds are added via `extreme`, and current position is advanced to the far edge in the active direction.

## State

Previous box height/width are remembered for the `same` attribute.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/boxgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/circgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pic/circgen.c

## Role

Generates `pic` circle and ellipse objects.

## Main Behavior

`circgen` handles both `CIRCLE` and `ELLIPSE`. It reads default radii from global variables, applies attributes for text, radius, diameter, width, height, `same`, `with`, `at`, invisibility, no edge, dotted/dashed outline, and fill.

For circles, the vertical radius is forced to equal the horizontal radius. For ellipses, width and height map to separate radii.

If no explicit `at` is provided, placement advances from the current point in the current direction by the relevant radius. `with` anchors sides/corners using full radius offsets or approximate diagonal offsets.

## Output

The generated object stores radii, attributes, dash/dot value, and fill value. It updates global extrema and advances current position by radius in the active direction.

## State

Previous circle and ellipse radii are remembered separately for the `same` attribute.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/circgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/for.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pic/for.c

## Role

Implements `pic` loop and conditional source expansion.

## For Loops

`forloop` pushes a loop frame with variable name, limit, operator, step, and saved source string. It initializes the variable and calls `nextfor`.

`nextfor` checks loop completion using a small slop factor and either frees/pops the frame or pushes the saved body plus an `Endfor` marker back onto the input stack.

`endfor` updates the loop variable by add, subtract, multiply, or divide, then continues through `nextfor`.

## Conditionals

`ifstat` pushes either the then-part or else-part source text back onto the input stream and frees the unused branch. It returns the branch string that will be freed later by the input stack.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/for.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/input.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pic/input.c

## Role

Implements `pic` input source stacking, macro definitions/expansion, argument parsing, pushback, file inclusion, `copy thru`, shell escapes, and syntax-error context reporting.

## Source Stack

`pushsrc` and `popsrc` manage a stack of input sources: files, macros, single pushed-back chars, thru markers, literal strings, and strings to free. `input` reads through `nextchar`, records context for errors, and triggers `do_thru` when a `copy thru` line expansion is pending.

`unput` pushes a character back through both the pushback buffer and source stack.

## Macros

`definition` reads a delimited macro body and installs it as a `DEFNAME`. `dodef` parses macro arguments in parentheses, stores them in an argument frame, and pushes the macro body. Macro expansion substitutes `$N` arguments.

`delimstr` reads balanced delimited bodies, supporting paired delimiters such as `{}`.

## Copy/Thru

`copyfile`, `copydef`, `copythru`, `copyuntil`, and `copy` coordinate copying from files and applying a macro to each input line. `do_thru` tokenizes each line into macro arguments, terminates on `.PE` or an optional until string, and pushes the thru macro.

## Errors And Shell

`yyerror` reports file/line and calls `eprint`, which prints nearby input and pushback context, then pushes `.PE` as a recovery guard.

`shell_init`, `shell_text`, and `shell_exec` collect and run `rc -c` commands.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/input.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/linegen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pic/linegen.c

## Role

Generates `pic` line, arrow, and spline objects.

## Main Behavior

`linegen` processes attributes for text, arrow heads, invisibility, no edge, dotted/dashed style, `same`, direction/length, `to`, `by`, `then`, `from`/`at`, `with`, `chop`, and fill.

It accumulates one or more segment deltas in `dx[]`/`dy[]`. Direction attributes add default or explicit lengths. `to` and `by` start new segments when needed. If no movement is specified, it emits a default movement in the current direction.

## Chopping And Arrows

`chop` shortens the first and last segment by configured distances, defaulting to circle radius when only bare `chop` is used. Arrow objects default to a head at the endpoint, and explicit head attributes are honored.

## Output

The object stores final endpoint, arrow dimensions, number of segment deltas, per-segment deltas, attributes, dash/dot value, and fill value. It updates global extrema for straight lines/arrows and approximate spline extrema.

## State

Last line delta is remembered for the `same` attribute, and current position/direction are updated as attributes are processed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/linegen.c -->