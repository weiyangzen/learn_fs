# Group Research: group_69_9front_sources_os_plan9_9front_sys_src_cmd_awk_run_c_sources_os_plan9_215fb3a2911f

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/run.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/awk/run.c

This is the runtime executor for the 9front/Lucent awk interpreter. It walks the parsed `Node` tree through `execute`, dispatches parse operators through `proctab`, and maintains awk control-flow sentinels for `break`, `continue`, `next`, `nextfile`, `return`, and `exit`.

Major responsibilities:
- Program execution: `run`, `execute`, `program`.
- User function calls: stack frames in `struct Frame`, argument copying/reference handling, return values.
- Expression evaluation: arithmetic, assignment, concatenation, relation/boolean operators, conditional expressions.
- Arrays: multi-subscript key construction using `SUBSEP`, delete, membership tests, `for (x in a)`.
- Builtins: `length`, math functions, `system`, `rand/srand`, case conversion, `fflush`, UTF rune conversion.
- I/O: `getline`, `print`, `printf`, redirections, pipes via `popen`, close/flush tracking through a fixed `files[FOPEN_MAX]` table.
- String operations: UTF-aware `substr`/`index`, `split`, `sub`, `gsub`, replacement escape handling.

Filesystem/OS relevance:
- Uses Plan 9 `Biobuf`, `/bin/rc -c` for `system`, file descriptors, pipes, and path-like redirection names.
- Redirection state is process-global and bounded by `FOPEN_MAX`.

Notable implementation details:
- Uses `setjmp/longjmp` for awk `exit`.
- Field/record coherence is lazy through `donefld`, `donerec`, `fldbld`, `recbld`.
- `adjbuf` centralizes dynamic output-buffer growth.
- UTF handling appears in match positions, case conversion, `substr`, `split("", ...)`, and `%c`.

Risks and caveats:
- Function-call logic is explicitly described as fragile and has comments about possible double frees.
- Several fixed-size or bounded resources remain: open file table, temp cell block allocation, format-number sizing.
- `system` waits for the exact child and treats any non-empty wait message as failure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/run.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/tran.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/awk/tran.c

This file implements awk symbol-table and value conversion machinery.

Major responsibilities:
- Initializes built-in variables: `FS`, `RS`, `OFS`, `ORS`, `OFMT`, `CONVFMT`, `FILENAME`, `NF`, `NR`, `FNR`, `SUBSEP`, `RSTART`, `RLENGTH`, `SYMTAB`.
- Builds `ARGV`/`ARGC` from command-line inputs.
- Lazily initializes `ENVIRON` from Plan 9 `/env`, skipping function variables named `fn#...`.
- Implements hash-table arrays: `makesymtab`, `setsymtab`, `lookup`, `freeelem`, `freesymtab`, `rehash`.
- Handles awk cell string/number duality through `setfval`, `setsval`, `getfval`, `getsval`.

Notable implementation details:
- `Cell` values track flags such as `NUM`, `STR`, `ARR`, `CON`, `DONTFREE`, `FLD`, and `REC`.
- Assigning to fields and `$0` invalidates the reciprocal cached representation.
- `SYMTAB` is exposed by storing the main `symtab` pointer in a cell marked `ARR`.
- `qstring` decodes awk string literals, including octal escapes.

Risks and caveats:
- `getsval` uses a fixed `char s[100]` buffer with a source comment noting it is unchecked.
- Environment import is Plan 9-specific and depends on `/env`.
- String ownership depends on `DONTFREE`; incorrect flag handling can leak or free wrong storage.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/awk/tran.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bar.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bar.c

This is a small graphical status bar for rio/Plan 9.

Major responsibilities:
- Draws time, battery percentage, and auxiliary stdin-provided text.
- Positions/resizes its window via `/dev/wctl` according to `-p` placement and `-b` bottom mode.
- Reads theme color from `/dev/theme`.
- Reads battery data from `/mnt/pm/battery` or `/dev/battery`.
- Emits clicked item information to stdout as `buttons<TAB>item`.

