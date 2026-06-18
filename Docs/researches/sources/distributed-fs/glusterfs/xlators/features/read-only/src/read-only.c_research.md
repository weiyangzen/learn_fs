# sources/distributed-fs/glusterfs/xlators/features/read-only/src/read-only.c

## Purpose
`read-only.c` is the concrete read-only feature translator. It registers shared `ro_*` FOP wrappers, manages the `read-only` volume option, and allocates the translator private state that tells common wrappers whether to block mutating client operations.

## Important APIs and Functions
- `mem_acct_init()` initializes memory accounting with `gf_read_only_mt_end`.
- `init()` validates exactly one child, warns on dangling volume, allocates `read_only_priv_t`, and reads the `read-only` boolean option into `readonly_or_worm_enabled`.
- `reconfigure()` updates the `read-only` option at runtime.
- `fini()` frees private state.
- `fops` registers all common mutating/lock wrappers from `read-only-common.c`.
- `options` exposes the settable `read-only` option.
- `xlator_api` identifies the module as `"read-only"` with tech-preview category.

## Control Flow
When the translator is active, GlusterFS dispatches registered FOPs to the shared wrappers. Those wrappers consult `priv->readonly_or_worm_enabled`; `read-only.c` itself only manages lifecycle and option state.

## State and Persistence
Runtime state is a single `read_only_priv_t` allocated with `GF_CALLOC` and stored in `this->private`. It persists only in process memory and is freed in `fini()`. The volume option controls it persistently through the volfile/config system outside this file.

## Dependencies and Integration Points
Depends on `read-only-common.h`, memory types, GlusterFS option parsing/reconfiguration, and the xlator API. It must be built with `read-only-common.c` as specified in `src/Makefile.am`.

## Risks
- If `this->children` validation is bypassed, FOP wrappers assume a valid `FIRST_CHILD(this)`.
- Option reconfigure depends on `this->private` being initialized; null private state would assert.
- The registered FOP list must be updated when new write-like operations are added to GlusterFS.

## Test Signals
Test init failure with zero/multiple children, option default off, runtime reconfigure on/off, `EROFS` behavior for registered mutating FOPs, pass-through behavior when disabled, and cleanup under `fini()`.
