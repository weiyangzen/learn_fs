<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_150.plist.in -->
# sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_150.plist.in

## Purpose
Darwin kernel-extension property-list template for the OpenAFS `afs` KEXT on the `x86` architecture family and Darwin `150` sysname. It supplies the bundle metadata copied by the Darwin libafs install/dest rules.

## Important APIs, Types, And Functions
The plist defines `CFBundleExecutable` `afs`, `CFBundleIdentifier` `org.openafs.filesystems.afs`, `CFBundleName` `afs`, `CFBundlePackageType` `KEXT`, version placeholders `@MACOS_VERSION@`, and `OSBundleLibraries` dependencies. This variant declares `com.apple.kpi.bsd`, `com.apple.kpi.mach`, and `com.apple.kpi.libkern` at `8.0.x`, with `CFBundleInfoDictionaryVersion` `8.0`.

## Control Flow
There is no executable flow. Configure/substitution fills `@MACOS_VERSION@`, Darwin make rules install the file as `Contents/Info.plist` inside `afs.kext`, and macOS KEXT loading uses the bundle keys and kernel-library dependency versions.

## State And Persistence
The file persists bundle identity and load requirements in the installed KEXT. It does not store runtime cache state or credentials.

## Dependencies And Integration Points
It integrates with `MakefileProto.DARWIN.in`, the generated Darwin `Info.plist`, Apple's KEXT loader, and the built `Contents/MacOS/afs` kernel binary. The architecture and Darwin version in the filename are the selection mechanism.

## Risks And Test Signals
Risks are stale kernel dependency versions, wrong architecture/sysname selection, malformed XML/plist syntax, and placeholder substitution failures. Test signals include `plutil` validation, correct `Info.plist` placement in `afs.kext`, successful code signing or local development loading where applicable, and KEXT load diagnostics that accept the declared KPI/kernel dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafs/afs.x86_darwin_150.plist.in -->