Event model:
- Uses Plan 9 threads and channels for mouse, resize, keyboard, auxiliary input, and timer events.
- `timerproc` ticks roughly once per second; battery refresh is throttled to about 30 seconds.
- `auxproc` reads lines from stdin and replaces displayed auxiliary text.

Notable implementation details:
- `nanosec` prefers cycle counter timing from `_tos->cyclefreq`, falling back to `nsec`.
- Separator formatting is custom via `%|`.
- Highlighting clips the draw region over the clicked item.

Risks and caveats:
- Fixed arrays cap displayed split items at 64 and string buffers at 1024 bytes.
- Keyboard delete exits the whole thread group.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/basename.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/basename.c

This is a compact implementation of `basename` with an added `-d` dirname-like mode.

Behavior:
- `basename string [suffix]` prints the final path component.
- If `suffix` is supplied and matches the end of the basename, it is stripped in place.
- `basename -d string` prints the directory portion before the last slash, or `.` if there is no slash.

Notable implementation details:
- Uses `utfrrune` to find the final `/`.
- Mutates `argv[1]` or the local basename buffer directly by inserting NULs.

Risks and caveats:
- Assumes argument strings are mutable, as is common in this Plan 9 C environment.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/basename.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bc.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bc.y

This is the yacc grammar and translator for Plan 9 `bc`. It converts bc syntax into dc commands and either prints the generated dc program with `-c` or pipes it to `/bin/dc`.

Major responsibilities:
- Grammar for statements, expressions, assignments, loops, conditionals, function definitions, `auto`, `return`, `break`, `print`, base/scale settings, arrays, and increments/decrements.
- Emits dc command bundles using `bundle`, `routput`, `output`, and `conout`.
- Maintains function/local-variable save/restore prologues and epilogues through `pp` and `tp`.
- Implements lexer `yylex` with keyword recognition and comment/string scanning.
- Handles input from files first, then stdin.

Notable implementation details:
- Supports `-c`, `-d`, `-l`, and `-s`.
- `-l` prepends `/sys/lib/bclib`.
- Keyword detection checks two-letter prefixes and skips the rest of the word.
- Uses fixed workspaces: `cary[1000]`, `string[1000]`, `bspace[5000]`, branch label range starting at `crs=128`.

Risks and caveats:
- The translator is tightly bounded by fixed buffers and label limits.
- Comment scanning has an unbounded loop until `*/`.
- Error reporting emits dc code that prints diagnostics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bc.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bind.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bind.c

This is a thin command wrapper around Plan 9 `bind`.

Behavior:
- Supports `-a`, `-b`, `-c`, and `-q`.
- Rejects simultaneous `-a` and `-b`.
- Calls `bind(new, old, flags)`.
- On failure, `-q` exits successfully; otherwise it probes `new` and `old` with `access` to print a clearer diagnostic.

Filesystem/OS relevance:
- Directly manipulates the Plan 9 namespace using `bind`.
- Uses Plan 9 mount flags `MAFTER`, `MBEFORE`, and `MCREATE`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bind.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bitsy/bitsyload.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bitsy/bitsyload.c

This utility writes Bitsy images into flash partitions.

Behavior:
- Method table maps verbs to partitions and default source files:
  - `k` -> `/dev/flash/kernel`
  - `r` -> `/dev/flash/ramdisk`
  - `u` -> `/dev/flash/user`
- Opens the target partition and `<partition>ctl`.
- Reads flash geometry from the control file.
- Reads the whole input file, pads to sector size, erases the partition, then writes sector-sized chunks.

Notable implementation details:
- Validates sector count and sector size before writing.
- Checks that padded input fits in the flash partition.
- `leputl` exists but is unused in this file.

Risks and caveats:
- Whole image is loaded into memory.
- Destructive operation: erases target flash partition before writing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bitsy/bitsyload.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bitsy/keyboard.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bitsy/keyboard.c

