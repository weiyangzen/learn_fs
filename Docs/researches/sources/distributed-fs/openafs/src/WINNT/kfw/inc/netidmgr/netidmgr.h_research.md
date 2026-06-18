# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/netidmgr.h

## Purpose

`netidmgr.h` is the umbrella include for the NetIDMgr SDK subset carried in the OpenAFS Windows tree. It gives plugins one stable include that pulls together definitions for utilities, UI, message queues, credential database access, configuration, modules, and plugin declarations.

## Important APIs, types, and functions

This file declares no functions of its own. It includes `khdefs.h`, `utils.h`, `khuidefs.h`, `kmq.h`, `khmsgtypes.h`, `kcreddb.h`, `kherr.h`, `kherror.h`, `kconfig.h`, `kmm.h`, and `kplugin.h`.

## Control flow

There is no runtime control flow. Compile-time control is the include guard `__NETIDMGR_H`, which prevents duplicate inclusion.

## State and persistence behavior

The header owns no state. It exposes APIs whose implementations manage credential state, configuration state, module state, and UI state elsewhere.

## Dependencies and integration points

The AFS credential plugin includes this through `afscred.h`, making NetIDMgr message queues, credential attributes, configuration spaces, plugin callbacks, error reporting, and UI configuration APIs available throughout the plugin.

## Risks and edge cases

As an umbrella header, the main risk is accidental dependency expansion and include-order coupling. The included headers expose Windows and NetIDMgr types broadly, so consumers may compile only in the expected NetIDMgr/KfW environment.

## Test signals

Build validation is the primary signal: plugin sources should compile when including only `netidmgr.h` through `afscred.h`, and duplicate inclusion should not redefine symbols.
