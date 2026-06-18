# sources/distributed-fs/openafs/src/tools/dumpscan/xf_profile.c

## Purpose
Implements an `XFILE` wrapper that records read/write/seek/tell/skip activity to a separate profile stream while forwarding operations to an underlying content stream. This is diagnostic instrumentation for dumpscan I/O behavior.

## Important APIs, Types, And Functions
The public open functions are `xfopen_profile` and `xfon_profile`. Internal `PFILE` holds two nested `XFILE`s: `content` and `profile`. Backend methods are `xf_PROFILE_do_read`, `xf_PROFILE_do_write`, `xf_PROFILE_do_tell`, `xf_PROFILE_do_seek`, `xf_PROFILE_do_skip`, and `xf_PROFILE_do_close`.

## Control Flow
`xfopen_profile` allocates a `PFILE`, opens the profile stream with `O_RDWR | O_CREAT | O_TRUNC`, opens the content stream with the caller's flags, installs wrapper methods, copies seekable/writable capability from the content stream, and writes an `OPEN` line. Each operation delegates to the content stream, logs operation name, byte count or offset, and result code to the profile stream, then returns the content result. `xfon_profile` parses `profile::xname` names, defaulting the profile stream to `-` when no profile name is provided.

## State And Persistence
Per-wrapper state is heap-allocated and freed on close. Persistent output is the profile file or stdout profile stream; persistent content effects are those of the wrapped `XFILE`. The wrapper has no global state and preserves the underlying stream capability flags.

## Dependencies And Integration Points
It depends on `xfiles.c` for recursive `xfopen`, on `xfprintf` for profile records, and on all backend types registered under the requested content/profile names. It is registered as the `PROFILE` type by `xfiles.c`.

## Risks And Test Signals
Profile logging errors are ignored in the operation wrappers, so profile loss may be silent. Closing a profile targeting `stdout` through `xfon_stdio` can close stdout. Tests should cover `PROFILE:file::FILE:data`, default profile output, nonseekable content behavior, delegation of error codes, close ordering, profile stream open failure cleanup, and nested profile wrappers.
