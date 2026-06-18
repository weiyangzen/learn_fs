# sources/distributed-fs/orangefs/src/common/llist/module.mk.in

Purpose: Build-fragment registration for the linked-list implementation.

Important build variables: Sets `DIR := src/common/llist`, then appends `llist.c` to `LIBSRC`, `SERVERSRC`, and `LIBBMISRC`.

Control flow/state: Make fragment only.

Dependencies/integration: Makes the generic list available to common, server, and BMI targets.

Risks: None specific; callers must include `llist.h` through normal dependency tracking.

Test signals: Link all target families that use `PINT_llist_*`.
