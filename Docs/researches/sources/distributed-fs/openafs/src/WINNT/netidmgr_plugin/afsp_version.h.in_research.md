# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsp_version.h.in

## Purpose
NMAKE-style template that generates `afsp_version.h` by copying a literal header body with substituted build variables for plugin version components.

## Important APIs, Types, And Functions
It emits macros for major, minor, patch, auxiliary version fields, aggregate numeric/string version, and comma-list version data. There are no C functions.

## Control Flow
The make target `afsp_version.h: afsp_version.h.in` uses `$(COPY) << $@` heredoc syntax to produce the final header. Build variables such as `$(AFSPLUGIN_VERSION_MAJOR)` and `$(AFSPLUGIN_VERLIST)` must be defined by the surrounding build system.

## State And Persistence
The generated header becomes build artifact state consumed by resource/version compilation. The template itself is static source.

## Dependencies And Integration Points
Integrated with Windows/NMAKE build rules and version resource files. It assumes Secure Endpoints/OpenAFS plugin version variables are set before target evaluation.

## Risks
Missing or malformed make variables generate invalid C preprocessor output. Because it is not a normal C preprocessor template, tools that expect plain C may misread it.

## Test Signals
Validation is a build of the generated `afsp_version.h` and any version resource using `AFSPLUGIN_VERSION_LST`.
