# Group Research: group_65_9front_sources_os_plan9_9front_sys_src_cmd_aux_listen1_c_sources_os_p_efd6567a1321

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/listen1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/listen1.c

`listen1` is a single-service network listener. It announces an address, accepts calls, optionally forks per connection, binds the accepted connection to `/dev/cons`, duplicates it to stdin/stdout, sets `net` to the connection directory, and execs the requested command.

Key controls are `-1` one-shot/no child fork, `-t` trusted mode skipping `becomenone`, `-v` preserving stdout, `-p` process limit with `/proc/$pid/wait` backpressure, `-n` namespace file, `-O` listener ctl options, and `-o` connection ctl options. By default it becomes user `none` and installs a new namespace before announcing.

Notable implementation details: default connection option is `keepalive`; stderr remains attached to the original process; `remoteaddr` reads `<netdir>/remote` and strips service after `!`; overload during fork failure rejects the call with `host overloaded`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/listen1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/mnihongo/mnihongo.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/mnihongo/mnihongo.c

`mnihongo` filters troff device-independent output, replacing characters from a Japanese font position with PostScript bitmap masks generated from Plan 9 bitmap fonts. It preserves most troff output commands while tracking horizontal and vertical positions.

It loads `/lib/font/bit/pelm/unicode.9x24.font`, opens subfonts lazily by rune range, renders a rune into a `Memimage`, unloads 1-bit rows into hexadecimal image data, and emits `x X PS ... imagemask` commands at the current troff position.

The parser handles troff motions, font changes, device-control `x` records, drawing records, comments, page/newline commands, and the compact `nnc` motion+character form. It identifies the Japanese font by seeing `x f <slot> Jp...` controls.

Caveats: the code assumes the pelm font layout and has small fixed buffers for strings and row data; failures in font parsing or subfont loading are fatal.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/mnihongo/mnihongo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/mouse.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/mouse.c

`mouse` probes and configures serial mouse hardware through `/dev/eia*` and reports the detected type to `/dev/mousectl`. It supports Microsoft-compatible `M`, Type `W`, Logitech/Mouse Systems style `C`, plus direct passthrough configuration for `ps2...` and `synaptic...`.

Detection resets serial control lines, tries known baud and line settings, probes for `M`/`M3`, sends Type W configuration commands, and probes Type C with status command `s`. Baud setup uses timed writes, alarms, and a notification handler to avoid hanging on unresponsive serial devices.

Options include `-b` baud, `-d` default type, `-n` detect without writing `/dev/mousectl`, and `-D` debug dumps. Final configuration is generally `serial <port>` with optional `M` suffix for Microsoft-compatible mode.

Risk points: heavy dependence on Plan 9 serial control strings (`b1200`, `l7`, `d1`, `r1`, etc.); timeout paths exit the program; Type W 9600 support is gated by a returned configuration bit.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/mouse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/ms2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/ms2.c

`ms2` converts either a Plan 9 executable or a raw binary file into Motorola S-record output. It uses `libmach` `crackhdr` for executable headers unless `-b` raw binary mode is selected.

Options select data segment only (`-d`), suppress end record (`-s`), set base address (`-a`), set page alignment between text/data (`-p`), halfword byte-swap (`-h`), binary input (`-b`), and S1/S2/S3 record width (`-1`, `-2`, `-3`). Records are capped at 32 payload bytes.

For executables, it emits text then page-aligns `addr` before emitting data; for raw files it emits the whole file from address 0 and writes an S9 trailer. Checksums are the standard one-byte complement of length, address, and data.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/ms2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/msexceltables.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/msexceltables.c

`msexceltables` reads BIFF Excel workbook streams and prints sheet contents as delimited text. It handles BIFF8 Unicode strings, shared string tables, worksheet records, numeric cells, inline labels, booleans/errors, RK compressed numbers, multiple RK records, column widths, date modes, and XF format indices.

The file builds an in-memory sorted row/column linked structure per sheet, then dumps it with padding, truncation, optional rc-style quoting, sheet and column range filters, and a configurable delimiter. Date/time formatting is recognized for selected built-in Excel format IDs, with Lotus 1-2-3/Excel 1900 leap-year compatibility noted in epoch comments.

The BIFF parser reads records with `getrec`, dispatches selected opcodes, and skips unhandled record payloads. `gstr` handles BIFF8 continuation records, Unicode/byte modes, rich-text runs, and Asian phonetic extension bytes.

