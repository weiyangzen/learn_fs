# Group Research: group_1613_plan9_sources_os_plan9_plan9_sys_src_cmd_spin_sym_c_sources_os_plan_0e9f9a4a178a

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/sym.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/sym.c

Spin symbol-table and declaration bookkeeping module.

Key responsibilities:
- Maintains Promela symbols in `symtab[Nhash+1]` and insertion order in `all_names`.
- Implements scoped `lookup`, with legacy and newer scope behavior using `context`, `owner`, and `CurScope`.
- Performs declaration typing via `setptype`, including redeclaration checks, array-size validation, channel `Nid` assignment, hidden/show/local flags, and unsigned width validation.
- Tracks channel usage and exclusive receive/send claims through `setaccess`, `setxus`, `setonexu`, and `Xu_List`.
- Tracks `mtype` constants and maps names to values with `setmtype` and `ismtype`.
- Reports symbol tables, channel access, and unused variables through `symdump`, `symvar`, and `chanaccess`.

Important data flow:
- Parser-created `Lextok` name lists are typed here.
- Channel and variable metadata later drives verifier generation, warnings, and x[rs] safety claims.
- `trackrun` and `checkrun` inspect `run` statements to infer possible narrower parameter types.

Notable details:
- `disambiguate` rewrites non-global scoped names by prefixing scope bytes when modern scope rules are active.
- Hidden bit flags are overloaded for visibility, type-width hints, formal parameters, and use markers.
- `setmtype` enforces <=255 effective elements and assigns constant initializers.

Risks/quirks:
- Uses global mutable compiler state heavily.
- Scope comparison has subtle prefix matching under newer rules.
- Name rewriting intentionally leaks/abandons old name memory.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/sym.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/tl.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/tl.h

Shared header for Spin's LTL translator.

Key responsibilities:
- Defines minimal `Symbol`, `Node`, `Graph`, and `Mapping` structures used by the LTL parser, rewriter, automaton generator, and Buchi printer.
- Defines token enum for temporal logic operators: `ALWAYS`, `EVENTUALLY`, `U_OPER`, `V_OPER`, `PREDICATE`, booleans, implication/equivalence, and optional `NEXT`.
- Declares cross-module APIs for parsing, lexing, canonicalization, graph translation, cache/memory management, and output.

Important data structures:
- `Node`: LTL AST with `ntyp`, `sym`, `lft`, `rgt`, and `nxt` list linkage.
- `Graph`: state-expansion node with New/Old/Next formula sets, incoming/outgoing symbols, acceptance color arrays, and reachability flags.
- `Mapping`: maps collapsed graph node names to canonical graph states.

Notable details:
- `Nhash` must match Spin's main `spin.h`.
- `rewrite(n)` macro applies right-linking and canonicalization.
- `True`, `False`, and `Not` are constructor macros that allocate AST nodes.

Risks/quirks:
- This header assumes C89-style global function declarations.
- `exit` is redeclared, reflecting old Plan 9/Spin portability style.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/tl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/tl_buchi.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/tl_buchi.c

Converts translated automaton graph transitions into a Promela `never` claim.

Key responsibilities:
- Maintains `State` and `Transition` lists representing the output Buchi automaton.
- Adds transitions from graph generation via `addtrans`.
- Prunes conditions, removes impossible/simple contradictory transitions, merges equivalent transitions and states, and emits final Promela code with `fsm_print`.
- Handles acceptance-state naming, reachability, `accept_all`, and optional optimizations.

Important functions:
- `Prune`: removes non-printable/non-state-condition portions from formulas.
- `unclutter`/`clutter`: detect simple contradictory conjunctions like `p && !p`.
- `mergetrans`: combines transitions to the same target by OR-ing conditions.
- `mergestates`: removes states with equivalent transition sets and matching acceptance.
- `buckyballs`: optional optimization for mutually equivalent accepting cycles.
- `rev_trans`/`printstate`: output Promela guarded commands.

Data flow:
- `tl_trans.c` calls `addtrans`, then `fsm_print`.
- Transition conditions are duplicated, pruned, rewritten, and printed through `dump_cond`.

Risks/quirks:
- Several optimizations are suppressed when `tl_verbose` is enabled.
- State retargeting uses string-name matching.
- Fixed-size buffers assume generated names fit expected lengths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/tl_buchi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/tl_cache.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/tl_cache.c

Canonical-form cache and AST utility module for the LTL translator.

Key responsibilities:
- Caches formula rewrites from input AST (`before`) to canonical AST (`after`) to avoid repeated normalization.
- Allocates, duplicates, compares, and releases `Node` trees.
- Implements structural and algebraic equality checks, including commutative equality for right-linked AND/OR trees.
- Provides `anywhere` helpers for containment checks in AND/OR contexts.

Important functions:
- `cached`, `in_cache`: cache lookup/store around `Canonical`.
- `tl_nn`, `getnode`, `dupnode`, `releasenode`: AST allocation and lifecycle.
- `sameform`, `isequal`, `ismatch`: increasingly strict/equivalence-aware comparisons.
- `any_term`, `any_and`, `any_lor`, `anywhere`: formula containment queries used by rewrite and automaton logic.

