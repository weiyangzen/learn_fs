# File Research: sources/block-storage/kvdo/vdo/instance-number.c

Global VDO instance-number allocator backed by a growable bitmap.

Key responsibilities:
- Tracks allocated instance numbers in a flat `unsigned long` bit array.
- Initializes and destroys global mutex-protected tracking state.
- Allocates the next free instance number, growing capacity as needed.
- Releases previously allocated instance numbers.
- Starts with minimum capacity for 1000 instances and grows by 100 bits.

Important behavior:
- Allocation scans from `next_instance` and wraps to zero if needed.
- The first allocation lazily grows the bitmap because initial `words` is `NULL`.
- Successive starts of the same volume can get different instance numbers, helping external monitoring detect reset stats.
- Cleanup asserts no instances remain allocated.

Dependencies:
- Uses Linux bit operations, mutexes, UDS memory allocation/reallocation, numeric helpers, and assertions.

Notable risks:
- All state is global; callers must initialize/cleanup exactly once at module lifecycle boundaries.
- Release only asserts on invalid/double release and otherwise continues.
- Bitmap scanning is O(n), intentionally accepted for expected device counts.