Options: `-D` debug hex dump, `-a` all sheet types, `-q` no quoting, `-d` delimiter, `-n` no padding, `-t` truncate, `-c` column range, `-w` worksheet range.

Caveats: only a subset of BIFF records and formats is implemented; range parser uses 1-based position in output iteration; several malformed files cause `sysfatal`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/msexceltables.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/mswordstrings.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/mswordstrings.c

`mswordstrings` extracts plain-ish text from an OLE-mounted Word `WordDocument` stream. It reads the Word FIB header, seeks from `fcMin` to `fcMac`, and translates control characters into newlines, tabs, field markers, placeholder labels, or suppressed output.

The generated `Fibhdr` reader decodes little-endian fields and bit flags from the first 0x22 bytes. Only the basic text range is used; formatting, piece tables, compression, encryption, and Unicode runs are not fully parsed.

Special mappings include paragraph end to blank line, hard/page breaks to newlines, field begin/separator/end to `<`, `:`, `>`, and some embedded object/date/time placeholders. Zero bytes are skipped to tolerate mixed single-byte and interleaved-zero text regions.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/mswordstrings.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/multi/mkmulti -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/multi/mkmulti

`mkmulti` is an rc build script that creates a combined `multi` binary from multiple Plan 9 commands. For each command name, it emits a renamed `<cmd>_main` prototype into `multiproto.h`, a dispatch entry into `multi.h`, builds the command object files with `mk`, prefixes symbols using `aux/8prefix`, and links all objects with `multi.c`.

It has special handling for `disk/prep` and `disk/fdisk`, tries several build directories and output names, moves generated `.8` objects into numbered `a.N.8` files, and cleans most command directories afterward.

The script depends on Plan 9 toolchain commands: `mk`, `8c`, `8l`, `hoc`, `sed`, `basename`, and `aux/8prefix`. It assumes `/sys/src/cmd` layout and 386 object naming.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/multi/mkmulti -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/multi/multi.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/multi/multi.c

`multi.c` is the runtime dispatcher for binaries produced by `mkmulti`. It includes generated `multiproto.h` and `multi.h`, maps command names to renamed `main` functions, and invokes the matching function with `argv` shifted so the selected command sees itself as `argv[0]`.

It strips any path prefix from the requested command name. If called without a command, or if no command matches, it prints an error and exits.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/multi/multi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/na/na.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/na/na.h

`na.h` declares the patch metadata used by the NCR53c8xx script assembler and a `na_fixup` interface. A patch records a longword offset and an 8-bit type.

`na_fixup` accepts a script image, physical addresses for script and register space, the patch array and count, plus an external-value callback. The header is a small shared contract between generated assembler output and runtime fixup code elsewhere.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/na/na.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/na/na.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/na/na.y

`na.y` is a yacc grammar and implementation for an NCR53c8xx SCRIPTS assembler. It preprocesses an input file through `cpp`, parses labels, constants, externs, expressions, SCSI phases, register names, move/select/reselect/jump/call/int/set/clear/nop/return/de fw instructions, and emits a C initializer `unsigned long na_script[]`.

The assembler performs two passes. Pass 1 builds symbols and computes `dot`; pass 2 prints instruction longwords with source-line comments, records patch entries, emits `NA_SCRIPT_SIZE`, `na_patches[]`, external enum values, label enums, and constant defines.

It has a typed expression system: constants, addresses, table addresses, externs, registers, unknowns, and errors. Type tables determine legal arithmetic; patch types are generated for address, register, extern, and certain immediate/register move cases.

The lexer supports decimal, octal, hex, and binary integers; symbols; comments beginning with `;`; and `#line` directives from cpp. It recognizes a large token table for NCR/SCSI register names and instructions.

Risk points: fixed limits for cpp options, patches, external symbols, source line length, and filename length; some range checks only warn under `wflag`; relative address encoding is 24-bit signed and may zero bad values.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/na/na.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/nfsmount.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/nfsmount.c

`nfsmount` is an RPC client for the NFSv3 mount protocol. It can call mountd procedures `null`, `mnt path`, `dump`, `umnt path`, `umntall`, and `export`, with `export` as default.

