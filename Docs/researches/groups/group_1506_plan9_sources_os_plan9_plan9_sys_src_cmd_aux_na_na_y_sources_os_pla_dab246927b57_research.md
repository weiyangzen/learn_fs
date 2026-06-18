# Group Research: group_1506_plan9_sources_os_plan9_plan9_sys_src_cmd_aux_na_na_y_sources_os_pla_dab246927b57

Scope verified against `Docs/research_subset_a.md`: all files are under included source tree `sources/os/plan9/plan9`. Every listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/na/na.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/na/na.y

Yacc grammar and support code for `na`, an NCR53c8xx SCRIPTS assembler. It preprocesses one input file through `/bin/cpp`, performs a first parse to resolve labels/symbols, then a second parse to emit C initializers for `na_script[]`, relocation/patch metadata, external symbol enums, label enums, and constant defines.

Core behavior:
- Defines NCR53c8xx instruction grammar for `MOVE`, `SELECT`, `RESELECT`, `WAIT`, `JUMP`, `CALL`, `RETURN`, `INT`, `INTFLY`, `SET`, `CLEAR`, `NOP`, and `DEFW`.
- Tracks assembler location counter `dot` in bytes while emitting 32-bit script words.
- Implements symbol typing with `Const`, `Addr`, `Table`, `Extern`, `Reg`, `Unknown`, and `Error`.
- Uses expression type tables to reject invalid arithmetic such as multiplying addresses or mixing incompatible symbolic types.
- Computes relative branch addresses with signed 24-bit range checking.
- Emits patch entries for address/register/external operands through `patchtype()` and `fixup()`.

Important functions:
- `main()` parses `-D` cpp options, preprocesses input, runs pass 1/pass 2, and emits output C.
- `yylex()`, `yygetc()`, `yyrewind()` implement the lexer, including `#line` handling from cpp.
- `setsym()`, `findsym()`, `eval()` manage symbol table and typed expressions.
- `regmove()` encodes register/SFBR move and ALU forms.
- `chkreladdr()` decides whether an operand can be compiled as relative now or needs patching.
- `fixup()` emits `struct na_patch na_patches[]`, `NA_PATCHES`, external enums, label enums, and constants.

Dependencies and integration:
- Includes Plan 9 libc plus local `na.h`.
- Calls `/bin/cpp` with `-+ -N` and user `-D` options.
- Output is generated C data intended to be compiled into a NCR SCSI driver or related firmware/script consumer.

Notable risks:
- Fixed-size arrays: `MAX_PATCHES` is 1000 and `externp` has 100 slots without robust overflow checks in all paths.
- Lexer line buffer is fixed at 500 bytes.
- `eval()` divides without checking zero divisor.
- `preprocess()` does not inspect child exit status beyond `wait()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/na/na.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/nfsmount.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/nfsmount.c

Small SunRPC/NFSv3 mount protocol client. It connects to a host, optionally asks portmap for the NFS mount daemon port, then runs one mount-protocol command.

Commands:
- `null`
- `mnt path`
- `dump`
- `umnt path`
- `umntall`
- `export` default

Core behavior:
- Uses `libsunrpc` and generated `nfs3.h` mount structures.
- `getport()` performs a portmapper `GETPORT`.
- `mountCall()` fills SunRPC program/version/procedure metadata and attaches AUTH_SYS credentials for calls.
- `tmnt()` prints the returned NFS file handle and accepted auth flavors.
- `tdump()` prints current mount entries.
- `texport()` unpacks and prints exported paths and groups.

Dependencies and integration:
- Includes `<thread.h>`, `<sunrpc.h>`, and `<nfs3.h>`.
- Uses Plan 9 thread entry `threadmain()`.
- Shares protocol idioms with `portmap.c`.

Notable risks:
- Static fake AUTH_SYS credential `unixauth` is hard-coded as user/group 1001 and host `gnot`.
- `tab` declares `umntall` as requiring one argument even though usage says none and `tumntall()` ignores arguments; this looks like a command table bug.
- Port rewriting assumes network address contains `!`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/nfsmount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/olefs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/olefs.c

Read-only 9P filesystem for Microsoft OLE Compound File Binary Format documents. It parses the compound file block allocation tables and directory tree, then exposes streams/storages as a mounted Plan 9 file tree.

Core structures:
- `Ofile`: backing `Biobuf`, number of FAT blocks, big-block map, root block, small-block map start.
- `Odir`: parsed directory entry with UTF-16 name, type, tree links, stream start block, and stream size.

Core behavior:
- Validates OLE magic `D0 CF 11 E0 A1 B1 1A E1`.
- Reads depot/FAT blocks from the header and extended depot chain.
- Reads directory entries from the root chain.
- Supports big streams through normal block chains and small streams via the root small-block depot.
- Builds a synthetic 9P tree with sanitized names, replacing spaces with `␣` and unsafe/control runes with `:`.
- Serves stream contents from `oleread()`.

Important functions:
- `oleopen()` parses the header and block map.
- `oreadblock()`, `oreadchain()`, `oreadfile()` implement block-chain reads.
- `convM2OD()` decodes on-disk OLE directory entries.
- `filldir()` recursively converts OLE storage tree entries into lib9p `File` objects.
- `main()` mounts the filesystem at `/mnt/doc` or `-m mtpt`.

Dependencies and integration:
- Uses Plan 9 `bio`, `thread`, and `<9p.h>`.
- Exposes a `Srv` with `.read = oleread`.

Notable risks:
- Complex OLE formats are only partially supported; timestamps are explicitly marked as a BUG.
- Recursion guard is a hardcoded depth limit of 100.
- `runestrecpy(rbuf, rbuf+sizeof rbuf, ...)` uses byte-size arithmetic on a Rune array, which is suspicious in modern terms.
- Several parse failures print diagnostics rather than returning structured errors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/olefs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/pcmcia.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/pcmcia.c

PCMCIA Card Information Structure tuple decoder. It reads attribute memory, decodes known CIS tuples, and prints human-readable information about devices, version strings, function IDs, configuration registers, power, timing, I/O ranges, IRQs, and memory ranges.

Core behavior:
- Defaults to reading `#y/pcm0attr`; optional file argument overrides it.
- Attribute memory is read with `seek(fd, 2*pos, 0)`, matching PCMCIA attribute-space byte layout.
- `-x` prints raw hex bytes as they are read.
- Tuple dispatch is through `parse[256]`.

