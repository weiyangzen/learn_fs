# Group Research: group_83_9front_sources_os_plan9_9front_sys_src_cmd_git_hist_sources_os_plan9__4e9b1a2cfb4b

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/hist -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/hist

- Purpose: rc wrapper that prints per-file history diffs for one or more repository paths.
- It initializes common git state with `/sys/lib/git/common.rc`, validates file arguments, and normalizes them relative to `$gitrel`.
- It runs `git/log -s` with optional `-n` count, then for each commit prints hash/date/author/message and a unified diff for each requested file.
- Parent content is found through `git/query $h~`; current and previous tree paths fall back to `/dev/null` when absent.
- Output is separated with `--`, a Plan 9 `⑨` patch separator, and blank lines, matching `git/import` patch batching.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/hist -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/import -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/import

- Purpose: imports mail-style or exported patch files into the current 9front git repository.
- `apply` parses headers/body/diff using awk, extracting author name/mail, date, subject/message, and patch body into environment/temp files.
- `apply1` dry-runs `patch -np1`, checks `git/walk -q` to avoid clobbering dirty files, applies with `patch -p1`, stages additions/removals, and optionally commits with `git/save`.
- It updates the active ref path directly after successful commit and appends tracked-file entries to `.git/INDEX9`.
- Supports `-n` no-commit mode, stdin patches, file arguments, and upas message directories with `header` and `body`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/import -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/init -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/init

- Purpose: initializes a Plan 9 git repository layout.
- Creates `.git/refs/heads`, `.git/refs/remotes`, `.git/fs`, `.git/objects`, empty `.git/INDEX9`, and `.git/HEAD`.
- Defaults branch to `front`, configurable with `-b`.
- Can set upstream with `-u`; otherwise derives `remote "origin".url` from `git/conf 'defaults "origin".baseurl'` plus directory basename.
- Writes `.git/config` with `repositoryformatversion = p9.0` and branch remote metadata.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/init -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/log.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/log.c

- Purpose: implements `git/log`, printing commit history with optional path filtering and query expressions.
- `Pfilt` is a trie-like path filter; `filteradd`, `lookup`, and `matchesfilter1` compare commit trees against parent trees only along requested paths.
- `show` emits either short one-line logs (`hash first-message-line`) or detailed logs with hash, author, optional committer, formatted date, and indented message.
- `showquery` resolves explicit ref expressions via `resolverefs`; `showcommits` walks commit parents using `Objq` priority order and `Objset` de-duplication.
- CLI supports `-s` short output, `-n` count, `-e expr`, `-c commit`, and optional path filters normalized from current working directory to repo root.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/merge -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/merge

- Purpose: rc wrapper for three-way merge against a target commit/ref.
- Resolves `theirs`, `ours` (`HEAD`), and merge base using `git/query $theirs ^ ' ' ^ $ours ^ '@'`.
- Refuses no-op merges and dirty worktrees (`git/walk -q`).
- Fast-forward case updates `.git/refs/<branch>` and runs `git/revert .`.
- Non-fast-forward records parents in `.git/merge-parents`, computes changed path union with `git/query -c`, and calls `merge1` for each file.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/merge -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/objset.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/objset.c

- Purpose: small open-addressed hash set for `Object*`, keyed by SHA-1 hash.
- `osinit` starts at 16 slots; `osadd` probes by big-endian first 32 bits of hash and doubles when load exceeds 50%.
- `osfind` returns an object matching a `Hash`; `oshas` wraps existence checks.
- Used throughout git traversal, object cache, ancestry painting, packing, and duplicate suppression.
- Ownership is shallow: `osclear` frees only the table, not objects.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/objset.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/ols.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/ols.c

- Purpose: object-list iterator over loose and packed git objects.
- `mkols` snapshots `.git/objects` and `.git/objects/pack`; `olsfree` closes active fd and frees directory arrays.
- Loose iteration scans two-hex-digit directories, concatenates directory and filename, and parses hashes.
- Packed iteration scans `.idx` files and reads the fanout count plus hash table entries.
- `olsnext` yields loose objects first, then packed objects, preserving iterator state across calls.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/ols.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/pack.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/pack.c