Notable details:
- A `NULL` node can compare equal to `TRUE` in `isequal`, matching translator conventions.
- Cache returns duplicates of stored canonical forms to avoid accidental mutation of cached objects.

Risks/quirks:
- Memory is managed through translator pool allocator `tl_emalloc`/`tfree`.
- Equality logic depends on right-linked AND/OR normalization for full effectiveness.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/tl_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/tl_lex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/tl_lex.c

Lexer and symbol table for Spin LTL formulas.

Key responsibilities:
- Tokenizes LTL syntax from `tl_Getchar` input.
- Recognizes textual operators (`always`, `eventually`, `until`, `not`, optional `next`) and symbolic operators (`[]`, `<>`, `U`, `V`, `&&`, `||`, `->`, `<->`).
- Treats balanced `{...}` or `(...)` groups as predicates when they do not contain LTL operators.
- Interns predicate strings into a local `tl_lookup` symbol table.

Important functions:
- `tl_lex`/`tl_yylex`: main tokenization.
- `is_predicate`: peeks ahead to decide if parentheses/braces represent an atomic predicate.
- `read_upto_closing`: captures predicate text.
- `tl_follow`: validates two-character operators.
- `getsym`: copies a symbol wrapper while sharing the name.

Risks/quirks:
- Predicate lookahead has hard limits around 2047 chars and a 512-char local word buffer for operator detection.
- Whitespace handling expects tabs/newlines to be pre-normalized by `tl_main.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/tl_lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/tl_main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/tl_main.c

Top-level driver and diagnostics for the LTL translator.

Key responsibilities:
- Stores the active formula in static `uform[4096]`.
- Provides character stream functions used by lexer: `tl_Getchar`, `tl_peek`, and `tl_UnGetchar`.
- Initializes translator subsystems and parses `spin -f`-style options.
- Prints normalized formulas, full formulas in never-claim comments, and token explanations.
- Emits fatal parse diagnostics with caret location.

Important functions:
- `tl_main`: resets global translator state, parses `-f`, `-v`, `-n`, and `-c`, then calls `tl_parse`.
- `tl_balanced`: checks parentheses balance.
- `dump`: pretty-prints AST nodes.
- `Fatal`/`tl_yyerror`: report and exit on LTL errors.

Risks/quirks:
- Copies formula into fixed 4096-byte buffer with `strcpy`.
- `-n` normalizes and exits before automaton generation.
- `tl_out` is used for formula and never-claim output, allowing standalone or embedded operation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/tl_main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/tl_mem.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/tl_mem.c

Pool allocator for Spin's LTL translator.

Key responsibilities:
- Allocates small fixed-size chunks from per-size freelists.
- Tracks allocation statistics by size class.
- Frees small allocations back to freelists; large allocations are intentionally not returned to libc.
- Maintains `All_Mem` accounting.

Important functions:
- `tl_emalloc`: rounds requested bytes to `union M` units, allocates blocks in growing batches, clears memory, and tags blocks with `A_USER`.
- `tfree`: validates allocation tag and returns small blocks to freelist.
- `a_stats`: prints pool/allocation/free counters.

Notable details:
- Size classes below `A_LARGE` are pooled.
- Batch sizes grow until `NOTOOBIG`.
- Large frees are logged but not actually freed.

Risks/quirks:
- Not thread-safe.
- Free validation only checks a magic high-byte tag.
- Designed for short-lived translator runs where leaking large blocks is acceptable.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/tl_mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/tl_parse.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/tl_parse.c

Recursive-descent parser and local simplifier for LTL formulas.

Key responsibilities:
- Parses unary temporal/logical operators, predicates, booleans, parentheses, and two binary precedence levels.
- Performs algebraic simplifications during parsing for U/V/AND/OR/IMPLIES/EQUIV and optional NEXT.
- Converts implication/equivalence into primitive forms.
- Sends final AST to `trans`.

Important functions:
- `tl_factor`: parses atomic/unary expressions, expands `[]p` to `false V p` and `<>p` to `true U p`.
- `bin_simpler`: simplifies binary forms such as `p U p`, identity/absorbing boolean rules, and some temporal absorption rules.
- `tl_level`: precedence parser over `U/V` and `OR/AND/IMPLIES/EQUIV`.
- `tl_parse`: parse, verify no trailing input, call `trans`.

Risks/quirks:
- Associativity and simplification rely on mutable AST reuse.
- Optional `NO_OPT` disables many simplifications.
- Parser uses global `tl_yychar` and `tl_yylval`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/tl_parse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/tl_rewrt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/tl_rewrt.c

Canonical rewrite engine for LTL formula ASTs.

Key responsibilities:
- Pushes negations inward using dualities.
- Right-links associative AND/OR trees.
- Sorts and deduplicates AND/OR clauses.
- Removes redundant clauses using boolean absorption and constants.

Important functions:
- `right_linked`: normalizes nested AND/OR associativity.
- `push_negation`: rewrites `!true`, `!false`, `!!p`, De Morgan forms, and U/V duals.
- `addcan`: builds a sorted canonical list based on `DoDump` string symbols.
- `Canonical`: canonicalizes top-level AND/OR, handles constants, duplicates, and absorption.

Data flow:
- Used via `rewrite(n)` macro across parser, cache, Buchi, and graph generation.
- Relies on `in_cache`/`cached` from `tl_cache.c` for repeated work.

Risks/quirks:
- Uses a single static `can` accumulator reset per call.
- Sorting key is a dumped symbolic representation, not a structural hash.
- Many operations mutate and release passed nodes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/tl_rewrt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/tl_trans.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/tl_trans.c

Core LTL-to-automaton translation module based on Gerth/Peled/Vardi/Wolper.

Key responsibilities:
- Expands LTL formulas into graph states using New/Old/Next formula sets.
- Collapses equivalent states via canonical Old/Next representations.
- Computes acceptance conditions for until formulas.
- Converts the Streett-like intermediate graph into Buchi transitions emitted by `tl_buchi.c`.

Important functions:
- `expand_g`: main state-expansion algorithm for AND, OR, U, V, predicates, booleans, and optional NEXT.
- `not_new`: detects duplicate graph states and records mappings.
- `fixinit`: creates explicit init graph and resolves incoming/outgoing edges.
- `liveness`, `mk_red`, `mk_grn`: classify states for acceptance obligations.
- `mkbuchi`/`fsm_trans`: generate named Buchi states and transitions.
- `dump_cond`: emits transition guard expressions.
- `trans`: top-level translation driver.

Data structures:
- `Nodes_Stack`: pending graph states.
- `Nodes_Set`: accepted graph states.
- `Mapped`: collapsed name mapping.
- Acceptance labels use fixed `isred[64]` and `isgrn[64]` arrays in `Graph`.

Risks/quirks:
- Fatal if more than 63 until acceptance classes.
- Uses name strings to identify graph nodes and mappings.
- Extensive mutable list manipulation across `nxt`, `lft`, and `rgt`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/tl_trans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/vars.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/vars.c

Spin runtime/interpreter variable access and state display module.

Key responsibilities:
- Reads and writes Promela variables in global and local contexts.
- Handles predefined names `_`, `_last`, `_p`, `_pid`, and `_nr_pr`.
- Lazily initializes variable storage and channel instances.
- Casts assigned values to Promela types and reports truncation.
- Dumps global/local variable state for simulation/tracing.

Important functions:
- `getval`/`setval`: dispatch local/global variable access.
- `checkvar`: bounds-checks, declares implicit ints, and initializes arrays/channels.
- `cast_val`: enforces BIT/BYTE/SHORT/UNSIGNED/MTYPE coercions.
- `dumpglobals`/`dumplocal`: print simulation-visible state and optional MSC/track output.
- `dumpclaims`: emits generated x[rs] claim code for channels.

Risks/quirks:
- Reading `_` warns and returns zero.
- Self-referential initializers are rewritten to constant zero.
- Visibility output behavior is controlled by many global flags.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/vars.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/version.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/version.h

Single-version definition for this Spin import.

Content:
- Defines `SpinVersion` as `Spin Version 6.1.0 -- 4 May 2011`.

Role:
- Used by Spin command build/version reporting.

Risks/quirks:
- Static version string only; no logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/spin/version.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/split.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/split.c

Plan 9 `split` command implementation.

Key responsibilities:
- Splits input by fixed line count (`-n`/`-l`) or regex boundaries (`-e`).
- Writes sequential output files named by stem plus suffix, default `xaa`, `xab`, etc.
- Supports regex-captured output names, suffix appending, case-insensitive matching, and suppressing matched lines with `-x`.

Important functions:
- `main`: parses options, opens optional input file, drives line or pattern splitting.
- `nextfile`: advances two-letter suffix through `aa`..`zz`.
- `matchfile`: opens file named by regex submatch or next suffix.
- `openf`: creates and initializes output `Biobuf`.
- `fold`: lowercases ASCII for case-insensitive regex matching.

Risks/quirks:
- Only supports two-letter suffix range; after `zz`, reports unsplit remainder once.
- `name[200]` can be overflow-prone when regex capture plus suffix exceeds expectations.
- Error string in `openf` says `grep: can't create`, likely copy/paste.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/split.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/srv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/srv.c