Supported tuple handlers:
- Device tuples: `tdevice()`.
- Multifunction long links: `tlonglnkmfc()`.
- Version 1 strings: `tvers1()`.
- Config registers: `tcfig()`.
- Config entries: `tentry()`.
- Function ID: `tfuncid()`.

Dependencies and integration:
- Standalone Plan 9 command using libc only.
- Primarily diagnostic/inspection tooling, not a driver.

Notable risks:
- Many decoder routines trust tuple lengths and stream structure; malformed CIS data may desynchronize parsing.
- `tuple()` always prints the tuple type, even without `-x`, so output is inherently verbose.
- The multifunction recursion follows linked tuple chains without a global visited-set.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/pcmcia.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/portmap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/portmap.c

SunRPC portmapper client. It connects to a host’s UDP portmap service and runs a requested portmapper procedure.

Commands:
- `null`
- `set prog vers proto port`
- `unset prog vers proto port`
- `getport prog vers proto`
- `dump` default

Core behavior:
- `portCall()` fills SunRPC portmapper program/version/procedure metadata.
- `tset()` and `tunset()` submit port mappings and print `rejected` on false response.
- `tgetport()` prints mapped port.
- `tdump()` prints all returned mappings as `prog vers proto port`.

Dependencies and integration:
- Uses `<thread.h>` and `<sunrpc.h>`.
- Uses generated/global `portProg` formatting/protocol metadata.
- Related to `nfsmount.c`, which embeds a smaller `getport()` helper.

Notable risks:
- No authentication or filtering; it exposes raw portmapper operations to the user.
- Numeric parsing uses `strtol()` without validating trailing garbage.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/portmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/rdwr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/rdwr.c

Tiny interactive read/write utility for Plan 9 device files or other seekable files.

Core behavior:
- Opens one file `ORDWR`.
- Optional `-w` performs an initial read and prints the result.
- Repeatedly prompts with `> `, reads a line from stdin, writes it to offset zero without the trailing newline, seeks back to zero, then reads and prints the file contents.

Dependencies and integration:
- Standalone libc command.
- Useful for manually poking text control files in `/dev`, `/proc`, or device namespaces.

Notable risks:
- Assumes the input line has a trailing newline and writes `n-1` bytes.
- Uses fixed 8192-byte read buffer and 1000-byte stdin reads.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/rdwr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/reboot.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/reboot.c

Watchdog-style reboot helper. It monitors a file or CPU-library path and reboots if a stat request fails for reasons other than timeout/alarm.

Core behavior:
- If an argument is supplied, monitors that path.
- Otherwise reads `/env/cputype` and monitors `/<cputype>/lib`.
- Forks into the background.
- Opens the monitored path and every five minutes attempts `dirfstat()`, with a one-minute alarm.
- If `dirfstat()` fails without alarm interruption, writes `reboot` to `/dev/reboot`.

Important functions:
- `readenv()` reads `/env/name`.
- `ding()` converts alarm notes into continuable interruptions.
- `reboot()` writes to `/dev/reboot`.

Dependencies and integration:
- Standalone Plan 9 libc command.
- Depends on `/dev/reboot`, `/proc` note/alarm behavior, and namespace file availability.

Notable risks:
- Reboots on non-alarm stat failure, so namespace/server transient errors can become machine resets.
- Does not log failures before reboot.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/reboot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/searchfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/searchfs.c

In-memory ASCII database search filesystem. It reads a database file into memory and serves a tiny 9P filesystem with `search` and `stats` entries. Clients write query strings to `search` and read matching database records back.

Filesystem layout:
- Root directory.
- `search`: writable query endpoint and readable result stream.
- `stats`: present but currently returns empty reads.