It optionally contacts the portmapper first to resolve the mountd port, then reconnects to the NFS mount program. Calls are constructed with `SunCall` metadata and, for mount calls, a hard-coded AUTH_SYS credential for user/group 1001 and machine name `gnot`.

Options: `-R` enables chatty RPC tracing, `-m` disables portmapper lookup. It uses `libsunrpc` and generated `nfs3` mount structures, including unpacking export and mount-list payloads.

Notable issue: command table lists `umntall` with `narg` 1 even though the function ignores arguments and usage says none.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/nfsmount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/olefs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/olefs.c

`olefs` exposes Microsoft OLE Compound File streams as a read-only 9P filesystem, mounted by default at `/mnt/doc`. It parses the 512-byte OLE header, FAT/depot block maps, root directory chain, and small-stream storage.

The in-memory `Ofile` holds the BIFF/OLE block map, root block, small-block root, and input `Biobuf`. `Odir` represents directory entries with UTF-16 names, type, tree links, stream start, and stream size.

Reads follow FAT chains for large streams and use the root small-block depot for streams under 0x1000 bytes. Directory entries are traversed as a binary tree with recursive child directories. Names are sanitized by converting spaces to U+2423 and control/slash/problem bytes to `:`.

The 9P service implements read-only file reads via `oleread`; directories and files are created in an in-memory tree using lib9p. It detects the OLE magic header and rejects bad magic.

Caveats: no full cycle detection beyond a recursion depth cap of 100; timestamps are ignored; malformed FAT/depot structures mostly fail with fatal errors or nil open.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/olefs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/pcmcia.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/pcmcia.c

`pcmcia` decodes PCMCIA CIS tuples from an attribute-memory file, defaulting to `#y/pcm0attr`. It reads every byte from even offsets (`2*pos`), reflecting attribute-memory layout, and prints parsed tuple information.

Supported tuple parsers include device descriptors, long-link multi-function tuples, version strings, configuration register location, configuration entries, function IDs, power descriptors, timing, I/O ranges, IRQ masks, and memory windows. `-x` also prints raw bytes as hex while reading.

The tuple dispatcher uses tuple type byte and link length, then advances to the next tuple by `next+2+link`. Long-link multi-function parsing recursively follows linked CIS chains.

Caveats: parsing is print-oriented and tolerant of partial reads; unhandled tuple types are skipped; tuple recursion and bad link targets can lead to confusing output but generally stop on read failure.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/pcmcia.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/portmap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/portmap.c

`portmap` is a command-line SunRPC portmapper client. It supports `null`, `set prog vers proto port`, `unset prog vers proto port`, `getport prog vers proto`, and `dump`, defaulting to `dump`.

It builds `SunCall` metadata for the portmapper program/version, dials `udp!portmap`, installs RPC formatters, and dispatches commands through generated `PortT*`/`PortR*` structures. `dump` prints program, version, protocol, and port for each returned map.

Option `-R` enables chatty RPC tracing. Rejected set/unset replies print `rejected`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/portmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/rdwr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/rdwr.c

`rdwr` is an interactive read/write exerciser for a file opened `ORDWR`. With `-w`, it reads and prints the current contents first. Then it repeatedly prompts, writes each input line minus its trailing newline at offset 0, seeks back, reads up to 8192 bytes, and prints the result.

It is useful for testing device files and control interfaces where writes change immediately readable state. Errors are printed but the loop continues unless open fails.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/rdwr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/realemu/arg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/realemu/arg.c

`arg.c` implements operand objects for the real-mode x86 emulator. It allocates short-lived `Iarg` values from a circular buffer inside `Cpu`, representing registers, memory operands, far pointers, and constants.

`ar` reads an operand with width masking, routing memory through the segment:offset bus mapping and registers through `cpu->reg`. `ars` returns sign-extended values for 1/2/4-byte operands. `aw` writes memory through bus callbacks and preserves unaffected bits for 8- and 16-bit register writes, including high-byte register tags.

This file is the central abstraction between decoded instructions and the bus/register model.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/realemu/arg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/realemu/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/realemu/dat.h

`dat.h` defines the real-mode emulator’s core data model: register indices, `Iarg`, decoded `Inst`, `Bus`, `Cpu`, `Pcidev`, and `Pit`.