This is a graphical on-screen keyboard and optional scribble input tool for Bitsy/touch environments.

Major responsibilities:
- Creates keyboard and scribble controls.
- Writes selected runes to `/dev/kbdin` or `#r/kbdin`, falling back to stdout.
- Optional window list mode (`-w`) shows rio windows and can raise/select them.
- Optional layout flags choose scribble side or keyboard-only mode.
- Mouse button bit `0x20` toggles hide/unhide through `/dev/wctl`.

Notable implementation details:
- Uses Plan 9 control library widgets: keyboard, scribble, text buttons, boxbox.
- Polls `/dev/wsys` to build window-button list.
- Handles resize by recalculating rectangles for keyboard, scribble, and window list.
- Uses channels for keyboard events, control events, and timer refresh.

Risks and caveats:
- Contains an empty infinite `watchproc` that is not used.
- Several resources and layout sizes are hardcoded for small-screen devices.
- `namectlimage(colors[Shade], "keymask")` appears where `colors[Mask]` would be expected.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bitsy/keyboard.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bitsy/params.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bitsy/params.c

This utility copies parameter data between a flash partition and `/tmp/tmpparams`.

Behavior:
- Default partition is `/dev/flash/user`, overrideable by positional argument.
- With `-f`, reads the flash partition and writes `/tmp/tmpparams`.
- Without `-f`, reads `/tmp/tmpparams`, erases the flash partition, and writes the data back.

Notable implementation details:
- `readfile` truncates at the first `0xff`, treating erased flash as terminator.
- `erase` writes `erase` to `<partition>ctl` if available.
- `writefile` creates missing destination files.

Risks and caveats:
- Silent returns on failed erase/write open paths can hide failure.
- Flash write path is destructive.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bitsy/params.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bitsy/pencal.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bitsy/pencal.c

This is a pen/touchscreen calibration utility.

Major responsibilities:
- Reads raw mouse/pen events from `/dev/mouse` or `#m/mouse`.
- Reads/writes calibration data through `#m/mousectl`.
- Displays calibration crosses at four corners and a center verification point.
- Computes linear scale/translation values for x and y.

Notable implementation details:
- Attempts to resize its window to nearly the full display through `/dev/wctl`.
- Reads existing calibration from a 48-byte `mousectl` message.
- Averages samples while button bits are down, ending a point when released.
- Retries calibration up to three times if center verification differs by more than four pixels.

Risks and caveats:
- Assumes fixed-format 48-byte mouse and mousectl messages.
- `scr2pen` uses `(p.y + cal.transy)` where the inverse would usually subtract; this may reflect device convention or a historical quirk.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bitsy/pencal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bitsy/prompter.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bitsy/prompter.c

This is a touch-friendly prompt/file editor with an on-screen keyboard and optional scribble area.

Behavior:
- Reads an input file into up to 24 editable lines.
- Builds text entry controls for as many lines as fit above the keyboard.
- Routes physical keyboard events to text entries and on-screen keyboard/scribble events into the keyboard channel.
- Exits on mouse button bit `0x20` or Escape.
- Writes non-trailing-empty lines back to the same file.

Notable implementation details:
- Uses two control sets: one for keyboard/scribble, one for text entries.
- `mousemux` routes mouse events by y-coordinate split at `kbdy`.
- `resizemux` forwards resize events to both control sets.
- `-n` disables scribble.

Risks and caveats:
- Reads the whole file based on `Dir.length`.
- Only visible/managed lines are written back, bounded by the calculated `Nline`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bitsy/prompter.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzfs/bzfs.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzfs/bzfs.h

This header declares shared entry points for the bzip-backed filesystem utilities.

Contents:
- Decompression pipeline functions: `unbzip`, `_unbzip`, `unbflz`, `xexpand`.
- Allocation helpers: `emalloc`, `erealloc`, `estrdup`.
- RAM filesystem entry point: `ramfsmain`.
- Shared verbosity flag `chatty`.
- Shared fatal reporter `error`.

