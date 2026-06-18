# sources/distributed-fs/orangefs/src/apps/karma/module.mk.in

## Purpose
This makefile fragment conditionally adds the Karma GTK monitoring application to the OrangeFS build when `BUILD_KARMA` is enabled.

## Important APIs, Types, and Functions
The important build variables are `KARMASRC`, listing all Karma C modules except the header; `KARMA := $(DIR)/karma`, defining the binary target; `MODCFLAGS_$(DIR) := @GTKCFLAGS@`; and `MODLDFLAGS_$(DIR) := @GTKLIBS@`. Under `GNUC`, it appends `-Wno-strict-prototypes` because GTK2 headers expose prototypes that trigger warnings.

## Control Flow
The whole fragment is guarded by `ifdef BUILD_KARMA`. If enabled, the listed source files are compiled and linked with configure-substituted GTK flags. If disabled, no Karma target is built.

## State and Persistence
The file affects build outputs only. It does not participate in runtime state.

## Dependencies and Integration Points
It depends on configure-time GTK detection and on top-level make rules that understand `KARMASRC`, `KARMA`, `MODCFLAGS_*`, and `MODLDFLAGS_*`. It integrates all Karma modules into one executable.

## Risks and Edge Cases
If a new Karma source is added but omitted here, the build may fail at link time or silently miss functionality. The warning suppression can hide real strict-prototype issues in local code as well as GTK headers. GTK2 availability is a hard requirement when `BUILD_KARMA` is set.

## Test Signals
Build with `BUILD_KARMA` on and off. Enabled builds should include all listed C files and link with GTK libraries. Compiler/linker failures are likely to reveal missing source-list entries or stale GTK configure substitutions.
