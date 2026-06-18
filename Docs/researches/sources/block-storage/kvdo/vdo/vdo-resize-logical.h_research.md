# File Research: sources/block-storage/kvdo/vdo/vdo-resize-logical.h

## Purpose
Declares logical resize operations.

## Public API
- `vdo_perform_grow_logical()`: commit a prepared logical grow.
- `vdo_prepare_to_grow_logical()`: prepare block map structures for a future logical grow.

## Context
The implementation requires preparation while running and commit while suspended.
