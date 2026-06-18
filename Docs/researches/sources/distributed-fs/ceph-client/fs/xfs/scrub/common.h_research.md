# sources/distributed-fs/ceph-client/fs/xfs/scrub/common.h

Purpose: Declares the shared XFS scrub helper API and compile-time fallbacks for optional quota and realtime features.

Important APIs, types, and functions: The header exports transaction helpers, error processors, corruption/preen/warning setters, setup functions for filesystem/AG/inode/directory/xattr/parent/dirtree/metapath/realtime/quota/counter scrubbers, AG and rtgroup lifecycle functions, inode acquisition and lock wrappers, buffer recheck, cross-reference gating, metadata inode fork scrub, filesystem hook enabling, inode allocation/block-count helpers, and root-directory predicates. Inline helpers include `xchk_setup_nothing()`, `xchk_ag_init_existing()`, `xchk_rtgroup_init_existing()`, `xchk_iget_safe()`, `xchk_skip_xref()`, `xchk_needs_repair()`, `xchk_could_repair()`, and `xchk_need_intent_drain()`.

Control flow: Scrub operation tables use the setup prototypes to acquire the required resources before calling a specific scrub function. Optional feature sections map unsupported realtime or quota setup functions to `xchk_setup_nothing()` or corruption-style stubs so callers can compile without feature-specific conditionals.

State and persistence: The header defines no persistent structures. Its inline predicates interpret `struct xfs_scrub_metadata` flags to decide whether xref should continue, whether repair is needed, and whether repair was requested and not already completed.

Dependencies and integration points: Included throughout `fs/xfs/scrub`. It ties scrub code to XFS mount, inode, buffer, btree cursor, perag, rtgroup, owner info, and quota types, and exposes integration points for repair, health marking, and feature-gated metadata scans.

Risks and test signals: Risks are API contract drift between setup functions and callers, wrong feature fallback behavior for `CONFIG_XFS_RT` or `CONFIG_XFS_QUOTA`, and misuse of `xchk_skip_xref()` causing missed cross-reference failures. Test by compiling quota/realtime combinations, running each scrub type's setup/teardown, and checking repair-flag transitions through preen/corrupt/xcorrupt outcomes.
