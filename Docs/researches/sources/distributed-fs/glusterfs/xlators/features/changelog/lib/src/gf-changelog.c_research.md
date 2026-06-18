# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog.c

## Purpose
Bootstraps libgfchangelog as a small GlusterFS runtime, manages global library state, registers consumers against one or more bricks, and wires callbacks to RPC and journal processing.

## APIs, Types, and Functions
Public registration entry points are `gf_changelog_init()`, `gf_changelog_register_generic()`, and legacy `gf_changelog_register()`. Setup helpers include `gf_changelog_alloc_priv()`, `gf_changelog_ctx_defaults_init()`, `gf_changelog_init_context()`, `gf_changelog_set_primary()`, `gf_setup_brick_connection()`, `gf_changelog_setup_rpc()`, `gf_init_event()`, and cleanup placeholders `gf_cleanup_connections()`/`gf_cleanup_brick_connection()`. `gf_changelog_cleanup_this()` tears down the synthetic context.

## Control Flow, State, and Persistence
A process-wide `primary` xlator singleton owns a generated Gluster context, iobuf/event pools, call frame pools, dict pools, syncenv, logging, and `gf_private_t` connection lists. `gf_changelog_register_generic()` sets logging, iterates `gf_brick_spec` entries, allocates `gf_changelog_t`, initializes its ordered/unordered event invoker, calls the consumer-specific `init`, links it into `priv->connections`, starts reverse and forward RPC channels, sleeps briefly, then sends the probe filter request. The legacy API constructs a one-brick journal spec using `gf_changelog_journal_*` callbacks and stores the scratch-dir API pointer in `priv->api`.

## Dependencies and Integration
Depends on libglusterfs globals, event pools, mem pools, syncop, logging, RPC helpers, changelog memory IDs, and callback structures from `gf-changelog-helpers.h`. It integrates with `gf-changelog-rpc.c` for probe RPC, `gf-changelog-reborp.c` for reverse callbacks, and `gf-changelog-journal-handler.c` for legacy journal persistence.

## Risks and Test Signals
Risks include global singleton constraints, incomplete cleanup functions, sleeps as connection synchronization, partial failure leaks in RPC setup, and legacy API limitation to a single journal owner. Test signals include repeated init idempotence, registration of multiple bricks with ordered and unordered modes, cleanup on failed callback init/RPC setup, logging setup failures, and legacy journal registration against a scratch directory.