Notable detail:
- `xexpand` is declared here but not present in the listed files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzfs/bzfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzfs/mkext.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzfs/mkext.c

Despite the filename, this is the main `bzfs` loader for a bzip2/BLZ-compressed mkfs archive filesystem.

Behavior:
- Archive format is described as `bzfilesystem\n` prefix, bzip2 data, BLZ data, and trailing zero padding.
- Starts an in-memory ramfs mounted at a target mountpoint, default `/root`.
- Scans the input file on 512-byte boundaries for `bzfilesystem\n`.
- Uses `blockread` to bridge block-aligned devices to arbitrary byte reads through a pipe.
- Chains decompression as `blockread -> unbzip -> unbflz`.
- Reads mkfs-style file headers with six fields: name, mode, uid, gid, mtime, bytes.
- Creates directories/files under `mtpt`, writes contents, and sets metadata with `dirfwstat`.

Filesystem relevance:
- Provides a read-in, memory-resident boot filesystem intended for floppy/contiguous DOS-file use.
- Changes after load stay in RAM and are not written back.

Risks and caveats:
- Always takes the search path because of `if(1 || strstr(file, "disk"))`.
- `blockread` detects an all-zero 512-byte block using `memcmp(zero, blk, n) == n`, which is unusual since `memcmp` returns zero on equality.
- Fatal `error` exits with status `0`, matching historical Plan 9 conventions poorly for failures.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzfs/mkext.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzfs/oramfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzfs/oramfs.c

This is an in-memory 9P ramfs implementation used by `bzfs`.

Major responsibilities:
- Serves 9P requests over pipes/stdio.
- Maintains a fixed `Ram ram[Nram]` array of file metadata and content.
- Maintains dynamic fid list `Fid`.
- Implements core 9P handlers: version, attach, walk, open, create, read, write, clunk, remove, stat, wstat.
- Mounts itself at a requested mountpoint, publishes `/srv/ramfs`, or uses stdio mode for kernel/loader use.

Filesystem model:
- Root starts as `.` with `DMDIR | 0775`.
- File data is stored in heap buffers, capped by `Maxsize` sanity check.
- Directory reads synthesize stat records for children.
- Metadata uses Plan 9 `Dir`, `Qid`, `convD2M`, `convM2D`.

Notable implementation details:
- User/group strings are interned by `atom`; atoms are intentionally never freed.
- Permission checks exist but many are behind `#ifdef CHECKS`; ownership checks are behind `#ifdef OWNERS`.
- `DMAPPEND`, `DMEXCL`, `ORCLOSE`, truncation, qid versions, and wstat length changes are supported.
- Message size is negotiated by `Tversion`.

Risks and caveats:
- Fixed maximum of 512 `Ram` entries.
- Removal does not recursively check directory children.
- Many permission checks are compiled out by default.
- `rwalk` compares `rhdr.newfid`/`rhdr.fid`, but request fields conventionally live in `thdr`; this deserves scrutiny in maintenance.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzfs/oramfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzfs/unbflz.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzfs/unbflz.c

This implements BLZ expansion as a pipe-producing process.

Behavior:
- Validates `BLZ\n` header.
- Reads uncompressed length as big-endian.
- Reads block descriptors until their summed lengths equal the output length.
- Descriptor high bit means literal data follows; otherwise descriptor is a back-reference with offset.
- Reconstructs the full output in memory, then writes it to the pipe.

Notable implementation details:
- `Bgetint` reads big-endian 32-bit integers from a `Biobuf`.
- `copy` is a forward byte copy intended to make overlapping back-reference expansion work.
- Forks with `RFMEM`, so child shares memory where Plan 9 semantics allow.

Risks and caveats:
- Entire expanded output is allocated at once.
- Corrupt descriptors can reference arbitrary prior offsets; there is no explicit offset bounds check.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzfs/unbflz.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzfs/unbzip.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzfs/unbzip.c