- Purpose: core object storage, packfile reading/indexing/writing, object cache, commit/tree parsing, and pack generation.
- Object cache: `readobject`, `cache`, `ref`, `unref`, and `clear` maintain a SHA-indexed object cache plus LRU memory cap (`cachemax = 128 MiB`).
- Pack management: `refreshpacks`, `loadpack`, `openpack`, and `closepack` load `.idx` files, open `.pack` files lazily, and limit open pack fds.
- Object loading: supports loose zlib objects, packed base objects, offset deltas, ref deltas, thin-pack lookup, delta application, prefix expansion, and tree/commit/tag parsing.
- Indexing: `indexpack` validates pack header, iteratively resolves delta chains, computes object hashes/CRCs, and writes v2 `.idx` fanout/hash/crc/offset tables plus pack/index checksums.
- Pack writing: `readmeta` finds objects reachable from requested heads but not tails, `pickdeltas` selects bounded delta chains, and `genpack` writes pack v2 objects with zlib compression and final SHA-1.
- Tree parsing maps git modes to Plan 9 directory modes, handles submodules and symlinks specially, validates path components, and stores `Dirent` arrays.
- Commit parsing extracts tree, parents, author/committer names, timestamps with timezone adjustment, skips gpg/ssh signature blocks, and exposes message payload.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/pack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/proto.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/proto.c

- Purpose: git transport protocol support for pkt-line I/O and connection setup.
- Implements pkt-line `readpkt`, `writepkt`, `fmtpkt`, `flushpkt`, capability parsing, and debug tracing.
- URI handling supports local repos, ssh, git, hjgit/gits via `tlsclient`, and HTTP/HTTPS smart git through Plan 9 `/mnt/web`.
- HTTP transport has explicit read/write phases for info/refs discovery, POST request body, and response body.
- Local repositories are served by spawning `/bin/git/serve -w` and handshaking with `git-{upload,receive}-pack`.
- `closeconn` closes fds and waits for ssh/tls child transports.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/proto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/pull -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/pull

- Purpose: fetches from a remote and fast-forwards the local branch when possible.
- `update` advertises existing local heads/remotes to `git/get`, parses remote refs, and writes `.git/refs/remotes/<upstream>/...`.
- CLI supports debug, quiet, fetch-only, and upstream selection.
- If local commits exist and remote is unchanged, exits “up to date”; if histories diverge, prints ours/theirs/common and suggests `git/merge`.
- Fast-forward path prints short log unless quiet, then moves the local branch with `git/branch -mnb`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/pull -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/push -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/push

- Purpose: rc wrapper around `git/send` for pushing branches/removals.
- Supports push-all, branch selection, force, debug, remove, and upstream selection.
- Reads configured remote URLs from `git/conf -a 'remote "<upstream>".url'`, falling back to upstream string as URL.
- Parses `git/send` result lines: `update`, `delete`, and `uptodate`.
- Mirrors successful remote branch updates into `.git/refs/remotes/<upstream>/...`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/push -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/query.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/query.c

- Purpose: resolves git ref expressions and optionally displays commit-to-commit tree changes.
- Builds query strings from argv, calls `resolverefs`, and prints hashes or `.git/fs/object/<hash>` paths with `-p`.
- `-c` prints tree differences between the first resolved commit and each later commit.
- Difference symbols: `+` added, `-` removed, `@` content changed, `!` mode/type changed; directories recurse.
- Handles reverse output with `-r` and debug with `-d`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/query.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/rebase -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/rebase

- Purpose: emits an rc command script to rebase a source branch onto a target commit.
- Resolves source branch, destination commit, and common ancestor.
- Refuses if destination is already the common ancestor.
- Uses `git/log -se dst..src` to enumerate commits, then prints commands to create `rebase.wip`, export each commit, and import it with optional `-n`.
- Finishes by moving the source branch to `rebase.wip` and removing the temporary branch.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/rebase -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/ref.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/ref.c

