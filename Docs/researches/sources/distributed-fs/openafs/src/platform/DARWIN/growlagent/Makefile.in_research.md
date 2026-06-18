# sources/distributed-fs/openafs/src/platform/DARWIN/growlagent/Makefile.in

## Purpose
Builds the Darwin `growlagent-openafs` helper, an Objective-C notification bridge for OpenAFS Venus Monitor events. The makefile compiles `main.o`, links it as an executable against Apple `Security`, `AppKit`, and `CoreFoundation`, and packages it into a `.app` layout for destination installs.

## Important APIs, Types, And Functions
The important targets are `all`, `growlagent-openafs`, `main.o`, `clean`, `install`, and `dest`. `main.o` depends on `GrowlDefines.h` and `GrowlPathway.h`, reflecting the source file's Growl bridge API surface. The `dest` target creates `Contents/MacOS`, `Contents/Resources/MacOS`, and `Contents/Resources`, then installs the executable, `Andy.icns`, and `Info.plist`.

## Control Flow
Normal build flow includes repository configuration and pthread rules, compiles `main.m` through the implicit rules, then runs `$(AFS_LDRULE)` with the required Cocoa/CoreFoundation frameworks. The packaging path is destination-only; `install` is intentionally empty, while `dest` stages an app bundle under `${DEST}/tools/growlagent-openafs.app`.

## State And Persistence
The only persistent artifacts are `main.o`, `growlagent-openafs`, and staged bundle contents. `clean` removes local objects and the executable but not installed bundles.

## Dependencies And Integration Points
Depends on top-level OpenAFS make configuration, Apple frameworks, and Growl headers/resources in the same directory. It integrates Darwin packaging with the broader OpenAFS `DEST` staging model.

## Risks And Test Signals
Risks are obsolete Growl framework assumptions, app bundle path correctness, and the empty `install` target differing from `dest`. Test signals are a successful Darwin build, correct framework linkage, bundle launchability, and presence of `Info.plist` and icon resources in the staged app.