Search query format:
- URL-style parameters `tag=val&tag1=val1`.
- Supports `search=<terms>` and `skip=<n>`.
- Multiple `?` segments use only the last search query, matching the HTTP comment in the file.

Core search behavior:
- Search terms are split on whitespace.
- Matching is ASCII case-insensitive.
- Longest term is promoted to a Boyer-Moore-like quick matcher.
- Remaining terms are checked exactly within the same newline-delimited record.
- Results are complete database lines/records.

9P behavior:
- Manual 9P server loop in `fsrun()` using `read9pmsg()`, `convM2S()`, and `convS2M()`.
- Fid table is hash-based with reference tracking.
- `Tflush` requests are ignored rather than answered directly.
- `fswrite()` replaces the fid’s active search and resets scan position.
- `fsread()` streams matches in chunks.

Dependencies and integration:
- Uses `<auth.h>` and `<fcall.h>`, but authentication is intentionally not required.
- Can mount at `/tmp` by default or publish a service file with `-s`.

Notable risks:
- Designed only for ASCII databases; case folding is custom ASCII-only.
- Entire database is loaded into memory.
- Manual 9P implementation has subtle fid/ref/open-state handling; `fswalk()` sets `f->open = 0` after `putfid()`, which is risky because `f` may have been released.
- `stats` is advertised writable/readable but returns empty content.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/searchfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/statusbar.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/statusbar.c

Progress/status bar utility. It reads progress pairs from stdin and displays either a graphical Plan 9 window bar or a text-mode bar.

Input format:
- Lines tokenize into two fields: current numerator and denominator.
- Percentage is `n * 100 / d`.

Modes:
- Default graphical window using draw/event.
- `-t` text mode.
- `-k` disables killing the parent on delete/control-C.
- `-w minx,miny,maxx,maxy` sets new window rectangle.

Core behavior:
- `newwin()` creates a new rio/window-system window by mounting `$wsys` on `/mnt/wsys`, rebinding `/dev`, and redirecting stdio.
- `drawbar()` updates only changed bar regions in graphics mode and uses backspaces/delta output in text mode.
- A child process watches keyboard/mouse events and sends an interrupt note to the parent on delete/control-C unless `-k`.

Dependencies and integration:
- Uses Plan 9 draw, bio, and event libraries.
- Includes local copies of helper logic that comments say should be in a library.

Notable risks:
- `ptext` is assigned with `r.min.x+4` as y coordinate, likely a typo, though it is not otherwise used.
- `postnote(PNCTL, child, "kill")` is called even when `child == -1` in text mode.
- Window setup is deeply Plan 9 namespace/window-system specific.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/statusbar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/stub.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/stub.c

Minimal 9P filesystem that inserts a single stub child into a mount point. It can expose one empty file or one empty directory.

Core behavior:
- `aux/stub [-Dd] path/name`.
- Splits `path/name` into mount point and child name.
- Mounts a 9P server `MBEFORE` at the parent path.
- Root directory lists exactly one entry.
- `-d` makes the child a directory.
- Non-root open is denied; root may be opened read-only.
- Writes always fail with `no writing`.

Important functions:
- `fsattach()`, `fswalk1()`, `fsstat()`, `fsread()`, `fsopen()`.
- `dirgen()` supplies the single directory entry for `dirread9p()`.

Dependencies and integration:
- Uses Plan 9 thread and `<9p.h>` server library.
- Closes standard descriptors before mounting to avoid confusing `mk`.

Notable risks:
- Child file has no read implementation beyond root directory listing; opening it is denied.
- `kidmode` defaults to 0 for file mode unless `-d`; that produces a file with no permission bits.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/stub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/timesync.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/timesync.c

Time synchronization daemon/client with optional NTP serving. It can synchronize local time from filesystem time, RTC, UTC file, GPS file, or NTP servers, and it can serve SNTP/NTP responses on specified networks.

Time sources:
- `Fs`: filesystem server time, default via `/srv/boot`.
- `Rtc`: `/dev/rtc`.
- `Utc`: external UTC file.
- `Gps`: GPS time file, default `/mnt/gps/time`.
- `Ntp`: one or more NTP servers, default `$ntp`.

Core loop:
- Initializes kernel clock interface and current frequency.
- Reads persisted frequency from a per-system file in `dir` default `/tmp`.
- Samples the selected source.
- If local time differs by more than 10 seconds, steps the clock.
- Otherwise slews a fraction of the delta and adjusts next sampling interval.
- Maintains samples up to one day to estimate clock frequency.
- Persists frequency periodically.

Kernel clock interfaces:
- `/dev/bintime` preferred.
- `/dev/nsec`, `/dev/fastclock`, and optionally `/dev/timing` fallback.
- Supports setting absolute time, frequency, and slewing delta.

NTP behavior:
- `ntptimediff()` sends SNTP client requests and computes offset and RTT.
- `ntpsample()` chooses the server with the best root dispersion/delay metric.
- `ntpserver()` answers client mode 3 requests with local stratum, root delay/dispersion, root ID, and timestamps.

