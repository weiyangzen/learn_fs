# Group Research: group_1629_plan9_sources_os_plan9_plan9_sys_src_cmd_upas_send_send_h_sources_o_bd9588fd6c6b

This group covers Plan 9 `upas` mail sender/SMTP/MIME-filter components plus USB audio, USB mass-storage, and USB Ethernet command drivers. The mail files implement address rewriting support, outbound SMTP, inbound SMTP daemon policy, greylisting, spam controls, MIME attachment filtering, and header/address parsers. The USB files expose device functionality through Plan 9 file interfaces: an audio control/audio endpoint server, a USB mass-storage SCSI-backed disk server, and Ethernet adapter reset/packet hooks.

Scope check: all files are under `sources/os/plan9/plan9`, which is listed in `Docs/research_subset_a.md`.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/send.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/send.h

Read fully: 114 lines, 3580 bytes. SHA-256 prefix: `b47778fb26f278ce`.

This is the shared private interface for `upas/send`. It defines recipient grouping limits (`MAXSAME`, `MAXSAMECHAR`), the `d_status` delivery-state enum, destination records, message records, global flags, and function prototypes used across the sender implementation.

`dest` models one delivery target plus rewrite/translation output, same-command recipient coalescing, parent translations, process status, and authorization state. `message` tracks parsed sender/reply/date/body/temp-file data, discovered RFC822 headers, MIME status, size, and attachment boundary.

Integration: included by send-side modules such as local delivery, rewriting, authorization, translation, logging, forwarding checks, and refusal reporting. It binds the module contracts tightly around Plan 9 `String`, `Biobuf`, `process`, and upas common helpers.

Risk notes: the enum values and struct fields are behavioral contracts across many C files. Recipient coalescing limits are explicitly SMTP/interoperability driven; changing them can affect command lengths and remote mail-system behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/send.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/skipequiv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/skipequiv.c

Read fully: 92 lines, 1747 bytes. SHA-256 prefix: `9c33ed67d265c31d`.

This file implements system-equivalence lookup used to strip already-local or equivalent systems from bang paths. `skipequiv()` walks leading `system!` components and skips each component found in the `equivlist`.

`lookup()` opens and caches local/global upas library files, then delegates membership tests to `okfile()`. `okfile()` scans comma/whitespace-separated tokens and requires exact token boundaries.

Integration: exported through `send.h`; used by send routing/rewrite paths to avoid forwarding loops through equivalent system names. It depends on `abspath()`, `UPASLIB`, `sysopen()`, and Plan 9 `Biobuf` line APIs.

Risk notes: `skipequiv()` temporarily writes NUL bytes into the supplied address string while parsing. Callers must pass mutable storage, not string literals or shared immutable buffers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/skipequiv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/translate.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/translate.c

Read fully: 43 lines, 804 bytes. SHA-256 prefix: `787bce785ad57fbe`.

This file implements address translation by piping a destination through an external command stored in `dp->repl1`. `translate()` starts the process, reads newline-terminated stdout as translated recipients, converts newlines to spaces, and turns the accumulated text into a destination list with `s_to_dest()`.

Lines beginning `_nosummary_` set the global `nosummary` flag and are not included in translated output. Stderr is drained, and nonzero process exit status sets `dp->pstat`, stores stderr text in `dp->repl2`, and returns no translated list.

Integration: invoked for `d_translate` destinations from the send rewrite/delivery pipeline. It uses upas process/stream wrappers and the shared `dest`/`message` structures from `send.h`.

Risk notes: process output directly drives destination expansion. Failed translators communicate diagnostic text through stderr, so callers must preserve `dp->repl2` for useful refusal messages.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/translate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/tryit -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/tryit

Read fully: 29 lines, 584 bytes. SHA-256 prefix: `65d502521297ea2d`.

This is a shell test script for `upas/send` delivery behavior. It prepares test mailbox/forward/pipe files in `/usr/spool/mail`, sends four messages with `mail`, waits, then prints mailbox and pipe-output results.

The cases exercise direct local delivery, forwarding, pipe delivery, and bang-path delivery through `dutoit!bowell!test.local`.

Integration: historical/manual test aid rather than compiled code. It assumes Plan 9 mail paths and commands exist and writes `/tmp/test.mail`.

Risk notes: it mutates real spool paths and uses fixed names. It is not isolated and should only be run in a disposable or test mail environment.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/send/tryit -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/greylist.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/greylist.c

Read fully: 317 lines, 7725 bytes. SHA-256 prefix: `6a137964fda6f57a`.