- Purpose: ref reading, ref-expression evaluation, ancestry/range computation, and ref listing.
- Expression parser uses an `Eval` stack over `Object*`; supports words, `^`/`~` parent, `@` LCA, and `:`/`..` range forms.
- `paint` performs colored priority traversal from heads and tails to compute LCA, “twixt” sets, or ordered ranges.
- `readref` resolves literal hashes, `HEAD`, refs under common prefixes, symbolic refs, and abbreviated hash prefixes.
- `resolveref` requires exactly one result; `resolverefs` returns all stack hashes.
- `listrefs` recursively scans `.git/refs`, resolving each file and returning parallel hash/name arrays.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/ref.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/repack.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/repack.c

- Purpose: repacks all refs into a single pack/index pair and removes old loose/pack objects.
- Lists refs with `listrefs`, writes temporary pack via `writepack`, indexes it with `indexpack`, then renames to `<packhash>.pack` and `<packhash>.idx`.
- `cleanup` removes all loose object files and all older pack directory entries except the newly produced prefix.
- Uses `.git/objects/pack/repack.{pack.tmp,idx.tmp}` temporary paths.
- Debug option increments `chattygit`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/repack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/revert -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/revert

- Purpose: restores specified files from a commit/query into the working tree.
- Defaults query to `HEAD`; `-c query` selects another commit-like expression.
- Uses `git/walk -c -fRM -b <query>` to find removed/modified paths relative to the selected tree.
- Copies each file from `$commit/tree/<path>`, preserves timestamp touch, and stages it with `git/add`.
- Normalizes arguments relative to `$gitrel` and drops `$gitroot`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/revert -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/rm -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/rm

- Purpose: compatibility wrapper for removal staging.
- Entire implementation is `exec git/add -r $*`.
- Delegates semantics to `git/add`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/rm -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/save.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/save.c

- Purpose: creates tree and commit objects from selected worktree paths and `.git/INDEX9`.
- Writes loose objects by constructing git object headers, SHA-1 hashing header+data, and zlib-deflating into `.git/objects/xx/yyyy...`.
- `treeify` recursively merges selected filesystem paths into the current HEAD tree, respecting index states, deletions, tracked files, submodules, and symlink restrictions.
- `blobify` writes file blobs; `writetree` sorts entries and writes tree objects with git modes.
- `mkcommit` writes commit objects with tree, parents, author/committer identity, date, and message.
- CLI requires message, author name/email, optional committer, date, and up to 16 parents; paths are normalized and sorted before tree construction.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/save.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/send.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/send.c

- Purpose: client-side receive-pack/push implementation.
- Builds requested local ref updates from selected branches, all refs, and deletions.
- Reads remote advertised refs/capabilities, maps local updates to remote current hashes, and records remote objects usable as pack tails.
- Refuses non-fast-forward updates unless `-f`; ancestry check uses `ancestor`.
- Sends update commands, writes pack via `writepack`, and parses optional report-status replies for unpack/update errors.
- CLI supports debug, force, remove branch, all refs, and branch selection; remote connection uses `gitconnect(..., "receive")`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/send.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/serve.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/serve.c

- Purpose: server-side `git-upload-pack` and `git-receive-pack` handler for 9front git.
- `showrefs` advertises HEAD symref and branch refs; upload negotiation reads `want`/`have` packets and writes ACK/NAK before `writepack`.
- Receive negotiation validates update triplets, ref names, write permissions, then reads the incoming pack to temp files.
- `checkhash`, `indexpack`, and rename logic verify and install received packs under `.git/objects/pack`.
- `updaterefs` locks repo, validates old hashes, updates/deletes refs, verifies new objects are commits, and may repair HEAD to newest pushed ref in empty repos.
- Main binds optional path prefix, binds requested repo as `/`, initializes git, then dispatches upload or receive; writes require `-w`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/serve.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/util.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/util.c

- Purpose: shared git utility functions, formatting, allocation, queueing, path/ref helpers, and repository initialization.
- Installs `%H`, `%T`, `%O`, `%Q` formatters; initializes inflate/deflate, author regex, object cache, and repository directory mode.
- Provides checked allocation helpers, hash parsing/comparison, suffix helpers, whitespace stripping, qid parsing, and MurmurHash2.
- `findrepo` walks ancestors looking for `.git/HEAD`; `gitinit` optionally returns repo root and relative depth.
- `Objq` is a commit priority queue ordered by commit time, used for history/ancestry traversals.
- `okref` implements git ref-name validity rules excluding higher-level HEAD/refs prefix policy.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/walk.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/git/walk.c

