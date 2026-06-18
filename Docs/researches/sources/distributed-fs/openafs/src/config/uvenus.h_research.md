# sources/distributed-fs/openafs/src/config/uvenus.h

This file is not a usable header; it is a three-line notice stating that `uvenus.h` has been renamed to `venus.h` and that future changes should be made in `config/venus.h`.

There are no APIs, control flow, state, dependencies, or direct integration beyond acting as a migration marker for developers or stale include paths. The main risk is that a compiler including this file will see raw text, not comments, so it should not be on any active include path. Test signals are absence of source includes of `uvenus.h` and successful builds using `afs/venus.h` instead.
