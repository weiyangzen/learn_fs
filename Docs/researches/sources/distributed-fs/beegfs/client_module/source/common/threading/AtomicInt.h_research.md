<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/threading/AtomicInt.h -->
## sources/distributed-fs/beegfs/client_module/source/common/threading/AtomicInt.h

**Purpose:** Wraps Linux `atomic_t` in the BeeGFS client threading abstraction. **APIs/types:** `AtomicInt` stores `atomic_t`; inline init/uninit, increment, decrement, read, set, compare-and-swap, max, and decrement-and-test helpers. **Control flow/state:** `AtomicInt_max` loops with cmpxchg until the value is at least `minValue` or another writer already advanced it. **Dependencies/integration:** used by counters needing lock-free integer updates. **Risks/tests:** `AtomicInt_max` can spin if values are concurrently non-monotonic as noted in comments; tests should cover cmpxchg return semantics and dec-to-zero behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/threading/AtomicInt.h -->