Important functions:
- `adjustperiod()`, `caperror()`, `whatisthefrequencykenneth()` implement control-loop timing/frequency logic.
- `hnputts()`, `nhgetts()`, `hnputfp()`, `nhgetfp()` convert NTP timestamp/fixed-point fields.
- `sample()` samples second-resolution sources at a transition edge.
- `background()` daemonizes after the first loop unless debug mode is set.

Dependencies and integration:
- Uses Plan 9 IP, auth, arbitrary precision `mp`, clock devices, network dialing/announce, syslog, and process priority controls.
- Uses `/proc/<pid>/ctl` to set priority and wire to processor 2.

Notable risks:
- Time-setting code is high-impact and system-specific.
- NTP support is minimal SNTP-style and does not authenticate packets.
- Duplicate prototypes for `hnputts()` and `nhgetts()` appear in declarations.
- Some arithmetic mixes signed and unsigned wide values; behavior depends on Plan 9 compiler/runtime assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/timesync.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/trampoline.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/trampoline.c

Bidirectional connection relay. It connects stdin/stdout or an alternate dialed address to a target address, then copies data in both directions.

Options:
- `-9`: copy 9P messages atomically by reading the 4-byte length and forwarding complete messages.
- `-a addr`: use a dialed alternate address instead of stdin/stdout for one side.
- `-m netdir`: verify remote MAC address through ARP/NDB before relaying.

Core behavior:
- Dials target address.
- Forks into two copy loops, one per direction.
- Uses `postnote(PNGROUP, getpid(), ...)` to terminate the process group when one side exits.
- `iptomac()` scans `<net>/arp`.
- `macok()` checks NDB for `ether=<mac> trampok`.

Dependencies and integration:
- Uses Plan 9 network dialing, NDB, bio, and fcall length macros.
- Intended as a network service helper/gate.

Notable risks:
- MAC verification is local ARP/NDB based and only as trustworthy as local network state.
- The process-group termination note text is intentionally crude and operationally significant.
- `freeendpoints()` does not free `ep->net`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/trampoline.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/usage.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/usage.c

Generic usage-message generator driven by environment variables.

Core behavior:
- Reads `$0`, `$flagfmt`, and `$args`.
- Prints `usage: <argv0> ...` to stderr.
- Parses `flagfmt` where single-character comma-separated flags can be grouped as `[-abc]`, while flags with arguments are printed as `[-x arg]`.
- Appends `$args`.
- Exits with status `usage`.

Dependencies and integration:
- Standalone Plan 9 libc utility.
- Designed for shell scripts or command wrappers that set `flagfmt`/`args`.

Notable risks:
- Mutates the `flagfmt` string returned by `getenv()` while parsing.
- Assumes `$0` exists; exits separately if missing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/usage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/3dfx.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/3dfx.c

VGA controller backend for 3Dfx Banshee, Voodoo3/Avenger, and Voodoo5-class devices.

Core behavior:
- Locates PCI vendor `0x121A`.
- Determines maximum pixel clock by device ID.
- Uses PCI memory BAR 2 as I/O register base.
- Saves 3Dfx MMIO-style registers and VGA CRTC overflow registers.
- Determines video memory size from PCI BAR and DRAM/SGRAM strap registers.
- Supports linear framebuffer and high-clock double-pixel mode above 135 MHz.
- Programs PLL, screen size, stride, pixel format, DAC mode, and overflow registers.

Important functions:
- `snarf()` discovers PCI device and snapshots registers.
- `tdfxclock()` brute-forces PLL `m/n/p`.
- `init()` prepares mode registers and validates depth.
- `load()` writes CRTC and 3Dfx registers.
- `dump()` prints register state and decoded PLL frequencies.

Ctlrs:
- `tdfx`
- `tdfxhwgc` placeholder with no hooks.

Notable risks:
- Direct port I/O through BAR-derived base.
- Supports only selected device IDs.
- Requires x multiple of 16 for high-clock double-pixel mode.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/3dfx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/ark2000pv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/ark2000pv.c

VGA controller backend for ARK Logic ARK2000PV GUI accelerator.

Core behavior:
- Unlocks extended sequencer registers.
- Saves sequencer, CRT, and coprocessor status registers.
- Derives memory size from sequencer register bits.
- Supports linear framebuffer, pixel-clock 2x8 behavior, 1-bit and 8-bit modes.
- Handles overflow bits, interlace registers, memory configuration, aperture setup, FIFO/pitch control, and clock select bits.

Important functions:
- `snarf()` snapshots ARK-specific state.
- `options()` advertises `Hlinear|Hpclk2x8`.
- `init()` validates depth and computes extended register values.
- `load()` writes clock selection carefully and applies linear aperture settings.
- `dump()` prints ARK extended registers.

Ctlrs:
- `ark2000pv`
- `ark2000pvhwgc` placeholder.