Plan 9 command for dialing or executing a service, posting it in `/srv`, and optionally mounting it.

Key responsibilities:
- Dials `net!host` service `9fs` or runs a command via `-e`.
- Posts the connected fd into `/srv/name`.
- Optionally mounts it at a derived or explicit mount point using `mount` or authenticated `amount`.
- Handles retry on hangup/timed-out mount by removing stale `/srv` entry.

Options:
- Mount placement flags: `-a`, `-b`, `-c`, `-C`, `-m`.
- `-n`: skip authentication and use `mount`.
- `-q`: post/check but do not mount.
- `-s`: sleep after connection before posting.
- `-e`: execute command instead of dialing.

Important functions:
- `connectcmd`: pipe to `/bin/rc -c`.
- `post`: writes fd number to `/srv/...`.
- `main`: derives srv name and mount point, connects, posts, mounts.

Risks/quirks:
- `post` leaves posted fd lifetime tied to process/fd semantics.
- Uses a 10-second alarm for connection establishment.
- Existing srv files are removed when mount retry sees hangup-like errors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/srv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/srvfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/srvfs.c

Small wrapper that starts `exportfs` and posts the resulting pipe in `/srv`.

Key responsibilities:
- Builds an `exportfs` argv with selected options.
- Creates a pipe to the exportfs child.
- Sends the exported path to the child and expects `OK`.
- Posts the pipe fd to `/srv/name` or an absolute srv path.

