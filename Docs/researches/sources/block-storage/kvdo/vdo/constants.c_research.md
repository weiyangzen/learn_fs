# File Research: sources/block-storage/kvdo/vdo/constants.c

## Purpose
Defines externally visible VDO size limit constants declared in `constants.h`.

## Constants
- `MAXIMUM_VDO_LOGICAL_BLOCKS`: 4 PB, represented as 1 terablock.
- `MAXIMUM_VDO_PHYSICAL_BLOCKS`: 256 TB, represented as 64 gigablocks.
- `MINIMUM_VDO_SLAB_JOURNAL_BLOCKS`: unit-test minimum of 2.

## Research Notes
This file contains only constant definitions; most compile-time constants live in `constants.h`.
