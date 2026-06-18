# File Research: sources/block-storage/kvdo/Makefile

## Purpose

Top-level Kbuild makefile for the kvdo source tree. It delegates all build participation to the `vdo/` subdirectory.

## Contents

- Adds `vdo/` to `obj-y`, causing Kbuild to descend into `sources/block-storage/kvdo/vdo`.

## Dependencies and Interactions

- Relies on `sources/block-storage/kvdo/vdo/Makefile` for actual module object definitions and compiler flags.
