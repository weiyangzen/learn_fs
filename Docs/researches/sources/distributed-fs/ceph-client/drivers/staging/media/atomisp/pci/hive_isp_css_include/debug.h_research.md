# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_include/debug.h

## Purpose

`debug.h` is the public facade include for the `debug.h` API, selecting local/public/private headers depending on inline build macros.

## Important APIs, Types, And Data

Key includes: `system_local.h`, `debug_local.h`, `debug_public.h`, `debug_private.h`. Important macros/constants include `__DEBUG_H_INCLUDED__`, `STORAGE_CLASS_DEBUG_H`, `STORAGE_CLASS_DEBUG_C`.

## Control Flow

The facade branches at preprocessing time. Without the subsystem inline macro it declares extern/public functions; with the inline macro it includes private static inline bodies. Runtime behavior is delegated to the selected public/private implementation.

## State And Persistence Behavior

This file has no mutable storage. Its effects persist only through callers that use the exposed macros, declarations, or include-time selection to touch device registers or shared firmware memory.

## Dependencies And Integration Points

Its integration role is include-graph composition. It depends on the matching local/public/private headers and `system_local.h`; users include the facade rather than selecting private headers directly.

## Risks And Edge Cases

- The main risk is include-mode skew: public declarations and private inline bodies must stay ABI-compatible with the out-of-line `.c` implementation.
- Because this file has little direct content, regressions usually appear as compile/link failures in consumers rather than as local unit-test failures.

## Test Signals

- Compile all consumers that include this header directly and through the subsystem facade.
- Enable warnings for missing prototypes, duplicate inline definitions, and macro redefinition drift.
- Use small caller-side tests to confirm macro expansion behavior and assertion handling.
