# sources/distributed-fs/ceph-client/drivers/pmdomain/Makefile

Purpose: top-level Kbuild file for PM-domain support.

Important APIs/types/functions: unconditionally descends into PM-domain vendor subdirectories with `obj-y += <dir>/` and builds common `core.o` and `governor.o`.

Control flow: no runtime control flow. Kbuild uses child Makefiles and Kconfig-resolved `obj-*` entries to select built-in or modular objects.

State and persistence: persistent effect is build composition: common generic PM-domain core/governor objects plus enabled provider drivers.

Dependencies/integration: must stay aligned with the top-level Kconfig source list and the directory names under `drivers/pmdomain`.

Risks: stale or missing directory entries break builds for visible Kconfig symbols; building `core.o governor.o` here is central to genpd availability.

Test signals: `make drivers/pmdomain/` and randconfig builds with representative provider symbols enabled.