Notable risks:
- Comments mention bugs for `1024x768x1` and hardware cursor in 1-bit modes.
- Contains a timing workaround for `w30c516` RAMDAC by toggling sequencer with sleep.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/ark2000pv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/att20c49x.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/att20c49x.c

RAMDAC backend for ATT20C490 and ATT20C491/492 true-color CMOS RAMDACs.

Core behavior:
- Parses optional speed grade suffix from controller name, defaulting to 55 MHz.
- Ensures requested pixel clock does not exceed part grade.
- Puts `att20c491`/`att20c492` into sleep briefly before writing mode.
- Writes control register 0 with base mode; 8-bit color control is present but disabled by `&& 0`.

Ctlrs:
- `att20c490`
- `att20c491`
- `att20c492`

Dependencies:
- Uses `attdaci()` and `attdaco()` accessors provided by `att21c498.c`.

Notable risks:
- The `if(vga->f == 0)` check appears to test the array pointer rather than `vga->f[0]`, likely a bug or old-compiler idiom mistake.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/att20c49x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/att21c498.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/att21c498.c

RAMDAC backend and indirect-register accessor for ATT21C498 16-bit-interface PrecisionDAC.

Core behavior:
- Implements `attdaci()`/`attdaco()` by reading Pixmask four times to enter indirect register sequence.
- Advertises `Hpclk2x8`.
- Parses speed-grade suffix, defaulting to 110 MHz.
- Chooses normal or 2x8-bit mode based on attached graphics controller capability and requested pixel clock.
- Resynchronizes initialization with `resyncinit()` if it halves the requested clock for 2x8-bit mode.
- Loads control register 0, including 2x8-bit mode bit when active.

Ctlr:
- `att21c498`

Notable risks:
- 8-bit color mode bit is disabled by `&& 0`.
- Global accessors are reused by other ATT DAC files, so sequencing assumptions matter.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/att21c498.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/bt485.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/bt485.c

RAMDAC backend for Brooktree Bt485 true-color RAMDAC, assuming S3 86C928-style wiring.

Core behavior:
- Provides `bt485i()`/`bt485o()` register access, including special indirect access for status/Cmd3/Cmd4 through S3 CRTC register `0x55`.
- Advertises S3-style enhanced/pixel-port/clock-doubler capabilities.
- Parses speed grade suffix, default 110 MHz.
- Uses clock doubler above 67.5 MHz.
- Programs sleep, clock source, clock doubler, 4:1 multiplexing, pixel port selection, enhanced mode, and wake-up.

Ctlr:
- `bt485`

Notable risks:
- Assumes Bt485 is wired to S3-style extended DAC select registers.
- Some 6/8-bit color selection is commented/disabled.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/bt485.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/ch9294.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/ch9294.c

Clock-selection backend for Chrontel CH9294 dual enhanced graphics clock generator.

Core behavior:
- Contains fixed 16-entry frequency tables for board/controller wiring patterns:
  - `e`/`E`: Tseng.
  - `g`/`G`: S3/IIT.
  - `k`/`K`: Avance Logic.
- Pattern is selected from controller name suffix after `-`.
- Chooses closest frequency index, optionally using clock divisors if the main controller supports `Hclkdiv`.
- Rejects matches with more than 5% frequency error.

Ctlr:
- `ch9294`

Notable risks:
- No hardware load hook; it only computes `vga->i[0]` and `vga->d[0]` for another controller to consume.
- Requires correctly suffixed controller name.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/ch9294.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/clgd542x.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/clgd542x.c

Controller backend for Cirrus Logic CL-GD542x/543x/5446/5480 and related chips.

Core behavior:
- Unlocks Cirrus extended registers.
- Saves sequencer, graphics, CRTC, chip ID, and hidden DAC register.
- Identifies chip family by CRTC ID and sets maximum clock.
- Determines memory size from chip-specific register layouts.
- Enables linear support for PCI/selected chips.
- Supports depths up to 8 bpp.
- Computes programmable VCLK using `clgd54xxclock()`.
- Programs Cirrus VCLK, packed-pixel mode, FIFO threshold, overflow bits, interlace, and linear graphics settings.

Shared behavior:
- `clgd54xxclock()` is exported and reused by `clgd546x.c`.

Ctlrs:
- `clgd542x`
- `clgd542xhwgc` placeholder.

Notable risks:
- Comments say 543x added capabilities are not used.
- Linear aperture handling is broad and uses a 16 MB apparent size when requested.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/clgd542x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/clgd546x.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/clgd546x.c

Controller backend for Cirrus Logic Laguna CL-GD546x visual media accelerators.

Core behavior:
- Locates PCI vendor `0x1013`, device `0xD0`, `0xD4`, or `0xD6`.
- Sets kernel VGA type to `clgd546x`.
- Attaches `clgd546xmmio` segment for MMIO register access.
- Saves standard extended VGA registers and Laguna MMIO registers.
- Uses PCI BAR 0 size for video memory and advertises linear framebuffer.
- Reuses `clgd54xxclock()` for VCLK.
- Programs format, display threshold, tiling control, vendor-specific control, 2D control, and tiling control for 2D/3D.

