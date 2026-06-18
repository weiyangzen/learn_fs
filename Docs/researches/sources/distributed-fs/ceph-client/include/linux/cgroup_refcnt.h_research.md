# sources/distributed-fs/ceph-client/include/linux/cgroup_refcnt.h

## Purpose

`cgroup_refcnt.h` provides inline or debug-overridable reference helpers for `struct cgroup_subsys_state`.

## Important APIs, Types, and Functions

It defines `css_get()`, `css_get_many()`, `css_tryget()`, `css_tryget_online()`, `css_put()`, and `css_put_many()` using `percpu_ref` operations unless `CSS_NO_REF` is set. `CGROUP_REF_FN_ATTRS` and `CGROUP_REF_EXPORT` are supplied by the includer.

## Control Flow

Callers acquire references when they already hold or can safely access a css. Try-get helpers either acquire a live/offline-tolerant ref or report failure. Put helpers release one or more refs.

## State and Persistence Behavior

The helpers mutate the css percpu refcount. `CSS_NO_REF` csses skip reference accounting and always succeed for try-get.

## Dependencies and Integration Points

It is included from `cgroup.h` when `CONFIG_DEBUG_CGROUP_REF` is off; debug builds provide out-of-line versions. It depends on `cgroup_subsys_state`, CSS flags, and percpu ref APIs.

## Risks and Edge Cases

`css_tryget()` can succeed for offline csses; callers needing online state must use `css_tryget_online()`. The caller must ensure pointer accessibility, typically through RCU or an existing ref. Mispaired many/get puts corrupt lifetime.

## Test Signals

Use refcount debug builds, RCU lookup races, online/offline try-get tests, CSS_NO_REF subsystem behavior, and leak detection during cgroup deletion.