Options:
- `-d`, `-R`, `-P patternfile` forwarded to exportfs.
- `-e exportfs`: custom exportfs binary.
- `-p perm`: permission for srv file.

Risks/quirks:
- Fixed `arglist[16]` is enough for current options but not dynamically checked.
- Assumes exportfs handshake returns exactly `OK`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/srvfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/srvold9p/9p1.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/srvold9p/9p1.h

Protocol definitions for old Plan 9 9P1 messages.

Key responsibilities:
- Defines fixed record sizes: directory, error, and name records.
- Defines `Qid9p1` and `Fcall9p1`.
- Enumerates old protocol message type numbers.
- Declares conversion routines between old wire format, Plan 9 `Fcall`, `Dir`, tickets, and authenticators.

Important details:
- 9P1 uses fixed-size 28-byte names and 116-byte directory records.
- `Fcall9p1` is a tagged union-like struct with overlapping fields for all message classes.
- Includes older auth/session message types and obsolete/illegal variants.

Risks/quirks:
- Fixed-size string fields require careful truncation/NUL behavior.
- `MAXSYSCALL` follows message enum, not necessarily array count semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/srvold9p/9p1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/srvold9p/9p1lib.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/srvold9p/9p1lib.c

Serialization, deserialization, and formatting library for old 9P1 protocol records.

Key responsibilities:
- Formats `Fcall9p1` messages for diagnostics via `%G`.
- Converts `Fcall9p1` structs to/from 9P1 wire byte streams.
- Converts between modern `Dir` and fixed 9P1 directory records.
- Converts old auth ticket/authenticator records with optional DES encryption/decryption.

Important functions:
- `fcallfmt9p1`: readable per-message diagnostics.
- `convS2M9p1`: struct-to-wire conversion.
- `convM2S9p1`: wire-to-struct conversion with length validation.
- `convD2M9p1`/`convM2D9p1`: directory stat conversion.
- `convA2M9p1`, `convM2A9p1`, `convM2T9p1`: auth record conversion.
- `dumpsome`: prints data payload as printable text or hex.

Notable details:
- QTDIR is encoded in high bit of old qid path.
- 64-bit length/offset high words are skipped/zeroed where 9P1 only supports old widths.

Risks/quirks:
- Uses macros with direct byte pointer manipulation.
- Some string fields are copied fixed-width and may not be NUL-terminated.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/srvold9p/9p1lib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/srvold9p/fcall.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/srvold9p/fcall.c

Stream reassembler for old 9P1 messages.

Key responsibilities:
- Determines complete 9P1 message lengths from byte streams.
- Handles variable-length `Twrite9p1` and `Rread9p1` by reading count fields.
- Forks a process that reads from an old service fd, reassembles complete messages, and writes them to a pipe.

Important functions:
- `mntrpclen`: returns complete message length when enough bytes are buffered, zero otherwise.
- `fcall`: creates pipe, forks reassembler, and returns read end to caller.

Use case:
- Interposed for stream transports where old 9P1 messages may arrive fragmented or coalesced.

Risks/quirks:
- Illegal/unknown fixed-length message types are consumed as available bytes.
- Child closes fds 0..19 except needed descriptors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/srvold9p/fcall.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/srvold9p/srvold9p.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/srvold9p/srvold9p.c

Bridge from modern 9P2000 clients to old 9P1 servers.

Key responsibilities:
- Connects to an old 9P service by command, network, file, or stdio.
- Exposes a modern 9P endpoint, optionally posted in `/srv` and mounted.
- Converts 9P2000 requests into 9P1 calls and converts responses back.
- Tracks fids, old/new directory offsets, and outstanding tags for flush handling.

Important architecture:
- `serve`: reads modern 9P requests, dispatches via `fcalls`, and writes modern responses.
- `demux`: reads old 9P1 responses and rendezvous-delivers them by tag.
- `transact9p1`: send old request and wait for matching old response.
- `Tag` list tracks `flushed`, `received`, and refs.
- `Fid` list tracks busy/allocated state and directory offset translation.

