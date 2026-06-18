# sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_manager_private.h

## Purpose

`audio_manager_private.h` declares private helper functions shared inside the Greybus audio manager implementation.

## Important APIs, Types, and Functions

It declares `gb_audio_manager_module_create()`, `gb_audio_manager_module_dump()`, and optional `gb_audio_manager_sysfs_init()`.

## Control Flow

`audio_manager.c` calls module-create/dump helpers and, when compiled with `GB_AUDIO_MANAGER_SYSFS`, initializes writable manager debug attributes.

## State and Persistence Behavior

No state is owned in the header. It exposes helpers operating on manager kobjects and module descriptors.

## Dependencies and Integration Points

It depends on kobject definitions and `audio_manager.h`, and is included by manager, module, and sysfs implementation files.

## Risks and Edge Cases

The header exposes sysfs init unconditionally while the call site is preprocessor-gated. It carries no include guard for sysfs config semantics, so build coverage must catch optional-object mismatches.

## Test Signals

Compile both default and `GB_AUDIO_MANAGER_SYSFS` builds to verify private declarations match object composition.
