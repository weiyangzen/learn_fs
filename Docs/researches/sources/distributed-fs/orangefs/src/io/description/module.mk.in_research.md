# sources/distributed-fs/orangefs/src/io/description/module.mk.in

## Purpose
Adds request-description and distribution source files to OrangeFS library and server builds.

## Important APIs, Types, And Functions
Appends `pvfs-request.c`, `pint-request.c`, `pint-distribution.c`, `pint-dist-utils.c`, `dist-basic.c`, `dist-simple-stripe.c`, `dist-varstrip-parser.c`, `dist-twod-stripe.c`, and `dist-varstrip.c` to both `LIBSRC` and `SERVERSRC`.

## Control Flow
No runtime control flow. It controls which distribution and request-description modules are compiled into client/library and server targets.

## State And Persistence
No runtime state exists. Build membership is the persistent project effect.

## Dependencies And Integration Points
Integrates all built-in distributions and request encoders with both client and server code, which is necessary because distributions are encoded/decoded and evaluated on both sides.

## Risks And Test Signals
Risks are build omissions if a new distribution is added without this file, or duplicate registration if sources are included twice elsewhere. Configure/build success and distribution availability tests are signals.
