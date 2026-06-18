<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Redirect.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Redirect.cc

Source read size: 111 lines, 4031 bytes.

## Purpose

Implements an fsctl helper that returns the open redirect URL for a path without performing data transfer. It is used by clients that need to discover the target FST for read or write/open-create operations.

## Important APIs, Types, and Functions

The function is `XrdMgmOfs::Redirect(...)`. It parses `eos.client.openflags` and `eos.client.openmode`, constructs XRootD `SFS_O_*` flags, applies read or write access macros, opens through `XrdMgmOfsFile`, and rewrites the redirect URL with `:<port>/<path>?`.

## Control Flow

The handler records `OpenRedirect`, builds a file object, maps textual flags (`wo`, `rw`, `cr`, `tr`) to open bits, chooses write access when create/rw/truncate is requested and read access otherwise, calls `file->open`, and returns `SFS_DATA` only for `SFS_REDIRECT`. Redirect text is patched to include `file->error.getErrInfo()` and the requested path; failures return the file error text and code.

## State and Persistence Behavior

Potential durable side effects depend on open flags: create and truncate can mutate namespace/file state through `XrdMgmOfsFile::open`. The local file object is temporary.

## Dependencies and Integration Points

Depends on `XrdMgmOfsFile`, access/stall/redirect macros, XRootD open flag semantics, and client opaque fields.

## Risks and Edge Cases

`eos.client.openmode` is read when `eos.client.openflags` exists; a missing mode yields octal parse of an empty string. The string replacement assumes the redirect text contains `?`; if not, `emsg.find("?")` can produce an invalid replace position. Flag substring matching can misinterpret unexpected flag text.

## Test Signals

Test read-only redirect, create/write/truncate redirects, missing or malformed open mode, failed opens, redirect text without `?`, permission failures, and path strings needing URL escaping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Redirect.cc -->
