<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_force_wake.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_force_wake.h

## Purpose
`xe_force_wake.h` declares forcewake initialization and reference APIs, iteration helpers, assertions, and scoped cleanup classes.

## Important APIs, types, and functions
Exports include `xe_force_wake_init_gt()`, `xe_force_wake_init_engines()`, `xe_force_wake_get()`, `xe_force_wake_put()`, and `xe_force_wake_domain_to_str()`. Macros iterate initialized domains, query a domain refcount, assert a domain is awake, check whether an opaque forcewake reference includes a domain, and create scope-bound forcewake acquisition/release classes.

## Control flow and integration points
Inline control flow implements domain iteration by bitmask, `xe_force_wake_assert_held()`, and cleanup-on-scope-exit through `DEFINE_CLASS`. Callers use `CLASS(xe_force_wake, ...)`, `xe_with_force_wake()`, or `xe_force_wake_release_only` around MMIO sections that require powered domains.

## State and persistence behavior
The header owns no state but controls forcewake reference lifetime. The opaque `struct xe_force_wake_ref` carries the `fw` pointer and acquired domain mask so cleanup can put only acquired domains.

## Dependencies, risks, and test signals
Dependencies include Xe assertions and forcewake types. Risks include using assertions with multiple domains, losing the returned domain mask after partial wake failure, and cleanup class misuse with mismatched lifetimes. Test signals are build coverage for scoped guards, lockdep assertions on MMIO callers, and forcewake leak/timeout tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_force_wake.h -->