- Purpose: worktree status scanner and `.git/INDEX9` maintenance tool.
- Compares indexed entries, mounted git/fs tree content, and actual working directory entries to classify Removed, Modified, Added, Untracked, and Tracked.
- Uses qid/mode fast path when possible; falls back to byte-by-byte comparison against `.git/fs/HEAD/tree` or selected base tree.
- Handles stale or missing index by rebuilding tracked state from mounted git/fs tree; can invalidate index with `-I`.
- Path filtering normalizes args to repo-relative paths and carefully handles directory-prefix matching.
- Writes refreshed `.git/INDEX9` when stale, excluding `U` entries and collapsing duplicate path entries.
- Exit status encodes dirty classes using letters from `RMAUT`; quiet mode still sets status.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/git/walk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/coord.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/grap/coord.c

- Purpose: coordinate-system state for the `grap` preprocessor.
- Tracks default/current coordinate names, explicit x/y ranges, log flags, and count of coordinate declarations.
- `coord_x`/`coord_y` store requested min/max pairs and suppress graph margin expansion.
- `coord` applies pending range/log flags to an `Obj`, validates positive log lower bounds, resets pending flags, and disables automatic x numbering.
- Multiple implicit default coordinates are renamed `ggN` to avoid clobbering the original default.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/coord.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/for.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/grap/for.c

- Purpose: implements `for` loops and `if` expansion in grap input.
- Maintains a fixed stack of loop frames containing variable, bound, step operator/value, and saved body string.
- `forloop` initializes variable and pushes loop body back onto the input stream with an `Endfor` marker.
- `endfor` updates the loop variable by `+`, `-`, `*`, or `/` and schedules the next iteration.
- `ifstat` pushes either then or else source strings based on numeric/string expression truth.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/for.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/frame.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/grap/frame.c

- Purpose: emits pic code for graph frames and customizable sides.
- Stores frame height/width and up to four side overrides.
- `frame` writes `frameht`, `framewid`, and a `Frame` box; default is a visible box unless side descriptors are supplied.
- `frameside` maps TOP/BOT/LEFT/RIGHT to line definitions and applies line attributes through `desc_str`.
- A descriptor with no explicit side applies to all four sides recursively.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/frame.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/grap.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/grap/grap.h

- Purpose: central declarations for grap’s parser, lexer, renderer, symbol table, attributes, and global state.
- Defines input source types, graph constants, side/justification flags, coordinate flags, and default dimensions.
- Core structs: `Infile`, `Src`, `Arg`, `Point`, `Attr`, `Obj`, and parser `YYSTYPE`.
- Declares global parser/render state such as temp output, coordinate defaults, tick state, point size, margins, object list, and numeric buffers.
- Declares functions implemented across coordinate, input, label, plot, print, ticks, frame, misc, and parser support files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/grap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/grap.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/grap/grap.y

- Purpose: yacc grammar for the `grap` language embedded between `.G1` and `.G2`.
- Parses graph blocks, frames, ticks, grids, labels, coordinates, plots, lines/arrows, circles, raw pic snippets, draw/next paths, copy/thru, for loops, if statements, assignments, and print commands.
- Expression grammar supports arithmetic, comparisons, boolean operators, unary ops, log/exp/trig/sqrt/rand/min/max/int, variables, and string equality.
- Semantic actions call renderer/state helpers such as `frame`, `ticks`, `label`, `coord`, `plot`, `line`, `circle`, `drawdesc`, `next`, `copy`, `forloop`, and `ifstat`.
- Pattern supports multiple `graph` sections in one `.G1` block, finalizing previous graph output when a new graph begins.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/grap.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/input.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/grap/input.c