This file implements SMTP greylisting for `smtpd`. Unknown callers are rejected temporarily until they retry after `Nonspammin` and before `Nonspammax`; successful retry promotes the sender IP into `/mail/grey/whitelist`.

`onwhitelist()` checks IP or CIDR entries in the whitelist. Bare IPv4 entries default to `/24`, intentionally accepting nearby mail hosts from large providers; IPv6 defaults to `/128`. `mkdirs()`/`mkpdirs()` create greylist directory paths, and `addgreylist()` creates or reads per-recipient greylist files under `/mail/grey/tmp/<local-ip>/<remote-ip>/<recipient>`.

`vfysenderhostok()` is the daemon-facing entry point. It returns immediately for whitelisted callers, checks every recipient for recent greylist state, appends the remote IP and optional DNS name to the whitelist on success, or replies `451` and exits on first-time/too-soon/too-late attempts.

Integration: called from `smtpd.c` when greylisting is enabled after sender/recipient policy checks. Uses `nci`, `rsysip`, `rcvers`, and `reply()` from the daemon.

Risk notes: filesystem state is the greylist database. Permissions, path length, or file-server semantics can affect behavior. Recipient names containing `/`, empty names, `.`, and `..` are rejected to avoid path traversal.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/greylist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/mxdial.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/mxdial.c

Read fully: 385 lines, 7753 bytes. SHA-256 prefix: `7a116d5c7322aba8`.

This file dials SMTP destinations using MX records. `mxdial()` parses a dial string, tries MX hosts for the destination domain, and optionally falls back to a configured gateway only for translation failures.

`mxlookup()` queries `/net/dns` and `/net.alt/dns`, stops on DNS failure, falls back to the host itself when there is no MX record, and resolves one IP per MX for loopback/newline safety checks. `callmx()` sorts MX entries by preference, skips configured busted MX hosts, and dials by MX host name with a 60-second alarm.

`dial_string_parse()` decomposes Plan 9 dial strings into network directory, protocol, host, and service. `$`-prefixed host names are expanded through `/net/cs` `!ipinfo` by `expand_meta()`.

Integration: used by outbound `smtp.c::connect()`. It publishes `dial_string_parse()` through `smtp.h` for TLS/auth host selection.

Risk notes: only the first IP per MX is checked, and the actual dial is by name. Loopback and newline checks reduce DNS abuse, but DNS instability is treated as a retry/permanent distinction by the caller.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/mxdial.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/rfc822.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/rfc822.y

Read fully: 779 lines, 13464 bytes. SHA-256 prefix: `be2164c90eebb9a5`.

This Yacc grammar parses RFC822-style message headers for upas SMTP processing. It recognizes originator, destination, date, subject, received, precedence, MIME/content/message-id, optional headers, Unix `From ` lines, address lists, groups, route addresses, and mailbox forms.

The lexer preserves original tokens, comments, folding whitespace, source byte ranges, and address markers in `Node` objects. Parsed fields are stored as `Field` lists; globals such as `originator`, `destination`, `date`, `received`, `messageid`, `usender`, `usys`, and `udate` summarize what was found.

Helper routines link and concatenate nodes, mark address nodes, validate field names, insert `BadHeader:` records for dropped malformed text, preserve or synthesize whitespace, and free parser state. `nobody()` maps empty `<>` senders to `pOsTmAsTeR`.

Integration: outbound `smtp.c` uses it to normalize headers and add missing fields; inbound `smtpd.c` uses it while piping accepted messages to the local mailer and adding warnings.

Risk notes: parsing is intentionally tolerant and source-preserving. Consumers depend on `Node.start`/`Node.end` to splice unparsed body/header bytes; mistakes here can duplicate, omit, or corrupt message content.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/rfc822.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/rmtdns.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/rmtdns.c

Read fully: 60 lines, 1102 bytes. SHA-256 prefix: `8fe86e36c4cf0a84`.

This file provides `rmtdns()`, a small DNS-existence check for remote path domains. It extracts the domain portion before `!`, accepts bracketed or bare IP literals without lookup, then writes `<domain> all` to `<net>/dns`.

If opening DNS fails, it returns success because the daemon cannot check. If the DNS write fails specifically with `dns: name does not exist`, it returns `-1`; other failures are ignored.

Integration: declared in `smtpd.h`; used by SMTP daemon policy code to verify remote sender domains when enabled.

Risk notes: the function treats DNS infrastructure failures as non-fatal and only distinguishes one exact error string. That policy favors mail availability over strict sender-domain enforcement.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/rmtdns.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/smtp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/smtp.c

