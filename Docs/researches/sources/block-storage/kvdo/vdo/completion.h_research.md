# File Research: sources/block-storage/kvdo/vdo/completion.h

## Purpose

Defines VDO’s asynchronous completion object and helper API.

## Contents

- `enum vdo_completion_type` with sorted completion type IDs.
- `typedef vdo_action`.
- `struct vdo_completion`
  - type,
  - complete/requeue flags,
  - callback thread,
  - result,
  - owning VDO,
  - callback and error handler,
  - parent,
  - work queue link,
  - priority,
  - queue pointer,
  - enqueue time.
- Inline callback/run/finish/prepare helpers.
- Declarations for initialization, reset, invoke, continue, complete, preserve error, assert, and enqueue functions.

## Behavior Details

`vdo_run_completion_callback()` routes to `error_handler` when the result is non-success and an error handler exists; otherwise it calls the normal callback.

The prepare helpers reset completions and set callback, error handler, thread, parent, and optional forced requeue.

## Role

This is the core asynchronous control-flow type used across the kvdo module.
