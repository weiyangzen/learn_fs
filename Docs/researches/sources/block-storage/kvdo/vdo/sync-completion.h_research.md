# File Research: sources/block-storage/kvdo/vdo/sync-completion.h

This header declares `vdo_perform_synchronous_action()`. The function runs a `vdo_action` on a specified VDO thread, optionally with a parent pointer, then waits synchronously for completion and returns the action result.
