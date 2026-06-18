<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/ProcCommand.cc -->
# sources/distributed-fs/eos/mgm/proc/ProcCommand.cc

Source read size: 723 lines, 21270 bytes.

## Purpose

Implements the legacy string/CGI-based MGM proc command dispatcher. It parses `/proc/admin` and `/proc/user` requests, invokes command-specific member functions, and formats stdout/stderr/return-code results for normal, FUSE, JSON, JSONP, and HTTP clients.

## Important APIs, Types, and Functions

Key methods are constructors/destructor, `OpenTemporaryOutputFiles`, `open`, `read`, `stat`, `close`, `MakeResult`, `KeyValToHttpTable`, and `CallJsonFormatter`. Dispatch targets include admin commands such as `archive`, `backup`, `geosched`, `monit`, `fusex`, `vid`, `rtlog`, `access`, `quota`, and user commands such as `accounting`, `archive`, `motd`, `version`, `who`, `fuse`, `fuseX`, `file`, `fileinfo`, `mkdir`, `rmdir`, `cd`, `chown`, `ls`, `rm`, `whoami`, `find`, `map`, `member`, `attr`, `chmod`, and `quota`.

## Control Flow

`open` stores request identity/path/info, identifies admin or user proc path, protects literal ampersands in opaque values, builds an `XrdOucEnv`, extracts command/subcommand/output-format/depth/selection/comment/callback/retc flags, resets output state, and dispatches to the appropriate command function. Unknown commands set `EINVAL` or `ENOTSUP`. Some commands return directly for special streaming behavior; otherwise `MakeResult` builds the response. `read` serves either file-backed result streams or in-memory `mResultStream` slices. `close` records privileged comments. `MakeResult` sorts stdout unless disabled, seals key/value output for default format, emits raw stdout for FUSE, renders simple HTTP/HTML output, or builds JSON/JSONP. File-backed results are spooled from temp stdout/stderr into a combined result stream.

## State and Persistence Behavior

Per-command state includes opaque env ownership, stdout/stderr/json strings, return code, temp files under `gOFS->TmpStorePath`, command flags, selection/depth/comment, and result length. Temporary files are removed in destructor or after spooling. Comments can persist in the MGM comment log for root/daemon/sudoer users.

## Dependencies and Integration Points

Depends on `XrdMgmOfs`, `XrdOucEnv`/tokenizer, `CommentLog`, namespace view/services, JSONCPP, command-specific member implementations in other files, and formatting helpers from `StringConversion`.

## Risks and Edge Cases

The ampersand repair heuristic depends on known prefixes and can still misparse unusual opaque values. Dispatch is a long string chain, making command names and format behavior easy to drift. HTTP output emits hand-built HTML and only sets a restrictive CSP when stderr is present. `read` assumes offsets fit `mLen`; file-backed reads rely on `FILE*` seek state. Destructor cleanup must match all early-return paths.

## Test Signals

Test admin/user command dispatch and unknown commands, literal ampersand handling, default/FUSE/HTTP/JSON/JSONP formatting, stdout sorting toggles, file-backed find-style output, `mgm.retc` open behavior, comment logging authorization, `read` offsets and EOF, and temp-file cleanup on success and failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/ProcCommand.cc -->