Ctlrs:
- `clgd546x`
- `clgd546xhwgc` placeholder.

Notable risks:
- Although format logic has cases for 16/24/32, the file rejects `mode->z > 8`, so high-depth code is unreachable.
- Tiling/interleave controls are simplified with `nointerleave` and `notile` forced on.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/clgd546x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/ct65540.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/ct65540.c

Controller backend for Chips & Technologies CT65540/CT65545.

Core behavior:
- Uses indexed extension ports `0x3D6/0x3D7`.
- Groups extension registers by functional category for snapshot/dump.
- Advertises linear framebuffer.
- Computes PLL settings by brute force for requested clock up to 220 MHz.
- Supports 8-bit packed mode with optional linear addressing and planar lower-depth mode.
- Programs extended overflow bits, clock registers, mapping mode, flat-panel/misc registers, and VGA sequential access bits.

Ctlrs:
- `ct65540`
- `ct65545`
- `ct65545hwgc` placeholder.

Notable risks:
- Supports only up to 8 bpp.
- Assumes 1 MB framebuffer in 8-bit mode.
- `flags` register group is declared but not included in `group[]`, so those registers are not dumped/saved via the grouped loop.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/ct65540.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/cyber938x.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/cyber938x.c

Controller backend for Trident Cyber938x and related Cyber/ProVidia/CyberBlade chips.

Core behavior:
- Handles old/new sequencer register modes.
- Accesses DAC Pixel Command Register via four Pixmask reads.
- Saves sequencer, CRTC, graphics, old registers, and PCR.
- Determines memory size from CRTC register `0x1F`.
- Determines LCD panel size from graphics register `0x52`.
- Supports linear framebuffer.
- Programs depth-specific PCR and pixel-bus register values for 8/16/24 bpp.
- Applies revision-specific register tweaks for ProVidia 9685, Cyber9320/9382/9385/9388, Cyber9525/DVD, and CyberBlade variants.

Ctlrs:
- `cyber938x`
- `cyber938xhwgc` placeholder.

Notable risks:
- Comments state ProVidia 9685 support is incomplete, with no clock code and only 640x480x8 working.
- Revision-specific magic values are hardware-fragile.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/cyber938x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/data.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/data.c

Global controller registry for the Plan 9 VGA utility.

Core behavior:
- Defines global flags:
  - `cflag`: do not use hardware graphics cursor.
  - `dflag`: do palette handling.
- Defines `ctlrs[]`, the ordered list of all available `Ctlr` backends: controllers, RAMDACs, clocks, hardware cursors, software cursor, VESA, VMware, Radeon, Nvidia, Matrox, and the files in this group.
- Defines `dacxreg[4]`, mapping low two bits of indirect DAC register addressing to VGA DAC ports.

Dependencies and integration:
- `db.c` uses `ctlrs[]` to instantiate configured controller chains from `vgadb`.
- Many controller modules export `Ctlr` globals consumed here.

Notable risks:
- Registry requires every referenced `Ctlr` symbol to be linked in the build.
- Controller matching in `db.c` depends on names matching this table.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/data.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/db.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/db.c

NDB-backed VGA configuration database reader. It resolves controller chains and display modes from Plan 9 `vgadb`-style databases.

Core behavior:
- Opens an NDB database and errors on failure.
- Matches controllers by BIOS string offsets/ranges or PCI vendor/device IDs.
- BIOS match wins over PCI match.
- Saves attributes into `Vga`: controller, RAMDAC, clock, hardware cursor, linear address, memory bandwidth, and arbitrary attributes.
- Adds linked copies of `Ctlr` definitions from global `ctlrs[]`, preserving suffixes such as speed grades.
- Parses monitor/mode entries, including aliases and `include` chains.
- Allows mode string clock override in `XxYxZ@NMHz`.
- Provides `dbdumpmode()` debug output.

Important functions:
- `dbctlr()` resolves hardware/controller config.
- `dbmode()` resolves monitor mode timing.
- `dbmonitor()` fills `Mode` fields.
- `dbbios()` and `dbpci()` implement hardware matching.

Dependencies and integration:
- Uses `<ndb.h>`, PCI probing, BIOS reads from `io.c`, and `Ctlr` registry from `data.c`.

