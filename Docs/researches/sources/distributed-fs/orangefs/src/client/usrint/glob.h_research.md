# sources/distributed-fs/orangefs/src/client/usrint/glob.h

## Purpose
`glob.h` is the public compatibility header for the bundled glob implementation. It defines the POSIX and GNU glob flags, result structures, status codes, and function prototypes used by OrangeFS usrint builds, including large-file variants when enabled.

## Important APIs, Types, And Constants
The main type is `glob_t`, containing `gl_pathc`, `gl_pathv`, `gl_offs`, `gl_flags`, and optional alternate directory functions. Under large-file support it also defines `glob64_t` with `struct dirent64`/`struct stat64` callback signatures. User flags include POSIX options (`GLOB_ERR`, `GLOB_MARK`, `GLOB_NOSORT`, `GLOB_DOOFFS`, `GLOB_NOCHECK`, `GLOB_APPEND`, `GLOB_NOESCAPE`, `GLOB_PERIOD`) and GNU/BSD extensions (`GLOB_MAGCHAR`, `GLOB_ALTDIRFUNC`, `GLOB_BRACE`, `GLOB_NOMAGIC`, `GLOB_TILDE`, `GLOB_ONLYDIR`, `GLOB_TILDE_CHECK`). Return codes are `GLOB_NOSPACE`, `GLOB_ABORTED`, `GLOB_NOMATCH`, and `GLOB_NOSYS`, with `GLOB_ABEND` as a GNU compatibility alias.

## Control Flow Contract
Callers pass a pattern, flags, optional error callback, and `glob_t` to `glob`; results are returned in `gl_pathv` with `gl_pathc` entries after any `gl_offs` reserved null slots. `GLOB_APPEND` allows multiple calls to accumulate results, and `globfree` releases allocations. `glob_pattern_p` is a GNU helper for checking whether a pattern contains unquoted metacharacters.

## State And Persistence Behavior
The header describes caller-owned result state but no persistent storage. The callback fields become active only when `GLOB_ALTDIRFUNC` is set; otherwise the implementation ignores them. The structure layout is ABI-sensitive because callers allocate `glob_t`.

## Dependencies And Integration Points
The header includes `<sys/cdefs.h>` and defines `__size_t`/`size_t` compatibly with feature macros. GNU feature macros control visibility of `struct stat`-typed callbacks and the `glob_pattern_p` extension. `_FILE_OFFSET_BITS=64` builds redirect `glob` and `globfree` to `glob64`/`globfree64`, while `__USE_LARGEFILE64` exposes explicit 64-bit APIs.

## Risks
Feature-macro-dependent typedefs and callback signatures can differ between compilation units if they include the header under different macro sets. Alternate directory callbacks must conform to the visible signature, especially with GNU vs non-GNU dirent/stat types. Redirected large-file prototypes need to match the compiled implementation, or callers may link against missing `glob64` symbols.

## Test Signals
Compile tests should cover POSIX-only, GNU, BSD, and large-file macro configurations. ABI tests should confirm `glob_t` layout and callback field offsets are stable for the usrint build. Runtime tests should pair this header with `glob.c` and exercise every flag exposed in `__GLOB_FLAGS`, including `GLOB_ALTDIRFUNC` and large-file redirects when enabled.
