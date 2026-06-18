# File Research: sources/block-storage/kvdo/vdo/admin-completion.h

## Purpose

Declares the admin completion structure and helper API for synchronous administrative VDO operations.

## Contents

- Defines `enum admin_operation_type`:
  - unknown,
  - logical grow,
  - physical grow,
  - prepare physical grow,
  - load,
  - pre-load,
  - resume,
  - suspend.
- Defines `vdo_thread_id_getter_for_phase`.
- Defines `struct admin_completion` with:
  - owning `struct vdo`,
  - outer completion,
  - sub-task completion,
  - busy flag,
  - operation type,
  - phase thread resolver,
  - phase index,
  - Linux completion for synchronous callback wait.
- Declares helpers for assertions, sub-task preparation, initialization, and operation execution.

## Dependencies and Role

This header is the bridge between control-plane operations and the VDO base-thread completion model.
