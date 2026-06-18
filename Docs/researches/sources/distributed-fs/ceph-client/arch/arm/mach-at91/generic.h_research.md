# sources/distributed-fs/ceph-client/arch/arm/mach-at91/generic.h

Purpose: shared AT91 header declaring SoC-specific PM initialization hooks, with no-op inline stubs when `CONFIG_PM` is disabled.

Control flow is compile-time abstraction: machine files can call late PM init unconditionally without surrounding `#ifdef CONFIG_PM`. State and implementation live in PM source files. Dependencies are matching PM function definitions for enabled SoC families. Risks are declaration/definition drift and silently no-op PM init on non-PM builds. Test signals are compile coverage with CONFIG_PM enabled and disabled for each AT91 machine descriptor.
