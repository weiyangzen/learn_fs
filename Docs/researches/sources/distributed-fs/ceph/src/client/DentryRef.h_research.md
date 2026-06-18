# sources/distributed-fs/ceph/src/client/DentryRef.h

## Purpose
`DentryRef.h` defines the intrusive smart-pointer alias used for `Dentry` references.

## Important APIs, Types, and Functions
It forward-declares `Dentry`, declares `intrusive_ptr_add_ref(Dentry*)` and `intrusive_ptr_release(Dentry*)`, and aliases `DentryRef` to `boost::intrusive_ptr<Dentry>`.

## Control Flow
Any code that stores a `DentryRef` increments the embedded dentry refcount through the functions implemented in `Dentry.cc`; releasing the ref calls `Dentry::put()` and may delete the dentry.

## State and Persistence Behavior
No state is declared beyond ownership semantics. The referenced dentry remains an in-memory cache object.

## Dependencies and Integration Points
It depends only on Boost intrusive pointer. `MetaRequest`, `Client::walk_dentry_result`, and cache code use `DentryRef` to pin dentries across async request flow.

## Risks and Edge Cases
Because ownership uses dentry-internal refcounts, all raw-pointer users must avoid creating untracked lifetimes. The add/release functions must stay consistent with `Dentry::get()`/`put()`.

## Test Signals
Build/link tests for intrusive pointer symbols, request lifetime tests that pin dentries, and cache trim tests with outstanding `DentryRef`.
