# File Research: sources/cow-pools/bcachefs/fs/bcachefs/closure.h

This tiny compatibility wrapper includes `vendor/closure.h` and aliases generic closure symbols to bcachefs-prefixed names.

Aliases:
- `closure_wait` to `bch2_closure_wait`
- `closure_return_sync` to `bch2_closure_return_sync`
- `__closure_wake_up` to `__bch2_closure_wake_up`
- `closure_sync_unbounded` to `bch2_closure_sync_unbounded`

It lets local bcachefs code use closure-style APIs while avoiding symbol collisions with external or vendored closure implementations.