Read fully: 1136 lines, 21007 bytes. SHA-256 prefix: `0091124574180032`.

This is the outbound SMTP client used by upas. It parses command-line options for TLS, authentication, gateway, host/domain, filter-only mode, ping timing, busted MX skips, and insecure behavior; then dials the destination, performs SMTP greeting, sends envelope commands, transmits DATA, and reports retry/permanent failures.

Connection setup uses `mxdial()`. `hello()` handles banner/EHLO/HELO, STARTTLS discovery, TLS upgrade via `dotls()`, certificate thumbprint validation through `/sys/lib/tls/smtp`, and AUTH LOGIN/PLAIN via Plan 9 auth helpers. `mailfrom()` and `rcptto()` generate envelope commands and classify 2xx/5xx/other replies.

`data()` reads and parses headers, invokes `rfc822.y`, adds missing `Message-ID`, `From`, `To`, and `Date` fields, converts bang addresses to `@`/route-address form, preserves header whitespace, dot-stuffs message data, and normalizes newlines to CRLF. Filter mode writes the transformed message to stdout without an SMTP session.

Address helpers include `bangtoat()`, `convertheader()`, `fixrouteaddr()`, `domainify()`, and timezone rewriting for generated dates. Reply handling supports multiline SMTP replies.

Integration: send rewrite rules invoke this program for remote delivery. It shares parser structures from `smtp.h`/`rfc822.y` and transport resolution from `mxdial.c`.

Risk notes: global state drives the SMTP transaction. TLS thumbprint failure after STARTTLS is treated as permanent unless unknown-secure mode is allowed; some error paths intentionally call `_exits()` to avoid flushing closed Bio streams.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/smtp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/smtp.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/smtp.h

Read fully: 68 lines, 1375 bytes. SHA-256 prefix: `737c2191145ca250`.

This header defines shared SMTP parser and MX-dialer types. `Node` represents a parsed token with links, token type, address flag, preserved string/whitespace, and original source span. `Field` links parsed header fields. `DS` stores parsed Plan 9 dial-string components.

It also defines `Maxbustedmx`, `Maxdomain`, `YYSTYPE`, parser globals, message summary flags, the busted-MX list, and prototypes for parser/link/address helpers, `mxdial()`, and `dial_string_parse()`.

Integration: used by `smtp.c`, `smtpd.c`, `rfc822.y`, `mxdial.c`, `rmtdns.c`, and greylist code.

Risk notes: `YYSTYPE` and struct fields must match generated parser expectations. Source-span fields are used for byte-level reconstruction, so changing ownership or lifetime assumptions can break message rewriting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/smtp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/smtpd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/smtpd.c

Read fully: 1751 lines, 36261 bytes. SHA-256 prefix: `b69f23f52000c306`.

This is the inbound SMTP daemon. It handles process setup, peer discovery, configuration, SMTP replies, greeting, command actions from `smtpd.y`, sender/recipient validation, filtering, DATA ingestion, local mailer execution, STARTTLS, and AUTH.

Startup reads options for authentication, TLS cert, no-relay, greylisting, sender-domain validation, banned IPs, mailer path, and logging/debugging. It gets `NetConnInfo`, parses the remote IP, loads spam config through `getconf()`, rejects banned peers, initializes the command parser, sends a deliberately slow greeting, and parses commands under an alarm.

Policy flow: `hello()` rejects clients pretending to be the local domain or bogus domains; `sender()` enforces authentication when requested and classifies sender/IP through spam policy; `receiver()` validates recipients, sender-IP authorization pairs, and relay rules; `data()` checks envelope state, optional sender MX validation, greylist/filter state, then accepts or rejects the message.

`pipemsg()` writes the accepted message to the configured mailer, adding a Unix `From ` envelope line, `Received`, missing `From`/`To`, and forged-header warnings; it parses the first 16 KiB of headers and handles SMTP dot unescaping. `startcmd()` chooses between real mailer execution, spam dump-to-file, temporary delay, or hard rejection.

TLS and auth: `starttls()` wraps stdin/stdout with `tlsServer()` after reading a certificate. `auth()` supports PLAIN, LOGIN, and CRAM-MD5, requires encryption for clear-password modes unless explicitly allowed, scrubs some password buffers, and marks authenticated clients as trusted.

Integration: generated command parser `smtpd.y` calls functions here; spam policy is in `spam.c`; greylisting in `greylist.c`; header parsing from `rfc822.y`; local delivery typically invokes `upas/send`.

