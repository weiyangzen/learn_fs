# sources/distributed-fs/ceph-client/include/linux/refcount_api.h

## Purpose

This compatibility wrapper includes `linux/refcount.h`, exposing the full refcount API through an `_api` include name.

## Important APIs, Types, and Functions

It defines no direct symbols. The available APIs are those from `refcount.h`: `refcount_set()`, `refcount_inc*()`, `refcount_dec*()`, saturation constants, and lock-coupled helpers.

## Control Flow

There is no runtime control flow in this file. It affects preprocessing only.

## State and Persistence Behavior

No state is introduced here; all state belongs to `refcount_t` objects declared by users of the included API.

## Dependencies and Integration Points

The only dependency is `#include <linux/refcount.h>`. It exists to satisfy include paths that distinguish API wrappers from type headers.

## Risks

The wrapper can obscure that all semantics come from `refcount.h`. Semantic risks are those of the underlying refcount operations.

## Test Signals

Compilation of users including `refcount_api.h` is the relevant signal; runtime behavior should be tested through `refcount.h`.
