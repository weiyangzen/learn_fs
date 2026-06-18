# Group Research: group_163_9front_sources_os_plan9_9front_sys_src_cmd_mothra_mothra_c_sources_o_3d656058129b

Scope: `Docs/research_subset_a.md` / source tree `sources/os/plan9/9front`.  
Read status: every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/mothra.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/mothra.c

Implements the main Mothra graphical web browser process. It owns the Plan 9 draw/event/panel UI, page history, command entry, plumbing integration, URL loading workflow, and lifecycle for rendered text/images.

Key responsibilities:
- Defines global UI panels for command entry, message/status label, page list, current URL label, main/alternate text views, and button-3 menu.
- Sets up cursors, fonts, bitmap decorations, event channels, plumb receiver `"web"`, and a process cohort used to kill helper processes on exit.
- Maintains a circular `Www` page log via `www()`/`nwww()` and switches current document with `setcurrent`.
- Handles keyboard scrolling, search, horizontal scroll, mouse wheel-like buttons, panel dispatch, and plumbed URLs in the main event loop.
- Implements command entry behavior: open URL, DuckDuckGo search, reload/go selected URL, jump to history, moth mode, image killing, screenshot dump, save selected hit, and quit.
- Loads URLs through `geturl`: resolves/fetches with `urlget`, determines type from MIME or snooping, pipes HTML through `uhtml`, spawns parsers for HTML/plain text, launches `page -w` for images/documents, and saves unknown types when not plumbed.
- Manages rendered document updates, asynchronous reader completion through `kickpipe`, page image memory pressure via `NPIXMB`, and old-page cleanup.
- Supports “moth mode,” adding/removing hot image-link affordances and allowing image URLs to be selected directly.
- Provides utility functions for status messages, save filters, file descriptor cleanup, shell pipelines, selection URLs, text/image cleanup, hit list writing, snarf/paste, and confirmation.

Important interactions:
- Calls `plrdhtml`/`plrdplain` from `rdhtml.c`, `urlget`/`urlresolve` from `url.c`, MIME snooping from `snoop.c`, image helpers, form helpers, and panel/rtext APIs.
- Relies on `/mnt/web` through URL helpers for HTTP-like fetching, `/dev/label` for window labels, plumbing for external send/receive, and shell tools such as `uhtml`, `page`, `tput`, and `aux/statusmsg`.

Notable quirks:
- Many operations fork helper processes and share state with `RFMEM`; correctness depends on simple flags such as `changed`, `finished`, and `alldone`.
- `geturl` waits before reusing a history slot if a reader is still active.
- Mothra is deliberately permissive and tool-driven rather than a standalone modern browser.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/mothra.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/mothra.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/mothra.h

Shared Mothra declarations and constants.

Defines:
- Browser limits: page history size, parallel image loader count, image memory budget, name/line/auth/title/label lengths, and redirect limit.
- Core structures:
  - `Action`: link/image/form/name metadata attached to rendered `Rtext`.
  - `Url`: relative/base/full URL state, fragment tag, content type, and image-map flag.
  - `Www`: one cached page, including URL, image/form storage, title, rendered text, scroll offset, and async status flags.
  - `Field`: forward declaration for form support.
- File/content type enum values for plain text, HTML, common image formats, icons, and page-rendered document types.
- Authentication and HTTP method constants.
- Shared globals for drawing assets, character width, current text panel, debug flag, and mouse state.
- Function prototypes across Mothra modules: parsing/rendering, URL resolution/fetch/post, image handling, form cleanup, MIME detection, panel creation, message reporting, and formatting.

This header is the local contract between Mothra’s UI, HTML reader, URL backend, MIME snooper, image loader, and form code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/mothra.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/rdhtml.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/rdhtml.c

Implements Mothra’s plain-text and HTML reader/rendering pipeline. It tokenizes input, maintains a small formatting stack, extracts titles/anchors/links/images/forms, and emits `Rtext` nodes for display by the panel text view.