It enumerates processor flags, trap/interrupt numbers, operand tags and operand descriptor kinds, and every supported opcode class (`OADD`, `OMOV`, `OJUMP`, etc.). `Cpu` includes general/segment registers, instruction count, memory and port buses, trap state, default operand/address/stack widths, jump buffer, and operand scratch buffer.

The header frames the emulator as a 16/32-bit-capable x86 decoder/executor with segmented real-mode addressing over pluggable memory and I/O buses.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/realemu/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/realemu/decode.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/realemu/decode.c

`decode.c` maps x86 opcodes to `Inst` structures. It contains primary and `0F` opcode tables plus selected group tables for arithmetic, shifts, tests, pushes/pops, calls/jumps, string ops, segment overrides, operand/address-size prefixes, conditional moves/jumps/sets, bit operations, and basic CPUID.

The decoder handles instruction prefixes, ModR/M and SIB decoding for 16-bit and 32-bit addressing, default segment selection, displacements, immediates, far pointers, string source/destination operands, segment registers, and high-byte registers.

Unsupported or arcane instructions are represented as `OBAD`, causing execution to trap later. Group decoding switches on the ModR/M `reg` field after operands are initially resolved.

This file is decode-only; actual semantics are in `xec.c`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/realemu/decode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/realemu/fmt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/realemu/fmt.c

`fmt.c` provides debug formatters for emulator instructions, flags, and CPU state. `%I` formats decoded instructions, `%J` formats selected flags, and `%C` formats a full CPU line with registers, flags, current opcode, and disassembly.

Instruction formatting understands registers, immediates, far pointers, relative targets, ModR/M memory forms, segment overrides, 16/32-bit address expressions, REP prefixes, and conditional jump mnemonic selection. It protects memory dereferences while formatting by saving/restoring the CPU jump buffer.

The code is diagnostic infrastructure used by `realemu/main.c` tracing.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/realemu/fmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/realemu/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/realemu/fns.h

`fns.h` declares the emulator subsystem interfaces: operand constructors/read/write, decoder, executor/trap/interrupt entry points, formatters, PIT operations, and PCI config access helpers.

It also defines `BDFBNO`, `BDFDNO`, and `BDFFNO` macros for extracting bus/device/function fields from a PCI BDF value.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/realemu/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/realemu/loadcom.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/realemu/loadcom.c

`loadcom` loads a DOS `.COM` program into Plan 9 real-mode execution devices. It opens the input file, `/dev/realmode`, and `/dev/realmodemem`, reads up to 0xFF01 bytes, writes the program at `CS:0100`, and writes an initialized `/386/include/ureg.h` register image.

It sets CS/DS/ES/FS/GS to `0x1000`, SS to `0`, SP to `0xfffe`, and PC to `0x0100`. It is a thin helper for bootstrapping real-mode code through the realmode device interface.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/realemu/loadcom.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/realemu/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/realemu/main.c

`realemu/main.c` implements a 9P service exposing emulated real-mode execution as `realmode` and memory as `realmodemem`, usually mounted before `/dev`. Writes of a `Ureg` to `realmode` execute the emulator and update the register image; reads return the last image. `realmodemem` reads/writes the emulator’s 1 MiB memory buffer.

It initializes memory buses for RAM, ROM, VGA framebuffer passthrough, and bad regions; port I/O buses for PIC, PIT, keyboard, RTC, DMA page registers, A20, PCI config space, and fallback Plan 9 port files `#P/iob`, `#P/iow`, `#P/iol`. Real hardware memory is accessed via `#P/realmodemem`.

`realmode` translates Plan 9 `Ureg` fields into emulator registers, optionally invokes an interrupt vector, runs instruction batches through `xec`, handles traps/pseudo-traps, then writes registers back. `-t` enables CPU trace, `-p` port trace, `-D` 9P chatty mode, `-s` service file, and `-m` mountpoint.

The service serializes execution through a worker proc and channels, supports flush interruption, and rejects concurrent requests with `device is busy`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/realemu/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/realemu/pci.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/realemu/pci.c

`pci.c` caches opened PCI config-space raw files for the emulator. `pciopen` maps a BDF to `#$/pci/<bus>.<dev>.<fn>raw`, opens it `ORDWR`, and stores the result in a linked list even if open failed.

`pcicfgr` and `pcicfgw` perform `pread`/`pwrite` at config offsets. This backs real-mode I/O ports `0xcf8`/`0xcfc` in `main.c`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/realemu/pci.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/realemu/pit.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/realemu/pit.c