Request handlers:
- `rversion`: local version negotiation.
- `rattach`, `rwalk`, `ropen`, `rcreate`, `rread`, `rwrite`, `rclunk`, `rremove`, `rstat`, `rwstat`.
- `dirrread`: converts fixed 9P1 directory records into variable 9P2000 stats.
- `rflush`: forwards flush and wakes blocked rendezvous if needed.

Risks/quirks:
- Authentication is explicitly unsupported in active path.
- Comment notes `demux` assumes one read per message unless paired with `fcall`.
- Directory seeks are disallowed because old/new directory record sizes differ.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/srvold9p/srvold9p.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/agent.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/agent.c

SSH1 agent forwarding implementation backed by Plan 9 factotum.

Key responsibilities:
- Requests agent forwarding from the SSH server.
- Maintains up to 16 forwarded agent channels.
- Reassembles agent protocol messages from SSH channel data.
- Lists RSA keys from `/mnt/factotum/ctl`.
- Answers RSA challenge requests by asking factotum to decrypt.

Important functions:
- `startagent`: sends `SSH_CMSG_AGENT_REQUEST_FORWARDING`.
- `handleagentmsg`: collects length-prefixed agent messages.
- `handlefullmsg`: handles identity listing and RSA challenge response.
- `dorsa`: factotum RSA decrypt path.
- `handleagentopen`, `handleagentieof`, `handleagentoclose`: channel lifecycle.

Security/data flow:
- Private keys remain in factotum; code sends challenges to factotum and returns MD5(challenge||session-id).
- Add/remove identity operations deliberately fail.

Risks/quirks:
- Static channel array limits concurrent forwarded channels.
- Agent message length controls allocation through `erealloc`.
- Some channel close paths are asymmetric and compatibility-oriented.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/agent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/authpasswd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/authpasswd.c

SSH1 client password authentication method.

Key responsibilities:
- Retrieves a password from factotum/auth helper using `auth_getuserpasswd`.
- Sends `SSH_CMSG_AUTH_PASSWORD`.
- Waits for success/failure.

Important function:
- `authpasswordfn`: full implementation.

Notable details:
- Interactive mode allows `auth_getkey`; noninteractive mode only uses available credentials.
- Exports `Auth authpassword`.

Risks/quirks:
- Password is passed in plaintext inside the already-encrypted SSH session.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/authpasswd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/authrsa.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/authrsa.c

SSH1 client RSA authentication method using factotum.

Key responsibilities:
- Starts factotum RSA client RPC.
- Iterates factotum-provided RSA moduli.
- Sends each public modulus in `SSH_CMSG_AUTH_RSA`.
- On challenge, asks factotum to decrypt, unpads RSA data, appends session id, MD5s it, and sends response.

Important function:
- `authrsafn`.

Data flow:
- Server challenge `mpint` -> factotum decrypt -> `rsaunpad` -> 32-byte right-justified value -> append `sessid` -> MD5 -> `SSH_CMSG_AUTH_RSA_RESPONSE`.

Risks/quirks:
- Continues to next key on several factotum/decode failures.
- Alloc size expression `16+(mpsignif(mod)+7/8)` appears precedence-sensitive and likely intends `(bits+7)/8`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/authrsa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/authsrvpasswd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/authsrvpasswd.c

SSH1 server password authentication handler.

Key responsibilities:
- Extracts password string from client message.
- Calls `auth_userpasswd` for the selected connection user.
- Exports `Authsrv authsrvpassword`.

Important details:
- First expected message is `SSH_CMSG_AUTH_PASSWORD`.
- Frees the message after extracting password pointer.

Risks/quirks:
- Relies on `getstring` returning storage valid through auth call before message free implications.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/authsrvpasswd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/authsrvtis.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/authsrvtis.c

SSH1 server TIS/challenge-response authentication handler.

Key responsibilities:
- Starts Plan 9 `p9cr` challenge through auth server.
- Sends SSH TIS challenge string to client.
- Receives `SSH_CMSG_AUTH_TIS_RESPONSE`.
- Validates response with `auth_response`.

Important function:
- `authsrvtisfn`.

Notable details:
- If client switches auth protocols instead of responding, message is pushed back with `unrecvmsg`.
- Logs auth challenge failures.

Risks/quirks:
- Challenge string format is user-facing and includes `Challenge:`/`Response:`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/authsrvtis.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/authtis.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/authtis.c

SSH1 client TIS/challenge-response authentication method.

Key responsibilities:
- Sends `SSH_CMSG_AUTH_TIS`.
- Reads challenge from server.
- Prompts on `/dev/cons`.
- Sends response and waits for success/failure.

Important function:
- `authtisfn`.

Risks/quirks:
- Only works in interactive mode.
- Response buffer is fixed at 256 bytes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/authtis.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/cipher3des.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/cipher3des.c

SSH1 3DES cipher adapter.

Key responsibilities:
- Initializes three DES states from the 32-byte SSH1 session key.
- Implements encrypt-decrypt-encrypt 3DES CBC and reverse decrypt path.
- Exports `Cipher cipher3des`.