Key responsibilities:
- Loads and caches four font families/sizes through `pl_whichfont` and `getfonts`.
- Maintains HTML parse state with stack push/pop helpers that duplicate/free inherited link, image, and anchor state.
- Reads input through buffered routines that normalize line endings, decode UTF-8 runes, and provide putback.
- Tokenizes permissive HTML: start/end tags, comments, script/style content, preformatted text, entity references, attributes, and normal text.
- Parses attributes case-insensitively and supports quoted/unquoted values, entity removal, and limited error reporting through `htmlerror`.
- Emits text with font, indentation, line break, paragraph, vertical offset, hot-link, strike-through, and attached `Action` metadata.
- Handles plain text by preserving line breaks, tabs, and fixed-width font rendering.
- Implements broad tag behavior for headings, lists, blockquotes, links, anchors, images, base URL, meta refresh, media/frame fallback links, tables, preformatted regions, title, inline styles, forms, and script/style suppression.
- Auto-linkifies obvious `http://`, `https://`, `gemini://`, `ftp://`, and some `www.` tokens.
- Starts image retrieval with `getpix` after EOF unless image loading is disabled.

Important interactions:
- Uses `html.h` tag/action metadata and `rtext.h` output primitives.
- Delegates form tags to `rdform`, `endform`, and field panel creation elsewhere.
- Calls `urlresolve` for `<base href=...>` and stores output in the current page’s `Www`.
- Sets `dst->changed` as output grows and calls `finish(dst)` when parsing is complete.

Notable quirks:
- Parsing is intentionally tolerant and incomplete; many tags are simplified or reported as unimplemented/deprecated.
- Script/style bodies are skipped as display text, not executed.
- Some modern media tags are represented as bracketed links rather than rendered media.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/rdhtml.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/snoop.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/snoop.c

MIME/type detection helper for Mothra.

Behavior:
- `filetype` reads an initial block from a file descriptor, runs `/bin/file -m` in a helper process, captures its MIME-style output, and arranges for the original descriptor stream to remain readable by forwarding the buffered prefix plus the remaining data.
- `mimetotype` maps content types to Mothra’s internal type enum, including plain text, HTML, JPEG/GIF/PNG/BMP/ICO, document/page-renderable types, generic images, generic text, and RFC822 messages.
- `snooptype` combines both steps: invoke file sniffing and convert the result to an internal type.

Important interactions:
- Used by `mothra.c` when server-provided content type is missing or not understood.
- Depends on Plan 9 process/file descriptor operations and `/bin/file`.

Notable quirks:
- The MIME map is prefix-based and intentionally small.
- Unknown types return `-1`, causing caller policy to decide whether to save, plumb, or report.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/snoop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/url.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/url.c

Implements Mothra URL fetching, posting, and resolving.

Key responsibilities:
- Supports `data:` URLs locally, decoding percent-encoded data or base64 payloads into an ORCLOSE temporary file.
- Supports `file:` URLs locally, resolving relative paths against a `file:` base, preserving fragment tags, cleaning paths, and opening the local file.
- Uses a web file service mounted at `mtpt` (`/mnt/web` by default) for network-style URLs.
- `webclone` opens `/mnt/web/clone`, writes `baseurl` and `url` controls, and returns the connection path.
- `urlpost` opens a connection, optionally sets content type, and returns a writable `postbody`.
- `urlget` fetches local/data URLs first, otherwise uses `/mnt/web/<conn>/body` or `errorbody`, reads parsed URL/fragment/content type/content encoding, and pipes compressed bodies through `uncompress`, `gunzip`, or `bunzip2`.
- `urlresolve` asks `/mnt/web` for parsed absolute URL and fragment without reading the body.

Important interactions:
- Used by Mothra UI/link code and the form/posting path.
- Relies on `pipeline` from `mothra.c` for content decoding filters.
- Shares the mutable `Url` structure fields declared in `mothra.h`.

Notable quirks:
- The network implementation is delegated entirely to the mounted web file system.
- `fileget` temporarily edits strings while resolving path components and then restores them.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/url.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mount.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mount.c

