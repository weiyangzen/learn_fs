# File Research: sources/block-storage/kvdo/vdo/admin-state.h

## Purpose

Declares the VDO administrative state model and transition APIs.

## Contents

- Defines `struct admin_state_code` category flags and state name.
- Extern-declares all state-code pointers.
- Defines `struct admin_state`:
  - current state,
  - next state,
  - waiter completion,
  - `starting` flag,
  - `complete` flag.
- Provides inline state predicates:
  - normal,
  - suspending,
  - saving,
  - saved,
  - draining,
  - loading,
  - resuming,
  - clean load,
  - quiescing,
  - quiescent.
- Declares start/finish APIs for drain, load, resume, generic operations, and direct quiescent resume.

## Dependencies and Role

This header is central to administrative flow control across VDO components. Components use it to block incompatible work while preserving consistent completion behavior.

## Notable Details

`vdo_set_operation_result()` only updates a waiter if one exists, making it safe for components to preserve errors opportunistically during multi-step operations.
