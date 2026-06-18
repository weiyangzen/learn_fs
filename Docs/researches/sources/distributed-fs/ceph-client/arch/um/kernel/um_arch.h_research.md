# sources/distributed-fs/ceph-client/arch/um/kernel/um_arch.h

## Purpose
Declares UML architecture boot helpers shared by `um_arch.c` and optional platform code.

## Important APIs, Types, and Functions
Declares `uml_load_file()`, `uml_dtb_init()` when `CONFIG_OF` is enabled, a no-op inline `uml_dtb_init()` otherwise, and weak/overridable `read_initrd()`.

## Control Flow, State, and Persistence
No state or control flow beyond the conditional inline. It defines compile-time linkage for optional DTB and initrd loading.

## Dependencies and Integration Points
Included by `um_arch.c`; optional implementations are expected elsewhere under UML architecture code when OF/initrd support is enabled.

## Risks and Test Signals
Risk is mostly configuration drift: missing optional implementations or wrong prototypes break boot-time initrd/DTB support. Test builds with and without `CONFIG_OF` and with initrd-enabled configs.
