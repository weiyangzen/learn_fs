## sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/util.h

### Purpose
`util.h` declares qtnfmac station-list helpers and chip ID string conversion, plus inline size/empty accessors.

### Important APIs, Types, And Functions
It declares all station list operations implemented in `util.c` and `qtnf_chipid_to_string()`. Inline helpers are `qtnf_sta_list_size()` and `qtnf_sta_list_empty()`.

### Control Flow
Callers initialize a list, add/delete/lookup nodes through the declared functions, and query size or emptiness with lightweight inline reads. The header itself contains no complex flow.

### State, Persistence, And Dependencies
The header has no state but exposes operations on state defined by `core.h`. It depends on `linux/kernel.h` and qtnfmac core structures.

### Integration Points
Interface, event, station-info, and debug paths include this header to share station-list behavior without exposing implementation details in every file.

### Risks
The inline accessors do not lock; they are only as safe as caller synchronization. Including `core.h` makes this utility header coupled to central driver internals.

### Test Signals
Build coverage across all users, lockdep/KCSAN around list readers, and station lifecycle tests validate the interface.