Notable risks:
- Include depth guard is fixed at 5.
- Numeric parsing is permissive.
- BIOS matching scans offsets and may read substantial BIOS ranges through `readbios()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/db.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/error.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/error.c

Fatal error and trace support for the VGA utility.

Core behavior:
- `error()` turns the sequencer back on, formats `argv0: message`, optionally echoes message body to stdout when verbose, flushes stdout, writes to stderr, and exits with status `error`.
- `trace()` writes diagnostic text to stdout when `vflag` or `Vflag` is set and additionally to standard print output when `Vflag` is set.
- Maintains global verbosity flags `vflag` and `Vflag`.

Dependencies and integration:
- Used by almost every VGA helper.
- Calls `sequencer(0, 1)` before fatal exit to avoid leaving display sequencer disabled.

Notable risks:
- Fatal path assumes display recovery through `sequencer()` is always safe enough to attempt.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/error.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/et4000.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/et4000.c

Controller backend for Tseng Labs ET4000 and ET4000-W32 variants.

Core behavior:
- Unlocks Tseng registers through magic key writes.
- Saves extended sequencer, CRTC, and attribute registers.
- Determines memory size from Tseng CRTC registers, including W32 doubling.
- Advertises clock-divisor support and W32 2x8 pixel-clock support.
- Converts lowercase vertical interlace marker `v` to `V` because ET4000 does not need vertical timing halved.
- Supports depths up to 8 bpp.
- Programs overflow registers, MMU/linear disable bits, clock selection, clock divisor, and attribute mode.

Dump behavior:
- Prints extended registers.
- For W32, also dumps sprite and IMA registers through secondary CRTC port.
- If not initialized, decodes timing values from raw registers.

Ctlr:
- `et4000`

Notable risks:
- Pixel clock capped at 86 MHz.
- Disables linear map/MMU buffers in init.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/et4000.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/et4000hwgc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/et4000hwgc.c

Hardware graphics cursor eligibility shim for ET4000-W32.

Core behavior:
- `init()` marks itself initialized.
- Sets global `cflag` to disable hardware cursor unless:
  - main controller name starts with `et4000-w32`,
  - depth is 8 bpp,
  - 2x8-bit pixel-clock mode is not active,
  - `cflag` was not already set.

Ctlr:
- `et4000hwgc`

Notable risks:
- Does not implement cursor load/render itself; only controls eligibility for shared cursor logic elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/et4000hwgc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/hiqvideo.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/hiqvideo.c

Controller backend for Chips & Technologies HiQVideo/HiQV32 chips, including 69000 and 65550/65554/65555.

Core behavior:
- Locates PCI vendor `0x102C` and supported device IDs.
- Saves flat-panel extension registers, multimedia registers, extended CRTC registers, and configuration extension registers.
- Determines max dot clock from chip and voltage state.
- Determines framebuffer memory size from chip-specific registers.
- Advertises linear framebuffer.
- Computes programmable DCLK PLL within documented constraints.
- Avoids programming DCLK when output is LCD according to flat-panel register state.
- Supports 8/16/32 bpp.
- Programs extended CRTC overflow, pixel format, linear aperture, and DCLK registers.

Ctlrs:
- `hiqvideo`
- `hiqvideohwgc` placeholder.

Notable risks:
- Header comment says depths other than 8 are too slow.
- 69000 extensions over 65550 are not fully considered.
- PLL code uses floating-point search and assumes stable register constraints.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/hiqvideo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/i81x.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/i81x.c

Controller backend for Intel 81x/815/830M integrated graphics.

Core behavior:
- Locates supported Intel PCI device IDs.
- Sets kernel VGA type to `i81x`.
- Attaches `i81xmmio` for graphics-control MMIO registers.
- Uses PCI aperture memory size for framebuffer and aperture.
- Saves standard VGA registers, clock control registers, i830 CRTC LCD registers, and pixel pipeline control.
- Advertises linear framebuffer.
- Computes DCLK settings for selected horizontal resolutions using `i81xdclk()`.
- Programs pixel pipeline depth, cursor enable, palette behavior, linear mapping, framebuffer start address, CRTC timings, and MMIO clock/LCD/pixel-pipeline registers.

Supported resolutions:
- Special cases for 640 and 720.
- Computes DCLK for 800, 1024, 1152, 1280, and 1376.
- Errors for other high resolutions.

Ctlrs:
- `i81x`
- `i81xhwgc` placeholder.

Notable risks:
- Contains many comments noting uncertain/empirical register values.
- Expression `vga->pci->mem[0].bar >>2 + 1` depends on C precedence and likely does not mean `(bar >> 2) + 1`.
- Uses `mode->deffrequency` for DCLK; errors if it resolves to zero.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/i81x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/ibm8514.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/ibm8514.c

IBM 8514/A graphics coprocessor setup helper.

Core behavior:
- Defines 8514/A I/O port constants.
- `load()` resets/enables subsystem state, sets foreground/background mix modes, scissors rectangle based on framebuffer size and mode width, write mask, and pixel control.
- `dump()` prints advanced function control and subsystem status.

Ctlr:
- `ibm8514`

Dependencies and integration:
- Has only load/dump hooks; no snarf/options/init.
- Intended as an auxiliary accelerator setup step paired with VGA mode programming elsewhere.

Notable risks:
- Scissors bottom uses `vga->vmz / vga->mode->x - 1`, assuming one byte per pixel and linear layout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/ibm8514.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/icd2061a.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/icd2061a.c

Clock-parameter calculator for IC Designs ICD2061A dual programmable graphics clock generator.

Core behavior:
- Supports only depths up to 8 bpp.
- Raises requested frequency by powers of two until VCO is above 50 MHz.
- Selects VCO range index from static threshold table.
- Searches denominator and numerator satisfying reference-frequency constraints.
- Stores computed `d`, `n`, `p`, and `i` fields in `Vga`.
- Computes final clock based on prescale and selected divisors.
- Does not directly load hardware; another component must use the calculated serial word.

Ctlr:
- `icd2061a`

Notable risks:
- Mutates `vga->f[0]` upward during VCO selection and later stores VCO-like result, so consumers must interpret `p` correctly.
- No load/dump hook in this file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/icd2061a.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/ics2494.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/ics2494.c

Clock-selection backend for ICS2494/ICS2494A dual video/memory clock generator.

Core behavior:
- Contains fixed 16-entry frequency patterns for suffixes:
  - `237` / `304`
  - `324`
- Selects pattern from controller name suffix after `-`.
- Chooses frequency index and optional divisor when the main controller supports `Hclkdiv`.
- Accepts matches within 1 MHz and stores `vga->i[0]` and `vga->d[0]`.

Ctlrs:
- `ics2494`
- `ics2494a`

Notable risks:
- No hardware load hook; selected index/divisor must be consumed by a graphics controller.
- Requires correctly suffixed configuration name.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/ics2494.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/ics534x.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/ics534x.c

ICS534x GENDAC backend, assumed wired to ET4000-W32p or ARK2000PV boards.

Core behavior:
- Uses controller-specific RS2 routing:
  - ET4000-W32 via CRTC `0x31`.
  - ARK2000PV via sequencer `0x1C`.
- Advertises `Hpclk2x8`.
- Parses speed grade suffix, default 80 MHz.
- Optionally halves requested clock and enables 2x8-bit mode when supported and beneficial.
- Computes PLL parameters `M/N/R` under documented constraints.
- Programs PLL entry `f7`, PLL control register, and pixel mode through DAC registers.
- Dumps all PLL frequency entries and command/control registers.

Ctlr:
- `ics534x`

Notable risks:
- Errors if used with an unsupported main controller.
- Assumes ICS534x clock select and RS2 wiring match one of the two coded board families.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/ics534x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/io.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/io.c

Low-level I/O, BIOS, vgactl, allocation, and dump formatting support for the VGA utility.

Core behavior:
- Provides `inportb/w/l()` and `outportb/w/l()` using Plan 9 `#P/iob`, `#P/iow`, and `#P/iol`.
- Reads and writes `#v/vgactl` attributes through cached parsing.
- Provides palette programming.
- Reads VGA BIOS from `#v/vgabios`, falling back to process memory.
- Caches BIOS reads in a static 64 KB buffer.
- Dumps BIOS as hex/ASCII if it finds a BIOS signature at `0xC0000` or `0xE0000`.
- Provides `alloc()`, `printitem()`, `printreg()`, and `printflag()` helpers.