Plan 9 `mount` command implementation.

Behavior:
- Parses mount options: after/before/create/cache flags, key pattern, no-auth, become-none/no-auth, and quiet mode.
- Opens the supplied service endpoint read-write.
- Optionally switches process user to `none`.
- Authenticated path calls `fauth` and `auth_proxy` with `proto=p9any role=client`, then mounts with the returned auth fd.
- No-auth path mounts directly with auth fd `-1`.
- Reports errors unless quiet mode is enabled.

Important interactions:
- Uses Plan 9 auth library (`auth_proxy`, `amount_getkey`) and the kernel `mount` call.
- Supports optional attach spec (`aname`) as the third positional argument.

Notable quirks:
- If `fauth` succeeds but `auth_proxy` fails, it logs the auth failure but still attempts the mount with the auth fd.
- `-N` implies `-n` and tries to mount as user `none`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mpc.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mpc.y

Yacc grammar and code generator for a small multiprecision arithmetic language. It parses functions and emits C functions using Plan 9’s `mp` library.

Language features:
- Function definitions with argument lists and statements.
- Expressions over names, numeric constants, calls, comma lists, unary minus, arithmetic, shifts, exponentiation, assignments, ternary expressions, and boolean comparisons.
- Statements for assignment, expression/call, `mod` scoped modular arithmetic, `if`/`else if`/`else`, `while`, `break`, and blocks.
- Lexer supports comments beginning with `#`, identifiers, numbers, keywords, operators, and shifts/equality tokens.

Code generation:
- Builds `Node` ASTs and interned `Sym` records with flags for set/use/argument/local status.
- Performs constant folding with multiprecision arithmetic where safe, including modular folding when the active modulus is constant.
- Emits `mpint *` temporaries with reuse/free tracking.
- Emits optimized cases for constants `mpzero`, `mpone`, `mptwo`, shifts, doubling, modular add/sub/mul, modular inverse/division, exponentiation, and branchless conditional selection with `mpsel` for expression conditionals.
- Tracks assigned locals, initializes them with `mpnew(0)`, and frees locals/temporaries on exit or break.
- Reports diagnostics with source filename and AST context using custom `%N` and `%B` formatters.

Important interactions:
- Uses Plan 9 `libmp` primitives such as `mpadd`, `mpsub`, `mpmul`, `mpdiv`, `mpmod`, `mpexp`, `mpinvert`, `mpmodadd`, `mpmodsub`, and `mpmodmul`.
- Reads stdin or files with `Biobuf`, repeatedly invoking `yyparse` until EOF.

Notable quirks:
- The compiler enforces “name used but not set.”
- Some operations fall through intentionally for folding/generation paths.
- Modular division is implemented by modular inverse followed by multiply.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mpc.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ms2html.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ms2html.c

Converts troff/ms-style input to HTML. It includes a compact macro processor, escape translator, conditional evaluator, include stack, and HTML emitter.

Key responsibilities:
- Defines supported ms/troff directives and dispatch tables for macros, pseudo-ops, conditionals, strings, and raw HTML helpers.
- Maintains global rendering state for title, basename, equation delimiter, indentation, lists, examples, headings, author blocks, anchors, conditionals, and font stack.
- Provides large entity and troff-special-character translation tables for HTML output.
- Implements string registers, number registers, macro definitions/appending/removal, macro argument substitution, and nesting stacks for strings/macros/includes.
- Reads logical runes from stdin, included files, macro bodies, or string expansions, with escape expansion in `getnext`.
- Handles troff escapes for strings, macro args, special chars, font changes, number registers, size changes, vertical movement, horizontal rules, comments, line continuation, superscript/subscript, and HTML escaping.
- Parses directives and arguments, including quoted/null arguments.
- Emits an HTML document with title/body setup and closing cleanup.
- Implements common ms macros: paragraphs, lists, indents, headings, numbered headings, title, authors, font macros, displays/preformatted blocks, abstracts, footnotes, quotes, references, raw HTML/title injection, and Bell Labs address macros.
- Handles `.EQ`, `.TS`, and `.PS` blocks by piping content through `troff2gif` and embedding generated GIFs.
- Handles `.BP` picture conversion through `ps2gif` unless the input already looks like JPEG/GIF.
- Implements `.if`, `.ie`, `.el`, arithmetic/condition evaluation, braced body push/skip, `.ds`, `.as`, `.ig`, `.so`, `.lf`, and Web reference helpers.

