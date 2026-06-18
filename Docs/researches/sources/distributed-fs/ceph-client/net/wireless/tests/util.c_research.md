# sources/distributed-fs/ceph-client/net/wireless/tests/util.c

## Purpose
`util.c` implements the shared KUnit wiphy fixture used by cfg80211 wireless tests.

## Important APIs, Types, And Functions
It defines `t_wiphy_init()` and `t_wiphy_exit()`. Initialization allocates `cfg80211_ops`, creates a named wiphy via `wiphy_new_nm()`, stores test context and ops in `struct t_wiphy_priv`, and installs a copied 2.4 GHz channel table. Exit frees the wiphy and the allocated ops.

## Control Flow
KUnit calls `t_wiphy_init()` through `kunit_alloc_resource()` from the `T_WIPHY()` macro. The init path asserts allocations, initializes the private fixture data, and returns the wiphy as resource data. KUnit later calls `t_wiphy_exit()` to recover the private data, free the wiphy, and release ops memory.

## State And Persistence
Fixture state persists only for the lifetime of a KUnit resource. It includes the caller context pointer, allocated cfg80211 ops, a supported-band object, and a mutable copy of the shared 2.4 GHz channels.

## Dependencies And Integration Points
The file depends on KUnit resource APIs, cfg80211 wiphy allocation/free APIs, `channels_2ghz` and `struct t_wiphy_priv` from `util.h`, and tests that need a lightweight wiphy without registering real hardware.

## Risks And Edge Cases
The fixture intentionally does not fully register the wiphy, so tests must use only APIs that work on an unregistered test wiphy. If future tests need more bands, rates, regulatory flags, or driver ops, they must extend this fixture without breaking existing assumptions. The TODO-style comment notes that teardown does not currently assert absence of outstanding state.

## Test Signals
Successful use by `tests/scan.c` confirms that channels can be looked up and inform-BSS callbacks can be installed. KASAN/KUnit resource cleanup can detect leaks in wiphy or ops allocation paths.
