# sources/distributed-fs/openafs/src/afs/afs_bypasscache.h

Purpose: Declares the cache-bypass read interface, bypass policy knobs, request carrier structure, and macros used by read paths to toggle bypass mode.

Important APIs and types: `struct nocache_read_request` carries platform-specific direct-read parameters. `enum cache_bypass_strategies` defines always, never, and large-file bypass modes. Exports `cache_bypass_prefetch`, `cache_bypass_strategy`, `cache_bypass_threshold`, allocation/free helpers, transition helpers, `afs_ReadNoCache`, and `afs_PrefetchNoCache`. `variable_cache_strategy` and `trydo_cache_transition` are policy macros for automatic vnode state transitions.

Control flow: The header is active only when `AFS_CACHE_BYPASS` or `UKERNEL` is defined. `trydo_cache_transition` checks whether the strategy is variable, compares the desired bypass flag with `avc->cachingStates`, and calls the appropriate transition routine.

State and persistence: Declares global policy variables and per-vnode state-bit interactions; no durable state is stored directly.

Dependencies and integration points: Pulls in AFS kernel headers, `struct vcache`, credentials, `struct uio`, and platform page-size definitions. It is consumed by fetch/read paths and the background daemon handling no-cache prefetch.

Risks: Macro policy code evaluates vnode state without taking a lock, relying on transition routines to re-check under lock. Platform-specific fields make incorrect structure use easy outside the intended OS branches. `AFS_CACHE_BYPASS_DISABLED` uses `-1` in a size-typed threshold, so comparisons must account for signed/unsigned behavior at callers.

Test signals: Compile with bypass disabled, enabled, and UKERNEL; verify policy transitions for all strategies; validate threshold-disabled behavior; and exercise macro use against vnodes already in the requested state.
