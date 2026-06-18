# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/langres.h

## Purpose
Resource ID header for the sample extension plugin language resource DLL.

## Important APIs, Types, And Functions
Defines string/icon/dialog IDs for plugin description, credential-template text, config descriptions, and token method descriptions. Also contains Visual Studio `APSTUDIO_INVOKED` next-ID defaults.

## Control Flow
No executable control flow; it is included by C and resource compiler inputs.

## State And Persistence
Defines numeric identity of resources embedded into the sample language DLL.

## Dependencies And Integration Points
Used by sample `main.c`, `plugin.c`, config code, and `lang\en_us\langres.rc` built by the sample Makefile.

## Risks
Duplicate or changed IDs can desynchronize C `LoadString()` calls from resource content. The generated-file path in comments is historical and not authoritative.

## Test Signals
Resource compilation and runtime `LoadString()` success for plugin description and token method strings.
