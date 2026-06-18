# File Research: sources/block-storage/kvdo/vdo/vdo-resize.h

## Purpose
Declares physical resize operations.

## Public API
- `vdo_perform_grow_physical()`: commit prepared physical growth.
- `vdo_prepare_to_grow_physical()`: prepare layout and slab depot structures for physical growth.

## Context
Physical growth is prepared before suspend/resume commit and performed only while suspended.