Risks/quirks:
- Uses first 24 bytes of `sesskey`.
- Separate encryption/decryption states are initialized with same key material and implicit IV behavior from libsec.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/cipher3des.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/cipherblowfish.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/cipherblowfish.c

SSH1 Blowfish cipher adapter.

Key responsibilities:
- Initializes Blowfish CBC state from full SSH1 session key.
- Provides encrypt/decrypt callbacks.
- Exports `Cipher cipherblowfish`.

Risks/quirks:
- Uses libsec `BFstate` with nil IV.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/cipherblowfish.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/cipherdes.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/cipherdes.c

SSH1 DES cipher adapter.

Key responsibilities:
- Initializes DES CBC state from session key.
- Provides encrypt/decrypt callbacks.
- Exports `Cipher cipherdes`.

Risks/quirks:
- DES is legacy/weak; included for SSH1 compatibility.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/cipherdes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/ciphernone.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/ciphernone.c

SSH1 no-encryption cipher adapter.

Key responsibilities:
- Provides no-op encrypt/decrypt callbacks.
- Returns a non-nil sentinel state.
- Exports `Cipher ciphernone`.

Use:
- Compatibility/debugging cipher, not safe for normal use.

Risks/quirks:
- Deliberately disables confidentiality when negotiated.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/ciphernone.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/cipherrc4.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/cipherrc4.c

SSH1 RC4 cipher adapter.

Key responsibilities:
- Splits session key into client-to-server and server-to-client RC4 keys.
- Direction depends on whether initialized as server or client.
- Provides symmetric stream encrypt/decrypt callbacks.
- Exports `Cipher cipherrc4`.

Risks/quirks:
- RC4 is legacy/weak but present for SSH1 compatibility.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/cipherrc4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/ciphertwiddle.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/ciphertwiddle.c

Debug cipher for SSH1.

Key responsibilities:
- Prints the session key.
- XORs every byte with `0xFF` for both encrypt and decrypt.
- Exports `Cipher ciphertwiddle`.

Use:
- Debugging only.

Risks/quirks:
- Not cryptographically meaningful and leaks key material to stderr.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/ciphertwiddle.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/cmsg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/cmsg.c

SSH1 client handshake, key verification, and pty request logic.

Key responsibilities:
- Reads server SSH1 identification string.
- Receives server public key packet.
- Checks host key against system and user keyrings.
- Chooses cipher, generates session key, computes session id, and sends encrypted session key.
- Authenticates user using configured auth methods.
- Requests pty and sends window-size changes.

Important functions:
- `sshclienthandshake`: full client protocol setup.
- `checkkey`: host key trust-on-first-use/system keyring enforcement.
- `send_ssh_cmsg_session_key`: double-RSA-encrypts SSH1 session key.
- `authuser`: tries supported auth methods in order.
- `requestpty`, `readgeom`, `sendwindowsize`.

Risks/quirks:
- SSH1 requires server and host RSA keys to differ by at least 128 bits.
- Interactive key mismatch prompts can allow continue/replace.
- Session key is generated with `fastrand`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/cmsg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/msg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/msg.c

SSH1 packet framing, encoding, decoding, CRC, and RSA padding utilities.

Key responsibilities:
- Allocates and sends SSH1 packets with padding, type byte, payload, and CRC32.
- Receives packets, decrypts, validates CRC, and skips DEBUG/IGNORE messages.
- Provides typed getters/setters for bytes, shorts, longs, strings, byte arrays, mpints, and RSA public keys.
- Implements SSH1-style RSA PKCS#1-like padding/unpadding helpers.

Important functions:
- `allocmsg`, `sendmsg`, `recvmsg`.
- `getstring`, `putstring`, `getmpint`, `putmpint`, `getRSApub`, `putRSApub`.
- `sum32`/`initsum32`: CRC table and calculation.
- `rsapad`, `rsaunpad`, `mptoberjust`, `rsaencryptbuf`.

Risks/quirks:
- Packet size hard limit is 256 KiB.
- Uses CRC32, not a MAC, reflecting SSH1 design.
- `rsaunpad` calls `error` on malformed padding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/msg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/pubkey.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/pubkey.c

SSH1 host public-key file parser and updater.

Key responsibilities:
- Parses SSH1 public-key records in decimal or hex forms, with optional host aliases.
- Searches keyring files for matching host aliases.
- Detects key match, missing key, missing key file, or wrong key.
- Appends or replaces host key entries.

Important functions:
- `readpublickey`, `parsepubkey`: parse public key lines.
- `match`: compare comma-separated host alias lists.
- `findkey`: lookup host key.
- `appendkey`, `replacekey`: update keyring files.

Risks/quirks:
- `parsepubkey` temporarily mutates input line while parsing.
- `replacekey` rewrites through `<keyfile>.new`, removes old file, then renames by `dirwstat`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/pubkey.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/scp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/scp.c

Plan 9 SCP implementation using classic scp source/sink protocol over `/bin/ssh`.

