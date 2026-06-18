# sources/distributed-fs/openafs/src/kauth/kpwvalid.c

## Purpose
Provides the default external password-quality checker used by `kpasswd` through the `kkids` child-process protocol.

## Important APIs, Types, And Functions
The only function is `main`. It includes component version metadata and uses two fixed 512-byte buffers for the old password and candidate passwords.

## Control Flow
The program reads the first stdin line as the old password, then loops over candidate new-password lines. For each candidate it accepts passwords whose line length is greater than eight characters, writes `0` to stdout, and returns status 0. Otherwise it writes an explanatory error to stderr, writes `1` to stdout, and returns status 1 if input ends after a rejection.

## State And Persistence
It stores only the old and candidate password lines in local buffers. It writes no files and persists no policy state.

## Dependencies And Integration Points
It is execed by `kkids.c` and communicates by newline-delimited stdin/stdout. `kpasswd.c` sends the old password first and expects integer decisions for subsequent candidates.

## Risks And Test Signals
Risks include the simplistic policy, newline-counting semantics where a visible eight-character password plus newline passes, unused old-password comparison, fixed-size input truncation by `fgets`, and protocol fragility if stderr/stdout are mixed by wrappers. Test signals include short, eight-character, longer, EOF, and truncated-line cases under the `kkids` pipe protocol.
