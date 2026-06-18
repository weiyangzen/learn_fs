# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/pagefault/pagefault.h

## Purpose

This generated header contains the Buchi automaton for the pagefault LTL property.

## Important APIs, Types, and Functions

Atoms are `LTL_PAGEFAULT` and `LTL_RT`. The automaton has a single state `S0`, with `ltl_atom_str()`, `ltl_start()`, and `ltl_possible_next_states()` implementing the property.

## Control Flow

The formula keeps `S0` only when the task is not RT or no page fault occurred. If `RT && PAGEFAULT`, no next state is set, causing a violation in the LTL framework.

## State and Persistence Behavior

Runtime state is a per-task bitset of atoms and Buchi states. This header stores only generated static logic.

## Dependencies and Integration Points

It includes `<linux/rv.h>` and is consumed by `pagefault.c` and `rv/ltl_monitor.h`.

## Risks and Edge Cases

The model is intentionally minimal; any mistake in atom pulsing or RT atom refresh directly determines false positives or false negatives.

## Test Signals

Exercise all atom combinations: non-RT/no fault, non-RT/fault, RT/no fault, and RT/fault, expecting violation only for the last.
