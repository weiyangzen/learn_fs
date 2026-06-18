# sources/distributed-fs/ceph-client/tools/perf/util/pstack.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/pstack.c` implements a small fixed-capacity stack of opaque pointers for perf utility code.

## Important APIs, Types, and Functions

The private `struct pstack` stores `top`, `max_nr_entries`, and a flexible `entries[]` array. Public functions are `pstack__new`, `pstack__delete`, `pstack__empty`, `pstack__remove`, `pstack__push`, and `pstack__peek`.

## Control Flow

Creation allocates a zeroed object sized for the requested entry count and records capacity. Push appends at `top` unless capacity is full, in which case it logs an error and drops the entry. Peek returns the last pushed pointer or `NULL`. Remove scans backward for pointer identity, shifts later entries down with `memmove`, decrements `top`, and logs an error if the key is absent. Delete frees the allocation.

## State and Persistence Behavior

State is entirely in-memory and caller-owned through the returned pointer. The stack does not own the objects referenced by entries. There is no synchronization and no persistence.

## Dependencies and Integration Points

It depends on `pstack.h`, perf debug logging, kernel `zalloc`, and libc allocation/string helpers. It is a generic utility for local traversal/context stacks.

## Risks and Edge Cases

Capacity and top are `unsigned short`, so very large requested capacities truncate at the API type. Underflow would occur in `pstack__remove` if called on an empty stack because `last_index` is initialized from `top - 1`; callers should avoid removing from an empty stack. Overflow and missing-key cases only log errors.

## Test Signals

Unit tests should cover allocation sizing, push/peek order, overflow logging/drop behavior, remove of top/middle/bottom entries, absent-key behavior, empty checks, and freeing without freeing pointed-to objects.