`pit.c` emulates the Intel 8253/8254 programmable interval timer. It supports counter latching, status latching/readback, BCD conversion, gate transitions, low/high/lo-hi access modes, and output modes 0 through 5 including rate generator and square wave variants.

`clockpit` advances three timer channels by a number of PIT cycles, honoring gate and reload behavior. `rpit` reads channel count/status latches or live counts. `wpit` handles control words, readback commands, and channel count writes.

The model is good enough for BIOS and real-mode code timing interactions used by `realemu`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/realemu/pit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/realemu/xec.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/realemu/xec.c

`xec.c` implements instruction execution for the real-mode x86 emulator. It covers stack control flow, interrupts, returns, enter/leave, push/pop families, flag transfer, arithmetic/logical/shift/rotate/bit operations, multiply/divide, condition evaluation, branches, loops, moves, sign/zero extension, string ops, I/O, CPUID, NOP, and HLT.

Execution uses `decode` to fill an `Inst`, advances RIP to the post-instruction offset, then dispatches through `exctab`. Traps restore RIP to `oldip` and longjmp out. `intr` pushes FLAGS/CS/IP and loads an interrupt vector from physical address `v*4`.

String instructions honor REP/REPNE/REPE and direction flag. Arithmetic helpers centralize flag setting for carry, overflow, sign, zero, and parity. Unsupported opcodes trap as `EBADOP`.

Notable simplifications: no floating point/MMX/control-register instruction support; CPUID returns a small synthetic Intel-like table; many flags are approximate enough for BIOS-style code but not a full CPU verification model.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/realemu/xec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/reboot.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/reboot.c

`reboot` is a watchdog utility. It forks into the background, repeatedly `dirfstat`s a target file once every five minutes, and reboots via `/dev/reboot` if the stat fails for a reason other than an alarm timeout.

If no file is supplied, it builds a default path from `/env/cputype` as `/<cputype>/lib`. The watchdog request itself is alarm-limited to 60 seconds. This is intended to detect loss of a critical fileserver connection while tolerating temporary slowness.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/reboot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/searchfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/searchfs.c

`searchfs` is a custom 9P filesystem over an in-memory ASCII database. It exposes `search` and `stats` files under a mounted root. Clients write URL-style queries to `search`, then read matching database lines back.

Search strings are parsed as `tag=val&...`; supported tags are `search` and `skip`. Multiple `search` terms are split on whitespace and matched case-insensitively. The longest term becomes a Boyer-Moore-like quick matcher; remaining terms are exact line filters.

The filesystem implements its own 9P message loop and fid table instead of lib9p. It supports version, attach, walk, open, read, write, clunk, and stat; create/remove/wstat/auth are rejected. Flush requests are ignored by design.

Limitations: explicitly ASCII-oriented; database is read fully into memory; `stats` currently reads as empty; root directory read only returns the `search` entry even though `stats` is walkable/stat-able.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/searchfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/seek.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/seek.c

`seek` benchmarks random 512-byte reads from a block device or file. It opens the argument read-only, computes sector count from file size, performs 100 random sector `pread`s, and prints elapsed time divided by `100000000`, effectively seconds per ten reads scale.

It is a simple latency probe for `/dev/sd??/data`-style devices and exits on any short read.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/seek.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/statusbar.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/statusbar.c

`statusbar` displays progress from stdin lines containing `n d`. It can open a new graphical window and draw a green progress bar with percentage text, or fall back to terminal text mode.

Options: `-w` window rectangle, `-t` force text mode, `-k` do not turn Delete/ETX into an interrupt, and optional title. In graphical mode it forks an event watcher so keyboard interrupt can post a note to the parent.

The text mode uses backspaces to update only changed bar content. Graphical mode tracks last pixel width and percent to avoid unnecessary redraws.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/statusbar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/statusmsg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/statusmsg.c

`statusmsg` displays the latest line read from stdin, either in a new graphical window or in terminal text mode. It shares window-opening and keyboard-interrupt behavior with `statusbar`.

Options are `-w`, `-t`, `-k`, and optional title. Graphical mode clears and redraws the message area each update; text mode overwrites prior text with backspaces and can prefix the title.

It uses `Bsize` allocation for the message buffer and `utfnlen` to avoid splitting the line incorrectly when copying.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/statusmsg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/stub.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/stub.c

