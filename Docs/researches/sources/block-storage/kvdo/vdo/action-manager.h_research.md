# File Research: sources/block-storage/kvdo/vdo/action-manager.h

## Purpose

Declares the action-manager API used to coordinate asynchronous operations across multiple zones.

## Contents

- Documents the action model:
  - optional preamble on initiator thread,
  - optional action per zone,
  - optional conclusion on initiator thread,
  - optional parent completion.
- Declares callback typedefs:
  - `vdo_zone_action`,
  - `vdo_action_preamble`,
  - `vdo_action_conclusion`,
  - `vdo_action_scheduler`,
  - `vdo_zone_thread_getter`.
- Declares construction, status, context, and scheduling functions.

## Dependencies and Role

The header forms the public internal contract for multi-zone components that need serialized operation execution, especially block map and slab/depot operations.

## Notable Details

The API distinguishes generic actions from named admin-state operations, and also provides a context-bearing scheduler variant for recovery or growth workflows that need temporary operation-specific state.