This is a bzfs-local, modified bzip2 decompressor. It embeds enough libbzip2 code to inflate a stream and expose it as a Plan 9 pipe.

Major responsibilities:
- `unbzip` forks a decompressor process and returns the read end of a pipe.
- `_unbzip` inflates fd input to fd output.
- Local `bunzip` streams data through `BZ2_bzDecompress`.
- Provides Plan 9 platform glue and allocation functions.
- Embeds bzip2 decompression machinery from `decompress.c`, including bit reading, Huffman table use, selector MTF decoding, block CRC handling, and BWT inverse setup.

Notable implementation details:
- Uses `sbrk` allocator with no-op free for decompression state.
- Small decompression path is disabled by `if (0 && s->smallDecompress)`, so fast `tt` table is always used.
- State machine saves local decode variables so decompression can resume when more input is needed.

Risks and caveats:
- This file is explicitly not identical to upstream bzip2.
- Error handling is minimal and often aborts/exits.
- Pipe child shares memory (`RFMEM`) and closes inherited descriptors to form a streaming stage.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzfs/unbzip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/bunzip2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/bunzip2.c

This is the Plan 9 `bunzip2` command wrapper around libbzip2.

Behavior:
- Supports `-c`, `-v`, and `-D`.
- With no files, decompresses stdin to stdout.
- With files, verifies `BZh` magic, derives output names, and writes decompressed output.
- `.bz2` suffix is stripped; `.tbz`/`.tbz2` become `.tar`.
- Avoids overwriting if output name would equal input name.

Streaming model:
- Uses `Biobuf` input/output and `bz_stream`.
- Refills an `IOUNIT` input buffer, preserves unconsumed bytes, and flushes an `IOUNIT` output buffer.
- Calls `BZ2_bzDecompressEnd` after `BZ_STREAM_END`.

Risks and caveats:
- Output name buffer is only 64 bytes.
- Failure removes the partially created output file via `delfile`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/bunzip2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/bzip2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/bzip2.c

This is the Plan 9 `bzip2` command wrapper around libbzip2 compression.

Behavior:
- Supports `-v`, `-c`, `-n`, `-D`, and compression levels `-1` through `-9`.
- With no files, compresses stdin to stdout.
- With files, rejects directories and writes `.bz2` output; `.tar` inputs become `.tbz`.
- `-n` suppresses use of input mtime, though the current compressed stream wrapper does not actually store file metadata.

Streaming model:
- Uses `Biobuf` and `bz_stream`.
- Calls `BZ2_bzCompress` with `BZ_RUN` until input EOF, then `BZ_FINISH`.
- Writes output in `IOUNIT` chunks and finalizes with `BZ2_bzCompressEnd`.

Risks and caveats:
- Mutates the input path string when replacing `.tar` with NUL before building `.tbz`.
- Output file is removed on write/compress failure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/bzip2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/bzip2recover.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/bzip2recover.c

This is upstream `bzip2recover`, a damaged `.bz2` block salvage tool.

Major responsibilities:
- Scans the input bitstream for bzip2 block header and end-marker magic values.
- Records candidate block bit ranges.
- Re-reads the input and writes each recoverable block as a standalone `.bz2` file named `recNNNN<original>`.
- Writes synthetic stream headers and end markers around recovered block data.

Notable implementation details:
- Uses stdio rather than Plan 9 `Biobuf`.
- Implements its own bit-level read/write abstraction `BitStream`.
- Fixed arrays hold up to 20,000 block ranges.
- Always writes recovered streams with block size marker `9`.

Risks and caveats:
- Source comments call it a complete hack.
- Fixed filename buffers are 2000 bytes.
- It can produce incomplete recovered blocks when EOF interrupts a candidate range.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/bzip2recover.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/blocksort.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/blocksort.c

This is libbzip2’s Burrows-Wheeler block sorting implementation.

Major responsibilities:
- Provides `BZ2_blockSort(EState *s)`.
- Uses a fast main sorting path for normal blocks.
- Falls back to a slower but robust sorting path for repetitive data or small blocks.
- Determines `origPtr`, the BWT primary index.

