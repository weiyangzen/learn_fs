# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/Makefile

## Purpose
NMAKE sample build file for a third-party AFS NetIDMgr extension plugin.

## Important APIs, Types, And Functions
Defines plugin/module/auth method names, DLL basename, version macros, environment checks (`MSSDK`, `KFWSDKDIR`, `AFSPLUGINDIR`, `CPU`), output directories, compiler/resource/message compiler/linker macros, manifest embedding helpers, generated `credacq_config.h`, main DLL target, and language resource DLL target.

## Control Flow
`all` creates directories, generates `credacq_config.h`, builds the plugin DLL from `afspext.obj`, `main.obj`, `plugin.obj`, and `config_main.obj`, then builds language resources. Pattern rules compile C and RC files. Clean targets remove object, destination, generated config, DLLs, and resources.

## State And Persistence
Produces `dest\<CPU>_<debug|release>` and `obj\<CPU>_<debug|release>` trees plus generated headers and DLLs. It does not mutate source beyond generated output directories.

## Dependencies And Integration Points
Requires Visual Studio/Platform SDK `Win32.Mak`, KfW SDK libraries/includes, AFS plugin headers, NetIDMgr import library, Windows resource compiler, linker, manifest tool, and sample language resources.

## Risks
The template ships with TODO placeholder names and version fields. It assumes classic NMAKE syntax and Visual Studio manifest macros. Missing `AFSPLUGINDIR` or SDK layout mismatch stops the build.

## Test Signals
Run debug and release builds with real SDK paths; verify generated `credacq_config.h`, plugin DLL link against `nidmgr32.lib`, manifest embedding, and `*_en_us.dll` resource output.
