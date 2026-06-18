# sources/distributed-fs/orangefs/src/io/bmi/module.mk.in

## Purpose
Adds the BMI core source files to OrangeFS build source variables.

## Important APIs, Types, And Functions
This makefile fragment appends `bmi.c`, `bmi-method-support.c`, `op-list.c`, and `reference-list.c` to `LIBSRC`, `SERVERSRC`, and `LIBBMISRC` using `DIR := src/io/bmi`.

## Control Flow
The build system includes this fragment while composing library, server, and BMI-library compilation units. There is no runtime control flow.

## State And Persistence
No runtime state exists. The persistent effect is build membership for BMI core helper code.

## Dependencies And Integration Points
Integrates with OrangeFS automake-style `module.mk.in` aggregation. It intentionally does not list `bmi_zoid/zoid.c`, which is presumably gated by a method-specific build path.

## Risks And Test Signals
Risks are build omissions or duplicate object inclusion if source ownership changes. Test signals are configure/build success for client library, server binary, and BMI library targets.
