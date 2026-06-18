# sources/distributed-fs/orangefs/src/common/dotconf/module.mk.in

Purpose: Build-fragment registration for the dotconf parser.

Important build variables: Sets `DIR := src/common/dotconf`, then appends `$(DIR)/dotconf.c` to `LIBSRC` and `SERVERSRC`.

Control flow/state: Makefile fragment only; it contributes source paths to higher-level build aggregation.

Dependencies/integration: Ensures the parser is linked into OrangeFS common library and server builds.

Risks: Does not add headers explicitly, relying on normal dependency scanning. Client or BMI builds that need dotconf would need separate source-list inclusion.

Test signals: Configure/build targets that consume `LIBSRC` and `SERVERSRC`, then confirm `dotconf.c` is compiled once per target.
