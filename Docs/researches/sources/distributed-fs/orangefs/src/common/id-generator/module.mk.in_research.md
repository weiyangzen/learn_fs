# sources/distributed-fs/orangefs/src/common/id-generator/module.mk.in

Purpose: Build-fragment registration for the ID generator implementation.

Important build variables: Sets `DIR := src/common/id-generator`, then appends `id-generator.c` to `LIBSRC`, `SERVERSRC`, and `LIBBMISRC`.

Control flow/state: Make fragment only.

Dependencies/integration: Makes safe ID registry available to common, server, and BMI targets.

Risks: None beyond normal source-list duplication concerns.

Test signals: Link all three target families with ID generator call sites.