Important interactions:
- Uses Plan 9 `Biobuf`, process/fork calls, `troff2gif`, `ps2gif`, and image file side effects for generated auxiliary GIFs.
- The `-b`, `-d`, `-q`, and `-t` options control auxiliary image basename, equation delimiters, quiet logging, and title.

Notable quirks:
- The generated HTML is old-style and intentionally simple.
- Many ms/troff macros are ignored or approximated.
- Include and macro/string nesting are bounded by fixed constants.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ms2html.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mtime.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mtime.c

Small utility that prints modification times for files.

Behavior:
- Usage: `mtime file...`.
- Rejects all options.
- For each argument, calls `dirstat`.
- Prints the file mtime as an unsigned decimal field plus the path.
- Reports stat errors to stderr and exits with `"errors"` if any file failed.

This is a straightforward Plan 9 metadata inspection command.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mtime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mug.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mug.c

Interactive Plan 9 image tool for making 48x48 grayscale “mug”/face icons.

Key responsibilities:
- Reads an input image from a file or stdin, converts it to `GREY8`, and displays the original beside a gamma/black-white ramp and 48x48 previews.
- Maintains editing `State`: black point, white point, stretch, gamma, output depth, gamma table, and selected square crop rectangle.
- Downsamples the selected square to 48x48 using separable smoothing, value remapping, gamma correction, and optional error-diffusion dithering for low bit depths.
- Supports depths 8/4/2/1 through the button-3 menu.
- Provides undo by keeping prior state/image, reset, write-to-stdout, and exit.
- Lets the user drag/resize the crop rectangle using region-specific cursors.
- Lets the user drag the current face or saved face slots between the active preview and eight storage slots.
- Writes GREY1/GREY2 output as numeric initializer-style rows and GREY4/GREY8 output as a Plan 9 image.

Important interactions:
- Uses Plan 9 draw/event/cursor APIs heavily.
- Uses `readimage`, `writeimage`, `loadimage`, `unloadimage`, `allocimage`, and `rgb2cmap`.

Notable quirks:
- The code defines its own `min`, `max`, and `abs`.
- UI behavior is mouse-centric; keyboard events are ignored.
- Some comments acknowledge visual flashiness and heuristic control behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mv.c

Plan 9 `mv` implementation.

Behavior:
- Supports `mv fromfile tofile` and `mv fromfile ... todir`.
- Cleans input pathnames before processing.
- Determines destination directory/element based on whether the final argument is an existing directory and whether the source is a directory.
- For same-directory moves, removes an existing target, then attempts `dirwstat` to rename the source.
- If rename cannot work and the source is not a directory, copies file contents to the target, preserves mode and mtime via `dirfwstat`, and removes the source.
- Refuses to copy directories across directories/devices.
- Handles append-only targets by hard-removing before create, since create would not truncate them.
- Uses `samefile` to reject no-op moves by comparing qid/dev/type metadata.
- `hardremove` repeatedly removes a target and exits on first failure.

Important interactions:
- Uses Plan 9 directory metadata, `dirwstat`, `create`, `remove`, `dirstat`, and `IOUNIT`.

Notable quirks:
- Removing an existing target happens before attempting same-directory rename.
- Cross-directory directory moves are refused rather than recursively copied.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/convDNS2M.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/convDNS2M.c

Packs internal DNS message/resource-record structures into DNS wire-format packets.

