# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/bit-rot-stub.h

Purpose: this header declares the bitrot stub's private structures, fop-local structures, fd context structures, guard macros, inline state helpers, and helper prototypes used by `bit-rot-stub.c` and `bit-rot-stub-helpers.c`.

Important types and APIs: `br_stub_inode_ctx_t` stores current version, dirty/modified flags, signing state, fd list, and bad-object state. `br_stub_fd_t` stores fd identity plus quarantine directory iterator state. `br_stub_local_t` carries delayed fop context across call stubs. `br_stub_private_t` stores the `bitrot` option, boot timestamp, export path, signature queue, bad-object worker container, local mem pool, quarantine base path, and bad-object directory GFID. Public helper prototypes cover fd context management, quarantine management, bad-object path lookup, readdir wrappers, and worker queueing.

Control flow helpers: `BR_STUB_VER_NOT_ACTIVE_THEN_GOTO`, `BR_STUB_VER_COND_GOTO`, `BR_STUB_VER_ENABLED_IN_CALLPATH`, and `BR_STUB_RESET_LOCAL_NULL` implement the sentinel-based mechanism used to remember whether versioning was enabled on the call path. Inline helpers mark inodes dirty/synced/modified, mark objects bad, read/set inode ctx, compute writeback version, determine release-trigger eligibility, filter internal xattrs, strip bitrot xattrs from outward dicts, and set bad inode markers.

State and persistence behavior: the header defines quarantine path constants, including migration support for the old misspelled `quanrantine` path. It does not write xattrs itself but names the state transitions used by the implementation before writing current-version, signing-version, and bad-object xattrs.

Dependencies and integration points: includes logging, dict, call-stub, syscall wrappers, common bitrot formats, structured messages, and XDR definitions. Its prototypes connect the main stub fop file to helper functions and to GlusterFS inode/fd context primitives.

Risks: `__br_stub_can_trigger_release` encodes the last-fd release rule and assumes modified implies not dirty before notification; regressions here directly affect missing or duplicate signing. Sentinel use in `frame->local` is compact but fragile. Inline xattr removal can accidentally hide or expose bad-object markers depending on the `remove_bad_marker` flag.

Test signals: unit-like tests should target inline state helpers through fop scenarios: dirty to synced to modified transitions, bad-object marking, release eligibility with multiple fds, internal xattr filtering, and outward dict scrubbing with and without bad marker retention.
