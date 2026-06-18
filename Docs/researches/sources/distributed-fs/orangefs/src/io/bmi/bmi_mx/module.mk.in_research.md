# sources/distributed-fs/orangefs/src/io/bmi/bmi_mx/module.mk.in

## Purpose
Build-system fragment for the OrangeFS BMI MX transport. It conditionally adds the MX implementation source to the library, server, and BMI library builds when configure enables MX support.

## Important APIs, Types, And Functions
The relevant make variables are `BUILD_MX`, `DIR`, `cfiles`, `src`, `LIBSRC`, `SERVERSRC`, `LIBBMISRC`, and `MODCFLAGS_$(DIR)`. The only source listed is `mx.c`, and MX headers are supplied through `-I@MX_INCDIR@`.

## Control Flow
If `BUILD_MX` is empty, the fragment contributes nothing. Otherwise it sets `DIR := src/io/bmi/bmi_mx`, expands `mx.c` to a source-tree path, appends that source to all three build source lists, and applies the configured MX include directory to the module.

## State And Persistence
This file has no runtime state. Its persistent effect is generated build metadata deciding whether the MX BMI transport is compiled and linked.

## Dependencies And Integration Points
It depends on configure detecting MX and substituting `@MX_INCDIR@`. It integrates the sibling `bmi_mx/mx.c` transport with the same top-level build variables used by other BMI modules.

## Risks And Test Signals
The main risks are stale configure detection, missing MX headers, and accidental omission from one of the build products if top-level variable semantics change. Test signals include a configure/build with `BUILD_MX` enabled, compile checks for `mx.c` against `@MX_INCDIR@`, and a disabled-MX build confirming the fragment is skipped cleanly.
