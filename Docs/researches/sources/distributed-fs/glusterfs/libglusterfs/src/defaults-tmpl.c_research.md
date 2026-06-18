# sources/distributed-fs/glusterfs/libglusterfs/src/defaults-tmpl.c

## Purpose
This template backs generated default translator operations. It fills `xlator_fops` with default pass-through FOP implementations and supplies non-generated default handlers for lifecycle and notification behavior.

## Important APIs, types, and functions
`_default_fops` initializes each FOP slot to `default_*` functions, and `default_fops` points to that table. Hand-written functions include `default_forget`, `default_releasedir`, `default_release`, `default_notify`, `default_mem_acct_init`, and `default_fini`.

## Control flow
Generated FOPs forward calls to the first child translator and unwind callbacks. `default_notify()` routes events according to direction: parent up/down and cleanup flow to children; child up/down/connecting/auth/upcall/ping flow to parents or root; graph top child-down can mark `graph->used = 0` and broadcast `child_down_cond` when all client xlators are down. `default_fini()` frees `this->private`.

## State and persistence behavior
The default FOP table is static process state. `default_notify()` mutates in-memory graph state for child-down completion and may propagate events through translator graph relationships. No disk persistence occurs.

## Dependencies and integration points
It depends on `glusterfs/defaults.h`, translator graph structures, `xlator_notify`, `XLATOR_NOTIFY`, graph mutex/condition variables, and memory-accounting setup through `xlator_mem_acct_init()`. It is foundational for translators that omit explicit FOP, callback, notify, or lifecycle handlers.

## Risks and edge cases
Notification routing is graph-sensitive and can accidentally bypass parents that have not `init_succeeded`. Root forwarding special cases are important for FUSE/client graphs. `default_fini()` blindly frees `this->private` without translator-specific cleanup, so translators with richer private state need custom fini handlers.

## Test signals
Tests should validate generated default FOP forwarding, callback unwind behavior, notify propagation for each event family, root xlator forwarding, child-down graph condition broadcast, and that translators with default fini only use simple `GF_FREE`-managed private data.