`stub` mounts a minimal 9P filesystem that presents exactly one child name at a requested path. The child can be a file or, with `-d`, a directory. It is useful for satisfying path existence expectations without providing content.

It supports attach, walk, open, read, write rejection, and stat. Root reads list the single child; opening anything other than root is denied. The mountpoint is derived by splitting the supplied `path/name`, and the service is mounted `MBEFORE`.

Option `-D` enables lib9p chatty logging.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/stub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/tablet.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/tablet.c

`tablet` bridges `/dev/tablet` motion lines into `/dev/mousein`. It reads lines beginning with `m x y b ...`, parses x/y/buttons, and writes `A x y b` events to mouse input.

It exits fatally on open or read failure and ignores non-motion or malformed lines. The local file has 31 lines, while the work item metadata listed 32.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/tablet.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/timesync.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/timesync.c

`timesync` is a clock synchronization daemon. It can synchronize from filesystem time, RTC, UTC file, GPS file, or NTP, adjust kernel time and frequency, optionally update RTC, and optionally serve SNTP/NTP replies on one or more networks.

It supports modern `/dev/bintime` or older `/dev/nsec` plus `/dev/fastclock`/`/dev/timing` interfaces. Time corrections can set absolute time, slew a delta over a period, and adjust frequency. `-i` makes it read-only/impotent for testing.

The main loop samples the chosen source, discards bad samples, sets time immediately if error exceeds 10 seconds, otherwise slews a damped correction, adapts the sampling period based on accuracy, estimates oscillator frequency from retained samples, caps error from frequency changes, and persists frequency under `dir` as `ts.<sysname>.<type>[.<server>]`.

NTP client mode queries configured servers, computes offset and RTT from NTP timestamps, selects the lowest metric based on root dispersion and delay, and derives local stratum/root delay/dispersion. NTP server mode listens on UDP ntp in header mode, replies to client mode 3 packets, and fills stratum, precision, root delay/dispersion, root id, reference, receive, originate, and transmit timestamps.

Options include accuracy `-a`, state directory `-d`, debug `-D`, filesystem `-f`, GPS `-G`, root id `-I`, logging `-l`, local-time RTC correction `-L`, NTP `-n`, RTC `-r`, serve network `-s`, stratum `-S`, and UTC `-U`.

Caveats: code assumes Plan 9 clock devices and kernel write protocols; root ID defaults vary by source; several source failures shorten retry period but otherwise continue.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/timesync.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/trampoline.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/trampoline.c

`trampoline` connects two byte streams: stdin/stdout or an alternate address to a target dial address. It forks two copy directions and posts a hangup note when one side ends. With `-9`, it preserves 9P message framing by reading the 4-byte length and forwarding whole messages.

Options include `-a` alternate local dial address, `-m` netdir for MAC authorization, `-o` ctl options for the outgoing target, and `-t` inactivity timeout. Timeout mode forks a supervisor that checks an `activity` flag and posts a group timeout note.

MAC checking reads local/remote endpoint files, looks up remote IP in `<net>/arp`, then checks NDB for an `ether=<mac>` entry with `trampok`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/trampoline.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/txt2uimage.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/txt2uimage.c

`txt2uimage` wraps a file or stdin into a U-Boot image with an 8-byte script payload prefix. It writes a 64-byte U-Boot header, data length and zero word, original data, then computes and fills data CRC and header CRC.

The image type is `IH_TYPE_SCRIPT`, compression is none, load/entry are zero, and the output defaults to `<input-name>.u` unless `-o` is supplied. It rejects files larger than 32-bit size minus prefix.

Caveat: `copy` uses `i = n & sizeof(buf) - 1`, which depends on C precedence and likely does not mean `n & (sizeof(buf)-1)` unless parsed as intended by the compiler.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/txt2uimage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/unbflz.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/unbflz.c

`unbflz` decompresses a simple `BLZ\n` format from a file or stdin to stdout. It reads total output length, then a block table whose entries are either literal lengths marked with high bit set or copy lengths followed by source offsets.

After validating that summed block lengths equal the output length, it reconstructs into memory, reading literal runs from the input stream and copying backreferences from prior output. Its `copy` function deliberately copies forward byte by byte for overlap semantics.