Key responsibilities:
- Copies local-to-local, local-to-remote, remote-to-local, and remote-to-remote paths.
- Implements remote source mode (`-f`) and sink mode (`-t`).
- Preserves mode and times with `-p`.
- Recursively copies directories with `-r`.
- Spawns `/bin/ssh` to run remote `scp`.

Important functions:
- `destislocal`, `destisremote`: choose transfer direction.
- `send`, `senddir`: emit SCP protocol records and file data.
- `receive`, `receivedir`: parse SCP protocol records and create files/directories.
- `getresponse`, `sendokresponse`: protocol acknowledgments.
- `remotessh`: fork/exec ssh and connect stdio via pipe.
- `fileaftercolon`: detects `host:path`.

Risks/quirks:
- Uses shell command strings for local `cp` and remote-to-remote cases.
- Fixed buffers for paths and protocol headers.
- Sends filler bytes if local read fails after committing file size.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/scp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/smsg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/smsg.c

SSH1 server handshake and authentication logic.

Key responsibilities:
- Loads SSH server host key from factotum.
- Generates ephemeral server RSA key.
- Sends SSH1 public-key packet and receives encrypted session key.
- Decrypts session key using server private key and factotum host key RPC.
- Authenticates user via configured server auth methods.
- Switches process credentials with `auth_chuid`.

Important functions:
- `sshserverhandshake`: full server-side setup.
- `send_ssh_smsg_public_key`: advertises keys, ciphers, auth methods.
- `recv_ssh_cmsg_session_key`: decrypts and unmunges session key.
- `authsrvuser`: drives user/auth method loop.
- `responselogin`, `authusername`: p9cr helper path.

Risks/quirks:
- Server ephemeral key is 768 bits in `sshserve.c`.
- Host key private operation is delegated through factotum RPC.
- Uses SSH1 protocol assumptions and weak legacy algorithms.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/smsg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/ssh.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/ssh.h

Shared header for Plan 9 SSH1 client/server tools.

Key responsibilities:
- Defines SSH1 packet type numbers, protocol flags, agent packet types, cipher IDs, auth method IDs, and constants.
- Defines core structs: `Auth`, `Authsrv`, `Cipher`, opaque `CipherState`, `Conn`, and `Msg`.
- Declares all shared APIs across message, handshake, auth, cipher, keyring, agent, and utility modules.

Important structures:
- `Conn`: carries fds, cipher state, cookies/session ids/session key, keys, auth/cipher preference lists, user/host aliases, server private keys, and unget message.
- `Msg`: packet buffer with read/write pointers and optional link for sshnet queues.

Risks/quirks:
- SSH1 protocol is inherently legacy and pre-MAC.
- Header exposes many global modules and extern variables.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/ssh.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/ssh1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/ssh1.c

Interactive SSH1 client command.

Key responsibilities:
- Parses cipher/auth/user/pty/interactive/raw/agent-forwarding options.
- Dials remote SSH port.
- Performs SSH1 client handshake and authentication.
- Optionally requests agent forwarding and pty.
- Runs remote command or shell.
- Copies stdin to SSH and SSH stdout/stderr back to local fds.
- Supports console raw mode, escape menu, window-size updates, and local shell escape.

Important functions:
- `main`: connection setup and command dispatch.
- `fromnet`: handles server output, exit status, disconnects, and agent channel messages.
- `fromstdin`: forked input loop sending stdin data/EOF.
- `menu`: handles escape commands.
- `system`: runs local command connected to remote stdin.
- `winchanges`: sends window-size updates.

