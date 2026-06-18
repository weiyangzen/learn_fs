# sources/distributed-fs/ceph-client/tools/memory-model/scripts/simpletest.sh

Purpose: Classifies a litmus test as simple enough for hardware translation by rejecting tests that use locking, RCU, or SRCU primitives.

Important APIs and functions: Command API is `simpletest.sh file.litmus`. It constructs one extended grep pattern covering `spin_lock`, `spin_unlock`, `spin_trylock`, `spin_is_locked`, RCU read-side and synchronize APIs, and SRCU variants.

Control flow: The script validates readability, runs grep for excluded primitives anchored after optional whitespace, exits 255 on a match, and exits 0 otherwise.

State and persistence behavior: Read-only; no persistent state.

Dependencies and integration points: Used by `runlitmus.sh` and `runlitmushist.sh` in hardware mode to avoid unsupported synchronization constructs.

Risks: It is lexical, so comments or unusual formatting can cause false positives or false negatives. New unsupported primitives require manually extending the pattern.

Test signals: Feed simple memory-access litmus files, lock/RCU/SRCU examples, commented primitives, and unreadable paths; verify exit status.