Key responsibilities:
- Maintains a small name-compression dictionary for packed domain names.
- Provides primitive packers for counted strings, symbols, raw bytes, unsigned integer fields, IPv4 addresses, IPv6 addresses, and compressed/uncompressed domain names.
- Enforces DNS label/domain/string size limits and output buffer bounds by returning beyond `ep` on overflow.
- `convRR2M` serializes resource records including HINFO, CNAME/MB/MD/MF/NS, MG/MR/MINFO, MX, A, AAAA, PTR, SOA, SRV, TXT, NULL, RP, DNSKEY/KEY, SIG, CERT, CAA, OPT, and unknown RDATA.
- Handles OPT records specially by writing UDP payload size and extended flags in the class/TTL fields.
- Computes RR TTL from db/expire/ttl state and clamps negative TTLs to zero.
- Serializes questions through `convQ2M`.
- `rrloop` packs sections and returns actual counts for questions, answers, authority, and additional records.
- `convDNS2M` writes section data first, accounts for optional EDNS record insertion, sets `Ftrunc` when output fills, then writes the DNS header with actual counts.

Important interactions:
- Depends on `dns.h` RR/DNSmsg layout and helper state such as `now`, `rrsupported`, and `dnslog`.
- Uses Plan 9 IP helpers `parseip` and `v6tov4`.

Notable quirks:
- The dictionary is limited to 64 entries but enough for normal DNS compression.
- SRV target names are intentionally packed without compression per RFC2782.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/convDNS2M.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/convM2DNS.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/convM2DNS.c

Parses DNS wire-format packets into internal `DNSmsg` and `RR` structures.

Key responsibilities:
- Uses a `Scan` cursor to track packet bounds, current position, parsing errors, outgoing response code, stop/truncation flags, and formatted diagnostics.
- Provides safe readers for bytes, shorts, longs, IPv4/IPv6 addresses, DNS strings, raw byte sequences, and compressed domain names.
- Implements DNS name decompression with pointer-loop limits and EDNS/reserved-label detection.
- Converts wire RRs to internal records for HINFO, CNAME/MB/MD/MF/NS, MG/MR/MINFO, MX, A, AAAA, PTR, SOA, SRV, TXT, NULL, RP, DNSKEY/KEY, SIG, CERT, CAA, OPT, and unknown RDATA.
- Converts questions separately with owner/type/class.
- Includes a Windows 2000 type-field byte-order workaround that can set format-error response feedback.
- Handles bad lengths defensively, including special tolerance for malformed hints and a known malformed CNAME reverse-lookup pattern.
- Builds section lists for questions, answers, nameservers, and additional records.
- Returns a duplicated error string for answer/nameserver parse errors while still attempting to parse additional records.

Important interactions:
- Allocates DNS structures through `rralloc`, `dnlookup`, `emalloc`, and related helpers from the DNS subsystem.
- `codep` receives a response code such as `Rformat` when parsing should abort with an immediate reply.

Notable quirks:
- If input appears truncated without the truncation flag, it may set `Ftrunc` heuristically.
- EDNS extended labels set a stop flag and are treated like a graceful parser stop.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/convM2DNS.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/cs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/cs.c

Implements the Plan 9 connection server `ndb/cs`, a small 9P service that translates dial strings into clone paths and addresses.

Key responsibilities:
- Serves a 9P tree containing directory `.` and file `cs`, mounted under the selected net mount point and also exposed through `/srv/cs...`.
- Tracks per-fid `Mfile` state: user, qid, current request fields (`net`, `host`, `serv`, `rem`), next network to try, and cached reply strings.
- Handles 9P requests: version, auth rejection, flush, attach, walk, open, read, write, clunk, stat, and permission-denied create/remove/wstat.
- Parses writes to `cs` as either owner-only control commands (`debug`, `ipv4`, `ipv6`, `add`, `refresh`), general `!` ndb queries, or dial strings split on `!`.
- On reads, lazily returns one reply segment at a time and performs more lookups as offsets advance.
- Builds a default network list by checking available `/net/<proto>/clone` files, and supports manual network additions.
- Tracks local IP interfaces, configured IPv4/IPv6 availability, DNS-usable addresses, and system name discovery.
- Resolves IP services through ndb `port` records and marks restricted TCP ports.
- Resolves hosts via DNS first for domains, then ndb, with fallback from non-domain attributes to domain names.
- Reorders IP results to prefer addresses on local interface networks.
- Translates IP results into dialable strings like `/net/tcp/clone ip!port`.
- Translates telco records similarly for the `telco` network.
- Spawns bounded slave processes around DNS lookups so slow DNS requests do not block the main 9P server.
- Mounts `/srv/dns...` into the net mount point on demand.
- Implements general tuple queries and `ipinfo` queries, including optional resolution of `@attr` values.

