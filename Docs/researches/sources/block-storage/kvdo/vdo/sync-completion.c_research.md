# File Research: sources/block-storage/kvdo/vdo/sync-completion.c

This file implements a bridge from VDO asynchronous completions to synchronous waiting. `struct sync_completion` embeds a `vdo_completion`, Linux `completion`, and target action pointer.

`vdo_perform_synchronous_action()` initializes the embedded completion, launches `run_synchronous_action()` on the requested VDO thread with an optional parent, waits for the Linux completion, and returns the VDO completion result. The launched action has its callback replaced with `complete_synchronous_action()`, which wakes the waiting caller.

This is used where a caller outside a VDO base thread needs to execute an action on a specific VDO thread and block until it completes.