- Purpose: grap input stack, macro expansion, definition parsing, copy/thru handling, and error context.
- `pushsrc`/`popsrc` manage nested input sources: files, strings, macros, chars, thru markers, and free-on-pop strings.
- `definition`, `delimstr`, `dodef`, and `getarg` install and expand macro definitions with positional `$N` arguments.
- `input`/`nextchar` multiplex file, macro, string, char pushback, and thru-line expansion; file EOF unwinds included files.
- `do_thru` tokenizes a copied input line into macro arguments until `.G2` or an optional terminator string.
- Error reporting records recent input, prints context, then pushes a safety `\n.G2\n`.
- Also includes copy-file/copy-thru state and shell command construction helpers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/input.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/label.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/grap/label.c

- Purpose: label generation and text-size adjustment for grap.
- Tracks global point size, label movement offsets, and optional label width override.
- `label` emits pic label boxes around the frame according to side, estimating vertical label width from longest string.
- `lab_adjust` appends accumulated `(right,up)` adjustments for labels/ticks.
- `sizeit` wraps string values in troff `\s` size changes, considering explicit per-string size and global pointsize.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/label.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/grap/main.c

- Purpose: main driver for the grap preprocessor.
- Handles `-d` debug/tempfile behavior and `-l` library-include suppression.
- Reads stdin or files, copies ordinary input through, and parses `.G1` graph regions into pic `.PS`/`.PE` output.
- Maintains line directives (`.lf`) for diagnostics and downstream tools.
- Initializes defaults, signal handlers, temp file, and per-file input source stack.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/misc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/grap/misc.c

- Purpose: miscellaneous grap data structures and formatting helpers.
- Stores numeric lists, current string justification/size state, and symbol table entries.
- `lookup`, `getvar`, and `setvar` manage `Obj` names, variables, coordinate ranges, and pointsize side effects.
- Attribute helpers allocate, chain, free, stringify, and format string/numeric attributes.
- `range` and `halfrange` update coordinate bounds for plotted points and ticks when bounds are not explicit.
- `sprntf` implements limited numeric formatting for grap `sprintf`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/plot.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/grap/plot.c

- Purpose: plot primitives for grap output.
- Emits lines/arrows, circles/point glyphs, raw pic snippets, numeric-list plots, text plots, formatted numeric labels, and path continuation.
- `xyname` converts a `Point` into `xy_<coord>(x,y)`, applying log transforms and validating positive values.
- `numlist` supports automatic x values when only y values are supplied and uses coordinate attributes for path plotting.
- `drawdesc` sets style and optional symbol for named paths; `next` appends line segments between successive points.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/plot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/print.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/grap/print.c

- Purpose: final graph assembly and per-graph lifecycle.
- `print` computes margins, log transforms, auto tick state, coordinate scaling macros (`xy_`, `x_`, `y_`), frame, auto ticks, and buffered drawing commands.
- `graph` flushes a previous graph block and starts a new named pic block, requiring capitalized graph names.
- `setup` resets per-`.G1` state, opens temp output, initializes frame/tick defaults, and loads first-use definitions.
- `do_first` injects `pid` and optionally copies `/sys/lib/grap.defines`.
- `reset` preserves definitions/variables while freeing graph objects and restoring coordinate/tick defaults.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/print.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/ticks.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/grap/ticks.c

- Purpose: tick and grid generation for grap.
- Stores explicit tick values/labels, selected sides, disabled sides, grid style, tick direction, tick length, auto-tick sides, and log tick ratio.
- `ticks` updates auto-tick policy based on explicit tick/off/in/out directives.
- Auto-tick generation computes linear or logarithmic quantization and emits ticks for default coordinates.
- `iterator` creates tick lists from `from/to/by` expressions with arithmetic operators.
- `print_ticks` formats labels, applies log conversion when needed, updates coordinate half-ranges, and emits tick marks/labels for each side.
- `gridlist` reuses tick printing with full-frame grid lengths and line descriptors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grap/ticks.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/graph/graph.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/graph/graph.c

- Purpose: standalone numeric plotting program that emits Plan 9 plot commands through `iplot.h`.
- Parses options for labels, line mode, overlays, automatic x values, grid style, plot symbols, transpose, equal scales, breaks, axis limits/log axes, size/offset, and pen colors.
- Reads x/y data and optional labels from stdin, with overlay support and stored label string table.
- Computes axis limits, log/linear scaling, quantized marks, equal-scale expansion, and screen coordinate transforms.
- Draws axes/grid/ticks, title/axis range labels, and data paths/symbols in selected pen modes/colors.
- Uses 0..4096 plot coordinate range and default plot rectangle from `bot=200` to `top=4000`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/graph/graph.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/graph/iplot.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/graph/iplot.h

