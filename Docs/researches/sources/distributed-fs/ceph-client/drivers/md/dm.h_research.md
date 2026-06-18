# sources/distributed-fs/ceph-client/drivers/md/dm.h

## Purpose

`dm.h` is the internal device-mapper header shared by core DM modules, table code, target registry, sysfs/interface code, and built-in targets. It declares cross-file APIs for tables, mapped-device state, target types, zoned integration, suspend/resume, table devices, uevents, mempools, and common linear/stripe targets.

## Important APIs, Types, and Functions

It declares table callbacks and lookup, queue-limit calculation and restrictions, target suspend/resume hooks, queue mode and immutable target helpers, mapped-device type locking and queue setup, zoned helpers, target registry helpers, deletion/suspension/internal suspend APIs, sysfs/interface APIs, linear/stripe target init/map functions, mapped-device destruction/open-count/device reference APIs, kcopyd/io init, mempool cleanup, and hash-lock utilities.

## Control Flow

Only a few inline helpers have control flow. In non-zoned builds `dm_is_zone_write()` returns false and `dm_has_zone_plugs()` is false. Target-type classification is based on callback presence. Hash-lock helpers compute a power-of-two count and sector hash index.

## State and Persistence Behavior

The header declares no persistent state. Its flags and function contracts define how other DM files coordinate runtime state, especially suspend/status flags and zoned queue setup.

## Dependencies and Integration Points

It includes Linux fs, device-mapper, list, moduleparam, blkdev, backing-dev, hdreg, completion, kobject, refcount, log2, and `dm-stats.h`. `dm.c`, table code, target registry code, zoned helpers, sysfs, and interface code all depend on these declarations.

## Risks and Test Signals

Risks are contract drift between declarations and implementations, conditional zoned behavior differences, target callback classification mistakes, and hash-lock power-of-two assumptions. Test by building zoned and non-zoned configurations and exercising table restrictions, suspend/resume, target registry, internal suspend users, and zoned reports.
