<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dev.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dev.h

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dev.h_research.md`.

Purpose: declares the kfilnd device-management API and local hash sizing constants.

Important APIs/types/functions: `KFILND_CURRENT_HASH_BITS`, `KFILND_MAX_HASH_BITS`, `kfilnd_dev_post_imm_buffers()`, `kfilnd_dev_free()`, `kfilnd_dev_alloc()`, `kfilnd_dev_reset_stats()`, and `kfilnd_dev_get_session_key()`.

Control flow: the main LND uses allocation/post/free during NI startup/shutdown; debugfs and transaction code use stats and session-key helpers.

State and persistence behavior: no state is stored in the header. Hash constants constrain internal peer-cache sizing expectations.

Dependencies and integration: includes `kfilnd.h` for `struct kfilnd_dev`, `struct lnet_ni`, and shared definitions.

Risks: constants are marked TODO for module parameters; changing them must align with rhashtable use and memory expectations.

Test signals: compile all users, startup/shutdown NI, read debugfs stats after reset, and verify session keys advance across peer allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dev.h -->
