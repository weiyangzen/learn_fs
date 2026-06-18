<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/features/Features.cc -->
# sources/distributed-fs/eos/mgm/features/Features.cc

## Purpose

`Features.cc` defines the static MGM feature advertisement map declared in `Features.hh`. These values describe client-visible EOS behavior such as path encoding, lazy open support, and the inode encoding scheme.

## Important APIs, Types, and Functions

The only function is file-local `checkInodeScheme()`, which reads `EOS_USE_NEW_INODES` and returns `"1"` only when the first environment character is `1`; otherwise it returns `"0"`. `Features::sMap` contains `eos.encodepath=curl`, `eos.lazyopen=true`, and `eos.inodeencodingscheme=<env-derived value>`.

## Control Flow

Control flow runs during static initialization. `checkInodeScheme()` is evaluated while initializing `Features::sMap`, so later environment changes do not alter this process's advertised inode scheme.

## State and Persistence Behavior

The state is a process-global `const std::map`. It persists for the MGM process lifetime and is not written to disk. Its only dynamic input is the environment at static initialization time.

## Dependencies and Integration Points

The implementation depends on `mgm/features/Features.hh` and `getenv()` from the C runtime. Consumers of `Features::sMap` can expose or negotiate feature values with clients or management interfaces.

## Risks and Edge Cases

Static initialization order matters if other globals read `Features::sMap` very early. The environment is sampled once and without validation beyond the first byte. The source banner says `File: ZMQ.hh` in the paired header, which is misleading but not behavioral.

## Test Signals

Tests should start a process with `EOS_USE_NEW_INODES=1`, unset, and other values, then check `eos.inodeencodingscheme`. Compile/link coverage should ensure there is exactly one definition of `Features::sMap`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/features/Features.cc -->