Risk notes: many policy decisions are global/session state. The daemon intentionally kills child mailer processes on alarms. Header parsing assumes the full header is within 16 KiB. DATA success/failure semantics depend on both pipe status and child exit status.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/smtpd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/smtpd.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/smtpd.h

Read fully: 69 lines, 1134 bytes. SHA-256 prefix: `643da5e72212a1eb`.

This is the SMTP daemon shared header. It defines filter/action states (`ACCEPT`, `REFUSED`, `DENIED`, `DIALUP`, `BLOCKED`, `DELAY`, `TRUSTED`, `NONE`), `MAXREJECTS`, linked-list types for senders/recipients, daemon globals, and daemon/spam/greylist/parser function prototypes.

Integration: included by `smtpd.c`, `smtpd.y`, `spam.c`, and `greylist.c`. It exposes session-global state such as `nci`, `dom`, `me`, `trusted`, `senders`, `rcvers`, and `rsysip`.

Risk notes: this header couples parser actions and policy modules to daemon globals. Any new filter state must be reflected in all switch statements in `smtpd.c` and `spam.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/smtpd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/smtpd.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/smtpd.y

Read fully: 318 lines, 6975 bytes. SHA-256 prefix: `1cb023bf154b42de`.

This Yacc grammar parses inbound SMTP commands and mailbox paths. It recognizes HELO/EHLO, MAIL FROM with optional AUTH parameter, RCPT TO, DATA, RSET, SEND/SOML/SAML, VRFY/EXPN, HELP, NOOP, QUIT, STARTTLS, AUTH, blank lines, and path/mailbox/domain forms.

Actions call daemon functions directly: `hello()`, `sender()`, `receiver()`, `data()`, `reset()`, `verify()`, `help()`, `noop()`, `quit()`, `starttls()`, and `auth()`. Address grammar canonicalizes `local@domain` into Plan 9 bang form `domain!local`; route paths are joined with `!`; empty paths become `/dev/null`.

`parseinit()` prepares a reusable bang token and binds lexer input to the SMTP input `Biobuf`. `yylex()` lowercases alphabetic command bytes, maps CRLF to `CRLF`, whitespace to `SPACE`, control bytes to `CNTRL`, and otherwise returns literal characters. `cat()` assembles `String` values from grammar pieces.

Integration: compiled into the daemon and included through generated `y.tab.h` in `smtpd.c`.

Risk notes: grammar accepts a relatively old SMTP/path model, including source routes and bang paths. It masks input to 7 bits and lowercases letters, which is appropriate for commands but constrains raw path syntax.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/smtpd.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/spam.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/spam.c

Read fully: 594 lines, 10298 bytes. SHA-256 prefix: `1d9c02aeb8781c38`.

This file implements `smtpd` spam and relay policy support. It reads SMTP daemon config, maps IP/account actions from `/mail/ratify`, tracks trusted networks/domains, checks forwarding/masquerading, validates recipients, handles banned IP CIDRs, and chooses blocked-message dump files.

`getconf()` reads `/mail/lib/smtpd.conf` options such as `norelay`, `verifysenderdom`, `saveblockedmsg`, `defaultdomain`, `ournets`, and `ourdomains`. `blocked()` classifies a sender based on trusted IP, remote-IP action, then lowercased account action. `forwarding()` rejects untrusted relay attempts outside local domains but supports loopback `[]!` rewriting to the remote IP literal.

`masquerade()` detects untrusted senders claiming local domains for warning headers. `recipok()` rejects shell metacharacters, optionally runs `/mail/lib/validateaddress`, and consults `names.blocked`. `optoutofspamfilter()` lets recipients skip spam filtering via `/mail/box/<user>/nospamfiltering`.

Integration: `smtpd.c` calls these routines during MAIL/RCPT/DATA handling. Shared list helpers and daemon globals come from `smtpd.h`.

Risk notes: policy is filesystem-driven and sensitive to exact file layout and config tokenization. CIDR matching is IPv4-only for `ournets`/badguy checks. External validator exit messages determine accept/reject behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/smtp/spam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/unesc/unesc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/unesc/unesc.c

Read fully: 52 lines, 969 bytes. SHA-256 prefix: `1f4bc2c8322c2f1c`.

This command decodes a narrow form of RFC2047-like encoded words from stdin to stdout. It copies ordinary bytes, detects `=?charset?encoding?encoded?=`, discards charset and encoding labels, and decodes `=HH` hex escapes inside the encoded section.

`hex()` maps hex digits to numeric values and returns zero for invalid input. `main()` streams with `Biobuf`, consumes encoded-word delimiters, and preserves malformed non-encoded `=` sequences as literal output.

Integration: standalone upas utility; likely used in mail-processing pipelines where encoded header fragments need simple unescaping.

Risk notes: it ignores the declared charset and encoding mode and only decodes quoted-printable-style `=HH`. It is not a complete RFC2047 decoder.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/unesc/unesc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/vf/vf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/vf/vf.c

Read fully: 1127 lines, 20307 bytes. SHA-256 prefix: `4c9d3f6db2c74e2e`.

`upas/vf` is a MIME attachment filter. It reads a message, recursively parses MIME parts, classifies content types and filenames using `/sys/lib/mimetype`, rejects or rewrites suspect executable attachments, and preserves/pass-throughs safe message content.

The parser builds `Part` objects with header lines, disposition, transfer encoding, content type, charset, boundary, filename, and temporary-buffer state. `part()` handles multipart recursion, forwarded `message/rfc822`, and leaf bodies. `passbody()` streams until an ancestor boundary, supporting temporary saved bodies when an external checker is run.

For suspect content, `problemchild()` optionally runs `/mail/lib/validateattachment`; if not accepted and not in reject-only mode, it wraps the attachment in a new multipart message explaining that headers were changed, renames the file with `.suspect`, and changes type/disposition to safer values. Hard-reject class files call `refuse()`.

Header parsing handles `Content-Type`, `Content-Transfer-Encoding`, `Content-Disposition`, boundary/name/charset/filename attributes, and RFC2047-like filename conversion for UTF-8, US-ASCII, and ISO-8859-1 with base64 or quoted decoding.

Integration: used as a mail filter before final delivery. It logs to `vf`/`mail`, can save rejected content to `-s savefile`, and signals refusal by posting a note to its process group.

Risk notes: the source contains visible debug `fprint(2, "x\n")`/similar traces in `problemchild()`. MIME parsing is hand-written and boundary-sensitive; malformed headers or unusual encodings may pass through or be wrapped conservatively.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/upas/vf/vf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audio.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audio.c

Read fully: 402 lines, 9991 bytes. SHA-256 prefix: `826e71b2b01e6060`.

This is the main USB audio driver command. It discovers/configures a USB audio device, parses descriptors, selects playback/record endpoints and defaults, initializes controls, optionally opens HID volume buttons, and starts control/button/server processes.

`audio_endpoint()` parses class-specific endpoint descriptors and records capabilities such as sampling-frequency control, pitch control, and max-packet-only behavior into the alternate setting’s `Audioalt`.

`threadmain()` handles options for debug, mountpoint, srv name, device number, attachment permissions, and initial volume. It finds an audio device by class/subclass/protocol, configures it, scans descriptors via `audio_interface()`/`audio_endpoint()`, chooses endpoints, sets default 44.1 kHz or fallback 48 kHz stereo 16-bit playback/recording, unmutes playback, applies volume, and starts `controlproc`, `buttonproc`, and `serve`.

`controlproc()` serializes textual control changes from the file server/buttons into `setcontrol()` calls. `buttonproc()` reads HID button events and adjusts playback volume.

Integration: works with `audioctl.c`, `audiosub.c`, and `audiofs.c`; uses Plan 9 USB library `Dev`, `Ep`, descriptor data, and endpoint control operations.

Risk notes: the file’s opening comment says the driver needs a rewrite and may cross nil pointers. Initialization has device-specific assumptions and a record fallback path that appears to force 48 kHz when the preferred rate is unavailable.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audio.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audio.h

Read fully: 84 lines, 2050 bytes. SHA-256 prefix: `7de4a938c843d06d`.

This header defines USB audio descriptor constants, control IDs, sample format tags, `Audioalt`, capability bits, global driver state, and cross-file function prototypes.

`Audioalt` stores alternate-setting audio capabilities: channel count, resolution, subframe size, continuous/discrete frequency ranges, and flags such as `has_setspeed`, `has_contfreq`, `has_discfreq`, `onefreq`, and `maxpkt_only`.

Integration: shared by all USB audio implementation files. It connects descriptor parsing, control selection, endpoint setup, and the 9P file server.

Risk notes: control IDs mix USB-standard and implementation-defined controls in one enum. Array dimensions and indexes must remain aligned with `audioctl.h` and `controls[2][Ncontrol]`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audioctl.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audioctl.c

Read fully: 697 lines, 17862 bytes. SHA-256 prefix: `65190a43b7902f31`.

This file implements USB audio control state, alternate-setting selection, speed management, feature-unit get/set operations, and text parsing/formatting for control values.

Global arrays track endpoint IDs, interface IDs, feature/selector/mixer units, current alternate settings, and `Audiocontrol` descriptors for playback/record. `findalt()` scans endpoint alternate settings populated by descriptor parsing to find channel/resolution/speed-compatible modes while updating min/max control ranges.

`setspeed()` clamps or selects continuous/discrete/one-frequency rates, optionally sends class endpoint `SET_CUR` sampling-frequency requests, verifies current speed, opens endpoint devices, and configures endpoint polling interval, sample size, and Hz. `setcontrol()` handles logical controls: speed, channels, resolution, feature-unit controls, and selector controls.

`getspecialcontrol()`, `getcontrol()`, and `getcontrols()` query current/min/max/resolution via USB class requests and populate cached values. `ctlparse()` parses scalar or per-channel values, including percentages mapped into min/max ranges. `Aconv()` formats controls for textual output.

Integration: called by `audio.c` initialization, `controlproc`, and `audiofs.c` reads/writes. It issues `usbcmd()` and endpoint `devctl()` operations.

Risk notes: many paths return `Undef` as an error/sentinel mixed with integer values. Channel bitmaps assume up to 7 numbered channels plus master. Device quirks are handled inline, such as Griffin iMic speed reporting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audioctl.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audioctl.h

Read fully: 29 lines, 618 bytes. SHA-256 prefix: `ce38668e176dfafd`.

This header defines playback/record indexes, `Undef`, `Audiocontrol`, control globals, and control helper prototypes.

`Audiocontrol` records a control name, readability/settability, channel bitmap, cached master/per-channel values, and min/max/step bounds. The header also declares unit IDs for endpoints, interfaces, feature/selector/mixer units, and HID button endpoint.

Integration: shared by `audio.c`, `audioctl.c`, `audiofs.c`, and `audiosub.c`; also registers `%A` formatting for `Audiocontrol`.

Risk notes: value arrays are fixed at 8 entries and depend on channel bitmap interpretation used throughout the driver.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audiofs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audiofs.c

Read fully: 939 lines, 17739 bytes. SHA-256 prefix: `9293e810abca627c`.

This file implements the small 9P file server exported by `usbaudio`. It serves a directory with `volume`, `audioctl`, and `audiostat`, mounts it under `/dev` by default, optionally posts `/srv`, and names USB endpoint data files as `audio` and `audioin`.

The server implements 9P handlers for version, attach, walk, open, read, write, clunk, stat, and rejects create/remove/wstat/auth. `volume` provides legacy percentage-style controls; `audioctl` reports changed controls and accepts textual control writes; `audiostat` is present in the directory but has no special read content in this file.

`Audioctldata` stores per-fid last-sent control values and buffered text. Reads from `audioctl` block off-line via `Worker` threads until a control change arrives; `ctlevent()` wakes workers after control updates. `rwrite()` parses control lines and sends serialized requests over `controlchan`, waiting on `replchan` for success/errors.

Integration: `serve()` is started by `audio.c`; it uses `setcontrol()` through `controlproc`, Plan 9 `Fcall` marshalling, and endpoint `devctl("name audio")` binding.

Risk notes: comments note a namespace bug: `/dev/audio` and `/dev/audioin` are created via endpoint name binding rather than being real served files, so mounting from another namespace may not expose them as expected. Blocking reads rely on careful worker/fid locking and flush handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audiofs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audiosub.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audiosub.c

Read fully: 300 lines, 8015 bytes. SHA-256 prefix: `53df19a9efb07f1f`.

This file parses USB audio class-specific interface descriptors and populates driver control/topology state. It names terminal types, tracks playback/record unit IDs, identifies terminals, mixers, selectors, feature units, and streaming format descriptors.

`audio_interface()` switches on interface subclass: audio control descriptors define input/output terminals, mixer/selector/feature units, and available controls; audio streaming descriptors define terminal linkage and format type details. Format descriptors populate `Audioalt` with channels, resolution, subframe size, continuous/discrete frequencies, and capability flags.

Feature-unit parsing marks supported mute/volume/bass/etc. controls as readable/settable for master or per-channel use. Selector and mixer unit IDs are assigned to playback or record based on source unit membership.

Integration: called during `audio.c` descriptor scan before `findalt()` and `getcontrols()`. It writes globals from `audioctl.h`.

Risk notes: topology inference is heuristic and fixed-size (`units[2][8]`). Complex devices with multiple mixers/selectors/features can trigger "Second ..." warnings and overwrite unit IDs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audiosub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/disk/disk.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/disk/disk.c

Read fully: 805 lines, 16221 bytes. SHA-256 prefix: `f75832a7be89a77b`.

This file implements the per-device USB mass-storage file server and bulk-only SCSI transport. It exposes each logical unit as an `sdU<dev>.<lun>` USB filesystem with `ctl`, `raw`, and `data` files.

Initialization finds bulk IN/OUT endpoints, resets the device, gets max LUN, runs SCSI inquiry/start/capacity for each usable disk-like LUN, handles large capacity via READ CAPACITY(16), and registers a `Usbfs` per LUN. `ctl` reports inquiry and geometry in sd-compatible text form.

`umsrequest()` wraps SCSI command/data/status in USB bulk-only `Cbw` and `Csw` structures, transfers data, handles stalls, validates signatures/tags/status, maps failures to SCSI status, and performs reset/unstall recovery. Too many errors detach the device and remove LUN filesystems.

`dread()`/`dwrite()` implement directory reads, raw command phase handling, and block data I/O. `setup()` maps byte offsets/counts into block-aligned transfers, using an intermediate buffer for unaligned reads/writes and enforcing `Maxiosize`.

Integration: `main.c` discovers matching USB storage devices and calls `diskmain()`. `scsireq.c` calls `umsrequest()` for `Fusb` requests.

Risk notes: only SCSI command-set mass storage is supported, not ATA. The raw interface has a strict command/data/status phase machine. Unaligned writes perform read-modify-write and reset cached capacity after errors because media may have changed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/disk/disk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/disk/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/disk/main.c

Read fully: 72 lines, 1196 bytes. SHA-256 prefix: `7f418d51b444ca81`.

This is the entry point for the USB disk server command. It parses debug, device-number, mountpoint, and srv options; initializes `usbfs`; then starts all matching USB mass-storage devices with `diskmain()`.

Supported class/subclass/protocol matches include ATAPI bulk, SFF-8070 bulk, and SCSI transparent bulk storage. Default mountpoint is `/n/disk`.

Integration: delegates all per-device behavior to `disk.c`; uses shared USB discovery helpers `startdevs()`, `matchdevcsp()`, and `usbdirfs`.

Risk notes: command-line arguments are forwarded into a bounded 80-byte `args` buffer. Excessive option text could be truncated by `seprint()` rather than rejected.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/disk/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/disk/mkscsierrs -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/disk/mkscsierrs

Read fully: 32 lines, 419 bytes. SHA-256 prefix: `a3d0fe841c9a4dc1`.

This `rc` script generates C source for SCSI error-code lookup. It emits includes, an `Err` table, reads `/sys/lib/scsicodes` lines matching four hex digits, transforms them into `{0xNNNN, "message"}` rows, and emits `scsierrmsg()`.

Integration: supports `scsireq.c::scsierr()` diagnostics. The generated table is not present in this source file; it depends on the system scsi code database at generation time.

Risk notes: generation uses `grep` and `sed` over a system file. Output quality depends on `/sys/lib/scsicodes` format matching the hard-coded expression.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/disk/mkscsierrs -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/disk/scsireq.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/disk/scsireq.c

Read fully: 987 lines, 19672 bytes. SHA-256 prefix: `30cd71259cab8c53`.

This file is a local copy/adaptation of Plan 9 `scuzz` SCSI request helpers, with extra debug support and USB transport support. It builds SCSI command descriptor blocks, routes requests through raw scuzz devices or `umsrequest()`, handles sense data, and provides open/read/write/seek/capacity helpers.

Command helpers include TEST UNIT READY, REWIND, REQUEST SENSE, FORMAT, READ BLOCK LIMITS, READ/WRITE(6/10), SEEK(6/10), FILEMARK, SPACE, INQUIRY, MODE SELECT/SENSE(6/10), START STOP, READ CAPACITY(10), and READ CAPACITY(16). Direct-access requests use 10-byte commands when offsets/counts exceed 6-byte limits or flags request them.

`SRrequest()` dumps debug traces, calls the selected transport, maps status, requests sense on check condition, retries busy devices, and sets `werrstr()` from `scsierrmsg()`. Open helpers configure direct, sequential, WORM/CD, printer, and changer device flags and block sizes.

Integration: used by `usb/disk/disk.c`; header notes it is also included by cdfs/scuzz contexts. For USB, `Fusb` and `umsc` route requests to the bulk-only transport.

Risk notes: comments acknowledge incomplete behavior. `exabyte` and `force6bytecmds` global quirks affect command selection and error handling. Sequential/tape short-read logic is preserved even though USB disk primarily uses direct-access devices.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/disk/scsireq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/disk/scsireq.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/disk/scsireq.h

Read fully: 176 lines, 5291 bytes. SHA-256 prefix: `34c6adb150e1b6df`.

This header defines SCSI request structures, flags, status codes, sense bits, device types, endian helpers, and function prototypes used by USB disk and other SCSI consumers.

`ScsiReq` stores unit path, LUN, logical block size, block offset, raw fd, USB LUN pointer, command/data buffers, returned status, sense data, inquiry data, and flags. `ScsiPtr` describes a command or data transfer buffer and direction.

Integration: included by `disk.c`, `main.c`, and `scsireq.c`. It declares `umsrequest()` as the USB transport hook and many SCSI/MMC/changer prototypes, including functions not implemented in this local `scsireq.c` subset.

Risk notes: `Maxiosize` is tied to Plan 9 devmnt message sizing. The header contains a non-ASCII exponent comment in `Max24off`; generated or ASCII-only tooling should avoid altering semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/disk/scsireq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/disk/ums.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/disk/ums.h

Read fully: 106 lines, 1787 bytes. SHA-256 prefix: `af10254364756eb2`.

This header defines USB mass-storage protocol/subclass constants, bulk-only transport constants, per-LUN/device structures, and CBW/CSW layouts.

`Umsc` embeds `ScsiReq` and adds capacity, setup state, raw command buffer, raw-phase state, inquiry string, parent `Ums`, per-LUN `Usbfs`, and an aligned transfer buffer. `Ums` tracks the USB device, bulk endpoints, LUN array, max LUN, sequence tag, error count, and residue quirk flag.

`Cbw` and `Csw` correspond to USB bulk-only Command Block Wrapper and Command Status Wrapper, using `"USBC"`/`"USBS"` signatures.

Integration: shared by `disk.c` and `main.c`; `diskmain()` is declared here for the device starter.

Risk notes: `Maxlun` is capped at 32 despite a commented 256. The structs assume transparent SCSI bulk-only transport and are not suitable for CBI/CB or ATA without new code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/disk/ums.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/ether/asix.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/ether/asix.c

Read fully: 489 lines, 10209 bytes. SHA-256 prefix: `2c86bc6fc1122e31`.

This file implements support hooks for ASIX USB Ethernet adapters. It contains vendor request constants, reset/GPIO/MII/media/RX-control bit definitions, controller initialization for supported chips, packet framing/unframing, promiscuous mode, multicast mode, and reset registration.

Low-level helpers issue vendor `usbcmd()` reads/writes, read GPIO/PHY/RX control/MAC/EEPROM, and access MII registers. `ctlrinit()` configures AX88178 and AX88772-like devices, including GPIO sequences, PHY selection/reset, auto-negotiation advertisement, medium mode, IPG, and RX control. Some known chips are recognized but reported unimplemented.

ASIX USB packets carry a 32-bit length/complement header. `asixbread()` reads aggregate USB data, validates the header, copies Ethernet frames into generic `Buf`s, and caches remaining aggregate data. `asixbwrite()` prepends the length/complement header and adds a zero-length-style terminator header when packet length aligns with endpoint max packet size.

Integration: plugs into the common USB Ethernet framework through `Ether` callbacks (`bread`, `bwrite`, `free`, `promiscuous`, `multicast`) and `asixreset()`.

Risk notes: comments note behavior was inferred from other systems without documentation. Multicast filtering is not implemented precisely; it toggles all-multicast when any multicast subscriptions exist. A8817x/A88179 are known but not implemented.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/ether/asix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/ether/cdc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/ether/cdc.c

Read fully: 60 lines, 1105 bytes. SHA-256 prefix: `391a15737254ae37`.

This file provides generic CDC Ethernet reset support. It assumes communication-class devices not claimed by specific controller drivers are standard Ethernet communication devices and tries to load their MAC address from CDC functional descriptors.

`getmac()` scans device descriptors for an Ethernet networking functional descriptor on a communication/ethernet interface, loads the string descriptor containing the 12-hex-digit MAC address, validates length, and parses it into `ether->addr`.

`cdcreset()` applies this generic path only when the USB device class is communications; specific controller probes are expected to run first.

Integration: part of the shared USB Ethernet driver stack and depends on helper functions from `ether.h` such as `parseaddr()`.

Risk notes: it ignores CDC union descriptors and only retrieves the MAC address; endpoint/interface pairing is left to the generic Ethernet framework. Devices with nonstandard descriptors may need a specific driver.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/usb/ether/cdc.c -->