Algorithms:
- `fallbackSort` uses initial byte radix sorting and iterative bucket refinement similar to suffix-array construction.
- `mainSort` uses two-byte bucket sorting, running-order scheduling, 3-way string quicksort, quadrant hints, and budget accounting.
- `mainGtU`, `mainSimpleSort`, and `mainQSort3` perform suffix comparisons and sorting within buckets.
- If work budget is exhausted, `BZ2_blockSort` reruns fallback sorting.

Notable implementation details:
- The file is performance-oriented and macro-heavy.
- `block` overshoot and `quadrant` arrays are tightly laid out inside compression work buffers.
- Sorting output is in `s->ptr`/`s->arr1`.

Risks and caveats:
- Relies on internal buffer alignment and `BZ_N_OVERSHOOT`.
- Uses explicit stack arrays for quicksort recursion simulation.
- Derived from upstream bzip2 1.0-era code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/blocksort.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/buffcompress.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/buffcompress.c

This implements `BZ2_bzBuffToBuffCompress`, a convenience API for compressing one memory buffer into another.

Behavior:
- Validates parameters: destination pointers, source pointer, block size 1-9, verbosity 0-4, work factor 0-250.
- Defaults work factor 0 to 30.
- Initializes a `bz_stream`, points it at the input/output buffers, and runs one `BZ_FINISH` compression.
- On success, updates `*destLen` to bytes written.
- Returns `BZ_OUTBUFF_FULL` if the destination buffer is insufficient.

Notable implementation details:
- Uses default allocators by leaving `bzalloc`/`bzfree` NULL.
- Always calls `BZ2_bzCompressEnd` before returning after initialization succeeds.

Relationship:
- This file is functionally identical to `bzbuffcompress.c` in this group.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/buffcompress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/buffdecompress.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/buffdecompress.c

This implements `BZ2_bzBuffToBuffDecompress`, a convenience API for decompressing one memory buffer into another.

Behavior:
- Validates destination/source pointers, `small` flag, and verbosity.
- Initializes a decompression `bz_stream`.
- Runs `BZ2_bzDecompress` once against the supplied buffers.
- On `BZ_STREAM_END`, updates `*destLen` to bytes written and returns `BZ_OK`.
- If decompression returns `BZ_OK`, distinguishes unexpected EOF from output-buffer exhaustion based on remaining output space.

Notable implementation details:
- Always finalizes decompression state after successful initialization.
- Uses caller-provided output buffer; no resizing is attempted.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/buffdecompress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzassert.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzassert.c

This file defines libbzip2’s hard assertion failure handler for stdio-enabled builds.

Behavior:
- `BZ2_bz__AssertH__fail` prints a detailed internal-error report to stderr.
- Includes the libbzip2 version string from `BZ2_bzlibVersion`.
- Exits with status 3.

Notable implementation details:
- Includes both core private headers and stdio-private headers.
- Message is upstream-style and requests bug reports to the original maintainer.

Risks and caveats:
- Assertion failure terminates the process; no recovery path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzassert.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzbuffcompress.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzbuffcompress.c

This is another copy of `BZ2_bzBuffToBuffCompress`.

Behavior:
- Validates input/output pointers and compression parameters.
- Defaults work factor to 30 when zero.
- Initializes stream compression, runs `BZ_FINISH`, finalizes state, and updates destination length on success.
- Returns libbzip2 status codes such as `BZ_PARAM_ERROR`, `BZ_OUTBUFF_FULL`, or the compression error code.

Relationship:
- The contents match `buffcompress.c` in this group, suggesting alternate build naming or duplicate split-library packaging.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzbuffcompress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzcompress.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzcompress.c

This is the low-level streaming compression state machine for libbzip2.