Dependencies and integration:
- Used by almost every VGA controller backend.
- Depends on Plan 9 VGA and port-I/O devices.

Notable risks:
- `vgactlinit()` stores pointers into a mutable static buffer; cache invalidation is manual.
- BIOS fallback to `#p/<pid>/mem` is highly Plan 9 specific.
- `printflag()` has a fixed table for known flag bits and prints unknown bits numerically.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/mach32.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/mach32.c

Controller backend for ATI Mach32.

Core behavior:
- Uses ATI extended indexed registers at assumed default port `0x1CE`.
- Unlocks multiple ATI extended register lock bits.
- Saves extended ATI registers and Mach32 I/O registers.
- Determines memory size from `Misc`.
- Uses a conservative fixed clock table intended to work across unknown clock generator variants.
- Supports 8-bit packed mode setup and legacy aperture access.
- Disables linear aperture/memory boundary in `load()` to keep VGA aperture access usable.
- Programs clock index bits and interlace flag.

Ctlr:
- `mach32`

Notable risks:
- Header states no accelerator support and practical modes only up to 1024x768.
- Clock generator cannot be detected; only a small safe clock subset is available.
- `vga->private = alloc(sizeof(mach32))` allocates pointer-size rather than `sizeof(Mach32)`, which appears to be a real bug.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/mach32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/mach64.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/mach64.c

Controller backend for ATI Mach64, modeled after the Mach32 backend.

Core behavior:
- Sets ATI extended register I/O address via graphics registers before using port `0x1CE`.
- Unlocks ATI extended register locks.
- Saves ATI extended registers plus Mach64 config/status/memory/scratch registers.
- Determines memory size from `Memcntl`.
- Assumes ATI18818 clock table and searches for a fixed clock within 1 MHz, including divide-by-two option.
- Programs 8-bit packed VGA-style mode, clock index bits, and interlace flag.
- Sets `ctlr->type = mach32.name`, making Mach64 reuse Mach32-style downstream behavior.
- Forces `vga->vmz` to 1 MB because Mach64 can only address 1 MB in VGA mode.

Ctlr:
- `mach64`

Notable risks:
- Header says no accelerator support and only up to 1024x768.
- Clock chip detection is not implemented; ATI18818 is assumed.
- Load path comments admit it does not fully ensure aperture/memory boundary/VGA-controller state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/vga/mach64.c -->