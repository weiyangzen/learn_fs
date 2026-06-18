# File Research: sources/cow-pools/bcachefs-tools/fs/errcode.h

## Purpose

Defines the complete bcachefs custom error-code namespace and helper APIs.

## Main Interfaces

- `enum bch_errcode` starts custom values at `BCH_ERR_START = 2048`.
- `BCH_ERRCODES()` x-macro lists all custom errors with parent classes.
- Helper macros/functions:
  - `bch2_err_matches(err, class)`.
  - `bch2_err_class(err)`.
  - block and zstd conversion declarations.

## Error Families

The macro covers block-device status, zstd failures, option parsing, allocation and ENOSPC sites, missing objects, btree transaction restarts, no-btree-node conditions, btree insert failures, fsck outcomes, recovery scheduling, bucket/data-update conditions, user permission errors, ioctl validation, invalid superblocks/bkeys, journal/blocking states, btree/data read-write failures, stripe/erasure-coding failures, decompression/read retry cases, no-promote outcomes, nocow failures, shutdown errors, and many targeted `EINVAL`/`EROFS` cases.

## Behavior

Each entry is written as `x(parent_class, leaf_name)`. Parents can be standard errno values or other bcachefs custom codes, allowing hierarchical matching and class reduction in `errcode.c`.

## Dependencies

Includes Linux block types and zstd error declarations after defining the enum.

## Risks And Notes

This file is central to error semantics. Adding, renaming, or reparenting entries changes string output, trace output, class matching, and user-visible/sysfs/ioctl error behavior. The enum order also backs generated lookup tables.
