# File Research: sources/block-storage/kvdo/vdo/read-only-notifier.h

Read completely: 58 lines.

This header declares the read-only notifier API and documents its purpose: propagating unrecoverable VDO errors to base threads, persisting read-only state through the superblock path, and allowing shutdown code to wait until notifications are complete.

It defines the `vdo_read_only_notification` callback signature and declares creation, destruction, wait/disallow, allow, enter-read-only, state query, and listener registration functions.

Dependencies: VDO completion types, thread configuration, `struct vdo`, and `thread_id_t` through included headers.

Research notes: the API separates `vdo_is_read_only()` for thread-local state from `vdo_is_or_will_be_read_only()` for checking whether read-only entry has begun globally.
