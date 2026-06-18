# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctimap.h

## Purpose

This header defines the generic input-mapper node and list operations used by ctxfi resource managers.

## Important APIs, types, and functions

`struct imapper` stores an input `slot`, consuming `user`, mapper RAM `addr`, linked-list `next`, and `list_head`. It declares `input_mapper_add()`, `input_mapper_delete()`, and `free_input_mapper_list()`.

## Control flow

Callers allocate mapper entries, maintain a list head, and supply a `map_op` callback that receives each changed entry whenever the chain is modified.

## State and persistence behavior

The header defines in-memory mapper state only. Persistent hardware state is produced by callback users such as SRCIMP manager code.

## Dependencies and integration points

It depends on `<linux/list.h>` and is included by `ctsrc.h`/`ctsrc.c` for SRC input mapper resource management.

## Risks and test signals

The structure is shared with hardware programming code, so field semantics must remain stable. Compile tests and SRCIMP mapping/unmapping tests are the best signals.
