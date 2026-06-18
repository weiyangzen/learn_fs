# sources/distributed-fs/coda/coda-src/util/histo.h

## Purpose
Declares histogram data structures and functions for linear and logarithmic distributions.

## Important APIs, Types, And Functions
`enum htype` defines `LINEAR`, `LOG2`, and `LOG10`. `struct histo` stores one bucket range and count. `struct hgram` stores buckets, underflow/overflow buckets, counts, and sums. Public functions initialize, clear, update, print, and plot.

## Control Flow
Callers allocate an `hgram`, call `InitHisto()`, update with samples, and print or plot the collected distribution.

## State And Persistence
State is caller-owned and heap-backed through the `buckets` pointer. No persistence is implied.

## Dependencies And Integration Points
Macros require `pow()` from libm in users of the header. The implementation links with math functions.

## Risks
The header does not expose a destructor/free API for bucket storage. `char *` plot labels are mutable in the prototype even though callers may pass literals.

## Test Signals
Compile with libm, verify all public functions, and check memory ownership conventions in callers.
