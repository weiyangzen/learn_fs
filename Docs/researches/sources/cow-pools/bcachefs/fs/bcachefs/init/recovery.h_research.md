# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/recovery.h

## Role

Public declarations for the recovery pipeline.

## Contents

Declares helpers for lost btree data, journal rewind error silencing, early RW transition, journal replay, full filesystem recovery, and new filesystem initialization.

## Notable Details

This header exposes only the top-level recovery operations; pass scheduling details are in `passes.h`.