Major responsibilities:
- `BZ2_bzCompressInit`: validates configuration, allocates `EState`, work arrays, and initializes run-length/block state.
- Input RLE: tracks repeated input bytes and writes bzip2 RLE representation into the current block.
- `BZ2_bzCompress`: handles `BZ_RUN`, `BZ_FLUSH`, and `BZ_FINISH` modes.
- `BZ2_bzCompressEnd`: frees compression state and work buffers.

State model:
- Modes: running, flushing, finishing, idle.
- States: input and output.
- `handle_compress` copies input into blocks, calls `BZ2_compressBlock`, and drains generated compressed bytes.

Notable implementation details:
- Block capacity is `100000 * blockSize100k - 19`.
- Work arrays are `arr1`, `arr2`, and `ftab`.
- RSC-added checks return `BZ_SEQUENCE_ERROR` if flush/finish makes no progress.

Risks and caveats:
- Correct usage requires stable `avail_in` during flush/finish; mismatches are sequence errors.
- The compressor is sensitive to caller-managed input/output buffer progress.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzcompress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzdecompress.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzdecompress.c

This is the low-level streaming decompression state machine for libbzip2.

Major responsibilities:
- `BZ2_bzDecompressInit`: validates options, allocates `DState`, initializes bitstream and output state.
- Converts inverse-BWT output into un-RLE’d bytes for both fast and small modes.
- `BZ2_bzDecompress`: alternates between block decoding and output draining.
- Validates per-block CRC and combined CRC.
- `BZ2_bzDecompressEnd`: frees `tt`, `ll16`, `ll4`, and state.

Notable implementation details:
- Fast path uses cached local variables in `unRLE_obuf_to_output_FAST` for speed.
- Supports randomized and non-randomized legacy bzip2 blocks.
- `BZ2_indexIntoF` supports small decompression table walking.
- Returns `BZ_OK` when more output/input progress is needed and `BZ_STREAM_END` after final CRC validation.

Risks and caveats:
- Depends on `BZ2_decompress` from the decompression parser file.
- CRC mismatch returns `BZ_DATA_ERROR`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzdecompress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzfeof.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzfeof.c

This is a tiny stdio helper for libbzip2’s stdio layer.

Behavior:
- `bz_feof(FILE *f)` reads one byte with `fgetc`.
- If EOF, returns true.
- Otherwise pushes the byte back with `ungetc` and returns false.

Notable implementation details:
- It checks practical EOF state without consuming data.
- Uses libbzip2 `Bool` type and stdio headers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzfeof.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzlib.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzlib.c

This file provides libbzip2 configuration and default allocation helpers.

Functions:
- `bz_config_ok`: verifies expected primitive sizes: `int` 4, `short` 2, `char` 1.
- `default_bzalloc`: allocates `items * size` with `malloc`.
- `default_bzfree`: frees non-null allocations.
- `bz_internal_error`: exits the process.

Notable implementation details:
- This is part of the split Plan 9-modified bzip2 library.
- `bz_internal_error` is marked as RSC-added replacement for missing original behavior.

Risks and caveats:
- `default_bzalloc` does not check multiplication overflow.
- Internal errors terminate with `exit(1)` and do not print context here.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzlib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzlib.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzlib.h

This is the public libbzip2 API header.

Contents:
- Action constants: `BZ_RUN`, `BZ_FLUSH`, `BZ_FINISH`.
- Return/status constants: `BZ_OK`, `BZ_STREAM_END`, `BZ_PARAM_ERROR`, `BZ_MEM_ERROR`, `BZ_DATA_ERROR`, and others.
- `bz_stream` structure with input/output pointers, availability counters, total counters, opaque state, and allocator hooks.
- Export/API macros for Windows and non-Windows builds.
- Prototypes for low-level compression/decompression APIs.
- Prototypes for buffer-to-buffer convenience APIs.
- Prototype for `BZ2_bzlibVersion`.

Notable implementation details:
- Header says it is modified from the original bzip2 distribution, mainly split into smaller pieces.
- It excludes many higher-level stdio APIs; those live in separate stdio headers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzlib.h -->