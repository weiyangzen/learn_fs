# sources/distributed-fs/glusterfs/xlators/playground/template/src/template.c

## Purpose
Provides a maintained example skeleton for writing a GlusterFS translator. It demonstrates memory accounting, private option parsing, statedump/priv-to-dict hooks, metrics output, init/fini/reconfigure, notify forwarding, xlator API registration, and option metadata.

## Important APIs, Types, And Functions
`template_mem_acct_init()` initializes memory accounting. `template_init()` validates exactly one child and at least one parent, allocates `template_private_t`, and parses `dummy`. `template_reconfigure()` updates `dummy`. `template_fini()` frees private state. `template_priv()`, `template_priv_to_dict()`, and `template_dump_metrics()` expose private state to diagnostics. `template_notify()` forwards all events to `default_notify()`. `xlator_api` wires these hooks with empty fop/cbk tables and `template_options`.

## Control Flow
Module load calls memory accounting then init. Runtime events enter `template_notify()` and are forwarded. Statedump and metrics paths read `priv->dummy`. Reconfigure uses Gluster option macros to update the integer. Fini clears `this->private`.

## State And Persistence
Only `template_private_t.dummy` is stored in memory. No filesystem operations are intercepted because the fop table is empty.

## Dependencies And Integration Points
Uses Gluster xlator API, defaults, dict, logging, statedump, message IDs from `template.h`, and volume option metadata with experimental tags.

## Risks
The parent check rejects dangling volumes as an error, unlike some production translators that only warn. `template_priv_to_dict()` does not check for null private state. Empty fops mean the template is not functional unless extended.

## Test Signals
Loading with valid graph should set `dummy`; invalid graph should fail. Reconfigure should update `dummy`. Statedump, `priv_to_dict`, and metrics should report the same value.