- Purpose: macro-based plotting API emitting textual plot commands.
- Defines wrappers such as `openpl`, `closepl`, `range`, `line`, `vec`, `move`, `text`, `pen`, `color`, `point`, splines, fills, boxes, circles, and save/restore.
- Most macros expand to `printf` commands with short operation mnemonics.
- Declares `putnum` for multi-point command bodies and `whoami`.
- Used by `graph.c`, `subr.c`, and `whoami.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/graph/iplot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/graph/subr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/graph/subr.c

- Purpose: helper for printing numeric arrays used by plot macros.
- `putnum` iterates over counted coordinate arrays and prints `{ x y ... }` blocks.
- Inserts a newline every other point pair.
- Supports the spline/poly/fill macros in `iplot.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/graph/subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/graph/whoami.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/graph/whoami.c

- Purpose: trivial identity function for the graph plotting backend.
- `whoami` returns the literal string `"general"`.
- Included to satisfy the `iplot.h` declaration/backend convention.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/graph/whoami.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grep/comp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/grep/comp.c

- Purpose: incremental DFA compiler and UTF/rune class expansion for Plan 9 grep.
- `increment` computes the next DFA state for a byte from a current state, de-duplicates states in a binary tree, and memoizes `s->next[c]`.
- `fol1` computes follow sets through regex nodes for byte `c`, handling alternation, anchors, case tables, end markers, and classes.
- `re2class` converts rune character-class ranges into byte-level regex fragments suitable for UTF-8 input scanning.
- Helper functions sort/merge rune ranges and split ranges by UTF-8 sequence length/pages.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grep/comp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grep/grep.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/grep/grep.h

- Purpose: shared definitions for the grep parser, compiler, and search engine.
- Defines regex node types (`Talt`, `Tbegin`, `Tcase`, `Tclass`, `Tend`, `Tor`), DFA state structure, regex fragment `Re2`, and regex node `Re`.
- Declares global flags/state, including input buffers, pattern source, follow set, parser output, state tree, and output buffer.
- Enumerates CLI/runtime flags and constants for allocation chunks, case optimization threshold, beginning sentinel, and flush cadence.
- Declares regex construction, compilation, search, lexer/parser, and debug-print helpers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grep/grep.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grep/grep.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/grep/grep.y

- Purpose: yacc grammar and lexer for grep regular expressions.
- Grammar supports alternation, concatenation, `*`, `+`, `?`, grouping, anchors, dot, classes, escaped characters, and newline-separated alternative patterns.
- Wraps compiled expression so matching can occur anywhere in a line and terminates with `Tend`.
- Lexer reads either pattern string or `-f` pattern file, performs optional case folding, parses character classes including negation, and handles escaped newlines.
- `yyerror` reports pattern/file and line context then exits with syntax status.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grep/grep.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grep/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/grep/main.c

- Purpose: command-line grep driver and streaming search loop.
- Parses flags `bchiLlnsv`, `-e pattern`, and `-f patternfile`; multiple patterns are ORed by repeated `str2top`.
- Initializes follow set, initial DFA state, and buffered output.
- `search` reads files/stdin in large chunks, preserves previous line prefix across chunk boundaries, simulates a final newline for unterminated files, and runs normal or case-folded DFA scan.
- Supports count, filename prefixes, line numbers, list matching/non-matching files, status-only, inverse match, and unbuffered output.
- Exit status is success when any selected file matched.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grep/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grep/sub.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/grep/sub.c

- Purpose: regex allocation, AST optimization, pattern parsing entry, and regex fragment constructors.
- `mal` uses `sbrk` hunks for arena allocation; `sal` allocates DFA states; `ral` allocates regex nodes and tracks max follow size.
- `addcase` rewrites large OR character-class sets into `Tcase` byte dispatch tables.
- `str2top` parses a pattern and ORs it with any previous top-level regex.
- Fragment helpers concatenate, star, alternation, character ranges, and patch next pointers.
- Debug helpers recursively print regex nodes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/grep/sub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/arch.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/arch.h