All integers are big-endian. The full output buffer and block table are allocated in memory.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/unbflz.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/usage.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/usage.c

`usage` prints a generated usage line using environment variables. It reads `$0`, `$flagfmt`, and `$args`, derives the command basename, and writes `usage: <cmd> ...` to stderr.

`flagfmt` syntax is parsed as comma/space separated flag descriptors. Single-letter flags without arguments are grouped into one `[-abc]`; flags with argument names print as `[-x arg]`. It handles UTF-8 flag runes.

It exits with status `usage` and reports an error if `$0` is missing.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/usage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/usbsdmux.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/usbsdmux.c

`usbsdmux` controls a USB-SD-Mux-like device by sending SCSI/vendor raw commands to an I2C GPIO expander at address `0x41`. Modes are `off`, `dut`, and `host`, with an optional raw device path defaulting to `/dev/sdUdca10/raw`.

`wr` sends a command header, writes register/value data, then reads textual status and requires zero. The program first disconnects all paths, configures all GPIO pins as outputs, sleeps 100 ms, then applies the selected output pattern.

GPIO bits represent data, power, DUT, and card switching lines. Failures in command writes, data writes, status reads, or nonzero status are fatal.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/usbsdmux.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/3dfx.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/3dfx.c

`3dfx.c` is a VGA controller module for 3Dfx Banshee, Voodoo3, and Voodoo5 devices. It locates PCI vendor `0x121A`, maps I/O register BAR 2, records up to 0x100 bytes of MMIO-style registers via port I/O, determines max PLL frequency and framebuffer size, and configures display mode registers.

It computes PLL parameters from reference frequency using m/n/p ranges, supports standard VGA clocks and programmed PLL clocks, and uses two-pixels-per-clock mode above 135 MHz when allowed and mode width is divisible by 16.

Mode setup programs screen size, stride, pixel format for 8/16/32 bpp, DAC mode, video processor config, VGA init, CRT overflow bits, and black attribute entry. `load` writes extended CRT registers and 3Dfx registers; `dump` prints captured registers and PLL-derived frequencies.

It exposes `Ctlr tdfx` and a placeholder `tdfxhwgc`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/3dfx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/ark2000pv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/ark2000pv.c

`ark2000pv.c` is a VGA controller module for the ARK Logic ARK2000PV accelerator. It unlocks extended registers, snarfs sequencer/crt state and coprocessor status, and derives VRAM size from sequencer register bits.

It advertises linear aperture and `Hpclk2x8` support. Initialization handles optional pixel-clock doubling timing adjustments, CRT overflow bits, interlace registers, memory/aperture mode, depth-specific setup for 1 bpp and 8 bpp, FIFO/pitch control by horizontal size, clock select bits, and palette black entry.

`load` performs a careful clock switch, optionally toggles the sequencer for a W30C516 RAMDAC quirk, enables linear aperture if requested, writes aperture base/size registers, and writes extended sequencer/CRT registers. `dump` prints relevant extended state.

It exposes `ark2000pv` and placeholder `ark2000pvhwgc` controllers.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/ark2000pv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/att20c49x.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/att20c49x.c

`att20c49x.c` is a RAMDAC module for ATT20C490/491/492 true-color CMOS RAMDACs. It validates requested pixel clock against a speed grade parsed from the controller name suffix, defaulting to 55 MHz.

`load` can put 20C491-class chips to sleep, then writes control register 0 to select mode and wake the chip. 8-bit color expansion logic is present but disabled with `&& 0`.

It exports three controller descriptors: `att20c490`, `att20c491`, and `att20c492`.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/att20c49x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/att21c498.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/att21c498.c

`att21c498.c` is a RAMDAC module for the ATT21C498 PrecisionDAC with a 16-bit interface. It implements indirect register access by reading Pixmask four times plus register index, then reading/writing Pixmask and resetting the sequence with `PaddrW`.

It advertises `Hpclk2x8`. Initialization derives speed grade from controller name, chooses max PCLK based on 8-bit or 2x8-bit mode, halves requested clock and resyncs if using internal 2x8-bit doubling above 80 MHz, and validates the resulting clock.

`load` sleeps the DAC, writes mode bit `0x20` for 2x8-bit if selected, leaves optional 8-bit color mode disabled, and wakes the DAC by writing control register 0. `dump` prints the six indirect registers.

<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/aux/vga/att21c498.c -->