Important interactions:
- Uses libndb, DNS query helpers, Plan 9 network interface inspection, 9P fcall conversion, `/srv`, `/net`, `/net/ndb`, and `/dev/sysname`.
- Shares DNS and database behavior with other `ndb` files such as `dblookup.c`.

Notable quirks:
- Global database access is serialized by `dblock`.
- Active DNS slave count is capped at `Maxactive`.
- Unknown network names are passed through without host/service translation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/cs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/csquery.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/csquery.c

Small client for querying `/net/cs`.

Behavior:
- Usage: `ndb/csquery [/net/cs [addr...]]`.
- Optional `-s` status-only mode suppresses normal output and only records errors.
- Opens the selected connection server file, writes the query string, then seeks back and reads all translated replies.
- With address arguments, queries each argument and exits with error status if any translation failed.
- With no query arguments, enters an interactive loop reading lines from stdin after printing `> ` prompts.

Important interactions:
- Talks directly to the 9P `cs` file implemented by `ndb/cs`.
- Uses simple read/write protocol rather than linking to resolver internals.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/csquery.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dblookup.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dblookup.c

Implements DNS resource-record lookup from Plan 9 ndb databases and database-backed DNS cache maintenance.

Key responsibilities:
- Opens and combines the configured ndb file with `/net/ndb` when present.
- `dblookup` handles class/type dispatch, `Tall` expansion, cached vs uncached lookup, wildcard domain search, and DNS response-code annotation for missing names.
- `dblookup1` maps DNS RR types to ndb attributes and RR constructors for A, AAAA, CNAME, MX, NS, PTR, SOA, SRV, TXT, CAA, AXFR/IXFR stubs, and wildcard/case/IDN lookup variants.
- Searches ndb by `dom` and, for single-label names, `sys`; tries IDN/UTF and lower-case variants.
- Respects line-level binding before whole-entry binding when associating attributes.
- Builds RR objects for addresses, text strings, aliases, MX/NS/SOA/SRV/CAA, and default TTL/serial values.
- Reads database contents into the DNS cache when `cfg.cachedb` is enabled, attaches authoritative and database RRs, and refreshes when source files change.
- Maintains local domain information via `lookupinfo`, interface scanning, and `mydoms`.
- Detects bad delegations to local DNS names outside owned areas.
- Determines whether IPs are local or on local networks.
- Builds synthetic local DNS server NS/A/AAAA records from `DOTSERVER`, `DNSSERVER`, `@dot`, and `@dns` configuration while rejecting self/duplicate/bad addresses.
- Builds domain search-list PTR records from `dnsdomain`.
- Generates reverse PTRs for owned IPv4 `in-addr.arpa` and IPv6 `ip6.arpa` areas, including classless IPv4 reverse handling and IPv6 nibble-prefix conversion.

Important interactions:
- Uses global DNS configuration/state such as `cfg`, `now`, `owned`, `delegated`, `Area`, `DN`, and RR cache helpers.
- Depends on ndb parsing/searching, IDN conversion, IP interface inspection, and DNS RR allocation/attachment routines.

Notable quirks:
- `doaxfr` is a stub here because TCP-specific transfer handling answers it elsewhere.
- Generated PTR TTL is deliberately nonzero to avoid resolver confusion with zero-TTL PTRs.
- Database reload loops until observed modification times are stable enough for a consistent cache read.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ndb/dblookup.c -->