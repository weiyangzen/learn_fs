# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/six.h

## Summary
Declares the six-lock interface, data structures, waiter representation, and initialization helpers for bcachefs shared/intent/exclusive locking.

## Main Contents
- `enum six_lock_type` with `SIX_LOCK_read`, `SIX_LOCK_intent`, and `SIX_LOCK_write`.
- `struct six_lock_waiter`, used both for sleeping and upper-layer cycle detection.
- `struct six_lock_wait_slot` and `struct six_lock_wait_fifo`, an RCU-replaceable stable-index wait array.
- `struct six_lock`, containing state, sequence number, reentrancy counters, owner, optional percpu readers, wait lock, wait FIFO, inline waiter storage, and optional lockdep map.
- `SIX_LOCK_INIT_PCPU` initialization flag.
- Inline wrappers for trylock, relock, and unlock variants.

## Important Behavior
The header documents six-lock semantics: intent is exclusive against intent but compatible with readers, and write is taken under intent. Sequence numbers let callers drop read/intent locks for blocking work and later relock if no writer intervened.

The waiter interface is intentionally exposed so a caller can embed `six_lock_waiter` in its own transaction/held-lock structures and walk wait lists for deadlock avoidance.

## Risks
The lock itself does not know which task owns read locks. Any reentrancy or self-deadlock avoidance involving read locks must be implemented by the upper layer. Lock waiters are externally visible, so users must preserve waiter lifetime until acquisition or abort completes.
