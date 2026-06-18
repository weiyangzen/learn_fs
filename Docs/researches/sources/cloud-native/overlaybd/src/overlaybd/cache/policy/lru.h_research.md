<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/policy/lru.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/policy/lru.h

## Purpose
Provides a compact, generic LRU container optimized for cache eviction metadata.

## Important APIs, Types, And Functions
Template `FileSystem::LRU<ValueType, KeyType>` exports `push_front`, `access`, `mark_key_cleared`, `remove`, `pop_back`, `front`, `back`, `size`, and `empty`. Internal `Record` stores prev/next links plus value in a vector-backed ring.

## Control Flow
Construction creates a dummy list head. New entries allocate from a free ring or append to the vector, then become most-recent. `access` moves an entry to the head. `back` selects the least-recent real entry. `remove` detaches an entry and adds it to the free ring.

## State And Persistence
All state is in memory: vector records, a free-list pointer, logical size, and current head. No persistence or synchronization.

## Dependencies And Integration Points
Uses only standard C++ headers and lives in `FileSystem` namespace for cache policy use.

## Risks And Test Signals
Default `uint16_t` keys cap capacity below 64K records and all safety is via asserts. `mark_key_cleared` removes without reducing `m_size`, so callers must understand its special eviction semantics. No direct tests in this subset. Source size reviewed: 147 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/policy/lru.h -->