Risks/quirks:
- Escape menu triggers on control-`\` byte.
- Agent forwarding assumes agent channels are the only channel traffic.
- Uses `/bin/rc` for local shell escape.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/ssh1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/sshnet.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/sshnet.c

SSH1-backed synthetic `/net`-style filesystem for remote TCP forwarding.

Key responsibilities:
- Authenticates an SSH1 session and starts a remote shell to enable port-open channels.
- Mounts a lib9p filesystem exposing `/`, `cs`, `tcp`, `tcp/clone`, and per-connection `ctl`, `data`, `local`, `remote`, `status`.
- Maps Plan 9 network control writes to SSH1 `SSH_MSG_PORT_OPEN`.
- Maps reads/writes on `data` to SSH channel data.
- Translates `cs` lookups into mount-local `/net` clone paths.

Important architecture:
- `threadmain`: parses options, connects, handshakes, starts fs threads, mounts service.
- `sshreadproc`: reads SSH messages into `sshmsgchan`.
- `fsnetproc`: serializes filesystem requests, clunks, and SSH messages.
- `Client`: tracks refcount, local num, remote channel num, state, pending read requests, and queued messages.

Key filesystem handlers:
- `fswalk1`, `fsopen`, `fsread`, `fswrite`, `fsflush`, `fsdestroyfid`.
- `ctlwrite`: handles `connect host!port` and `hangup`.
- `dataread`/`datawrite`: queue reads and send channel data.
- `handlemsg`: handles channel data, EOF/close, open confirmation/failure.

Risks/quirks:
- Single serialized fs thread avoids many races but requires explicit wait channels.
- `statusread` builds a local address buffer but returns only state string.
- Uses SSH1 port-forward messages and assumes remote support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/sshnet.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/sshserve.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/sshserve.c

SSH1 server command.

Key responsibilities:
- Parses server cipher/auth options and client address.
- Generates ephemeral server RSA key.
- Performs SSH1 server handshake and authentication.
- Accepts pty/options/exec-shell/exec-command messages.
- Starts local shell command or telnetd session and bridges stdio over SSH packets.
- Sends exit status or disconnect.

Important functions:
- `main`: setup and handshake.
- `fromnet`: pre-exec option handling, then stdin channel loop.
- `startcmd`: forks command environment and starts stdout/stderr copyout processes.
- `copyout`: sends local fd output as SSH stdout/stderr data.

Notable behavior:
- Shell mode runs `/bin/ip/telnetd -tn`; command mode runs `/bin/rc -lc cmd`.
- Sets `user`, `sysname`, `tz`, and `service` environment variables for child.

Risks/quirks:
- Default server auth list is `tis`.
- Ephemeral RSA key is generated with 768 bits.
- Some unsupported client messages receive generic failure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/sshserve.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/util.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/util.c

Shared utilities for SSH1 tools.

Key responsibilities:
- Error/debug output and zeroing allocation wrappers.
- Process cleanup via registered kill list.
- Reads newline-terminated SSH identification strings.
- Computes SSH1 session id from host/server public moduli and cookie.
- Writes syslog entries.
- Builds host alias list from ndb/dns.
- Rebinds terminal factotum when needed.

Important functions:
- `error`, `debug`, `emalloc`, `erealloc`.
- `atexitkill`, `atexitkiller`.
- `readstrnl`, `calcsessid`.
- `setaliases`, `privatefactotum`.

Risks/quirks:
- `sshlog` calls `va_start`/`va_end` before using `fmtvprint`, which is suspicious in modern C terms.
- `trim` sorts and deduplicates aliases by mutating tokenized string.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh1/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/cipher3des.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/cipher3des.c

SSH2 3DES-CBC cipher adapter.

Key responsibilities:
- Initializes `DES3state` from negotiated server-to-client or client-to-server keys and IVs.
- Provides CBC encrypt/decrypt callbacks.
- Exports `Cipher cipher3des` named `3des-cbc` with 8-byte block size.

Dependencies:
- Uses `netssh.h` connection fields `s2cek`, `c2sek`, `s2civ`, and `c2siv`.
- Allocates with `emalloc9p`.

Risks/quirks:
- Legacy cipher retained for protocol compatibility.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/cipher3des.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/cipheraes.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/cipheraes.c

SSH2 AES-CBC cipher adapters.

Key responsibilities:
- Implements shared AES initialization for 128/192/256-bit keys.
- Provides CBC encrypt/decrypt callbacks.
- Exports `aes128-cbc`, `aes192-cbc`, and `aes256-cbc` `Cipher` objects.

Important details:
- Uses a global `QLock aeslock` around AES setup/encrypt/decrypt.
- Selects key/IV direction from `dir`.
- Guards encrypt/decrypt with checks on `AESstate.setup` and rounds.

Risks/quirks:
- If AES state validation fails, encrypt/decrypt silently returns without transforming data.
- Global lock serializes all AES operations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/cipheraes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/cipherblowfish.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/cipherblowfish.c

SSH2 Blowfish-CBC cipher adapter.

Key responsibilities:
- Initializes Blowfish state from negotiated directional key/IV.
- Provides CBC encrypt/decrypt callbacks.
- Exports `Cipher cipherblowfish` named `blowfish-cbc`.

Notable details:
- Prints key/IV material when `debug > 1`.
- Also prints cipher-state pointer and first bytes before/after decrypt unconditionally in current code.

Risks/quirks:
- Unconditional debug `fprint` in init/decrypt leaks runtime internals and plaintext/ciphertext bytes.
- Blowfish-CBC is legacy compatibility code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/cipherblowfish.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/cipherrc4.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/cipherrc4.c

SSH2 RC4/arcfour cipher adapter.

Key responsibilities:
- Initializes RC4 state from negotiated directional key.
- Provides stream encrypt/decrypt callbacks using the same RC4 operation.
- Exports `Cipher cipherrc4` named `arcfour`.

Risks/quirks:
- RC4/arcfour is legacy and cryptographically weak.
- Declares block size as 8 in `Cipher`, likely fitting surrounding packet code expectations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/cipherrc4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/common.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/common.c

Small SSH2 utility module.

Key responsibilities:
- `freeptr`: frees a pointed-to pointer and sets it to nil.
- `readfile`: reads up to `size-1` bytes from a file into a NUL-terminated buffer.

Risks/quirks:
- `freeptr` accepts `void **` but casts to `char **`; intended for pointer cleanup rather than typed ownership.
- `readfile` returns `-1` on open failure and leaves caller's buffer unchanged in that case.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ssh2/common.c -->