- Purpose: Ghostscript architecture-selection header for Plan 9 build targets.
- Includes target-specific headers based on preprocessor symbols `T386`, `Tmips`, `Tspim`, `Tpower`, `Tpower64`, `Tarm`, `Tarm64`, or `Tamd64`.
- Unknown targets intentionally produce a compile-time error text requesting an arch.h update.
- Acts as a central switch for generated architecture parameter headers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/arch.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/contrib9.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/contrib9.mak

- Purpose: Ghostscript make fragment restoring contributed drivers not present in the current distribution.
- Defines Plan 9 bitmap device object and `.dev` target using `gdevplan9.c`.
- Defines HP cdj850-family driver objects and device targets (`cdj850`, `cdj670`, `cdj890`, `cdj1600`) using `gdevcd8.c` and PCL dependencies.
- Comments document provenance/contact notes for contributed drivers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/contrib9.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/default.386.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/default.386.h

- Purpose: generated Ghostscript architecture defaults for 386.
- Defines scalar alignments, log2 sizes, pointer size 4, float/double sizes, mantissa bits, unsigned max expressions, cache sizes, endian/signed-pointer/IEEE/arithmetic-shift flags.
- Little-endian, IEEE floats, signed pointer flag false, arithmetic right shift mode 2, full-long shift not supported.
- Cache defaults are 128 KiB L1 and 4 MiB L2.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/default.386.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/default.amd64.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/default.amd64.h

- Purpose: generated Ghostscript architecture defaults for amd64.
- Similar to 386 but pointer alignment/size are 8 and double alignment is 8.
- Little-endian, IEEE floats, arithmetic right shift mode 2, full-long shift not supported.
- Cache defaults are 128 KiB L1 and 4 MiB L2.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/default.amd64.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/default.arm.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/default.arm.h

- Purpose: generated Ghostscript architecture defaults for 32-bit ARM.
- Pointer size/alignment are 4; double size is 8; IEEE floats enabled.
- Little-endian, arithmetic right shift mode 2, full-long shift supported.
- Cache defaults are 1 MiB L1 and 1 MiB L2.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/default.arm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/default.arm64.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/default.arm64.h

- Purpose: generated Ghostscript architecture defaults for arm64.
- Pointer alignment/size are 8; struct alignment is 8; double alignment is 8.
- Little-endian, IEEE floats, arithmetic right shift mode 2, full-long shift supported.
- Cache defaults are 1 MiB L1 and 1 MiB L2.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/default.arm64.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/default.mips.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/default.mips.h

- Purpose: generated Ghostscript architecture defaults for MIPS.
- Pointer size/alignment are 4; IEEE floats enabled.
- Big-endian, arithmetic right shift mode 2, full-long shift not supported.
- Cache defaults are 4 KiB L1 and 512 KiB L2.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/default.mips.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/default.power.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/default.power.h

- Purpose: Ghostscript architecture defaults for 32-bit Power.
- Header notes it was copied from `default.mips.h` and not tested.
- Pointer size/alignment are 4; IEEE floats enabled.
- Big-endian, arithmetic right shift mode 2, full-long shift not supported.
- Cache defaults are 4 KiB L1 and 512 KiB L2.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/default.power.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/default.power64.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/default.power64.h

- Purpose: generated Ghostscript architecture defaults for 64-bit Power.
- Pointer alignment/size are 8; struct and double alignment are 8.
- Big-endian, IEEE floats, arithmetic right shift mode 2, full-long shift supported.
- Cache defaults are 1 MiB L1 and 1 MiB L2.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/default.power64.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/default.spim.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/default.spim.h

- Purpose: SPIM Ghostscript architecture defaults derived from MIPS defaults.
- Includes `default.mips.h`, then overrides endianness.
- Sets `ARCH_IS_BIG_ENDIAN` to `0`, making SPIM little-endian while inheriting other MIPS parameters.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/default.spim.h -->