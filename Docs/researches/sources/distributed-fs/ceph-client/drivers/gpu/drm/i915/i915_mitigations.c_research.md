# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_mitigations.c

## Purpose
Implements the `i915.mitigations` module parameter and the query for whether residual thread-local register clearing should be enabled.

## Important APIs, types, and functions
Public `i915_mitigate_clear_residuals()` reads the mitigation bitmask. Private `mitigations_set()` parses parameter strings, `mitigations_get()` formats active state, and `module_param_cb_unsafe()` registers the parameter.

## Control flow
The bitmask defaults to all bits set (`auto`). Parsing duplicates the input, tokenizes comma-separated values, handles first-token `auto` or `off`, accepts `!` and `no` prefixes to disable named mitigations, and updates the mask with `WRITE_ONCE()` only after successful parsing. The getter prints `off`, `auto` plus disabled exceptions, or enabled named mitigations.

## State and persistence
Global `mitigations __read_mostly` stores the active mitigation mask for all Intel GPUs. It persists for the module lifetime and is read locklessly.

## Dependencies and integration points
Depends on Linux module parameter APIs and is consumed by context-switch or workaround code that checks `i915_mitigate_clear_residuals()`.

## Risks
The parser is an ABI: unknown names reject the whole update. `module_param_cb_unsafe` signals runtime changes may not be synchronized with all users. The `auto` representation uses high bits to distinguish default from explicit masks.

## Test signals
Boot or modprobe with `mitigations=auto`, `off`, `residuals`, `auto,noresiduals`, `!residuals`, and invalid names; verify sysfs formatting and residual-clear behavior on affected Ivybridge/Baytrail/Haswell platforms.
