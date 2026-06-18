# Research: sources/distributed-fs/openafs/src/platform/DARWIN/Makefile.in

Purpose: top-level Darwin platform build/install makefile for OpenAFS macOS UI/helper artifacts.

Important targets and control flow: `all` builds `OpenAFS.prefPane`, `afssettings`, `afscell`, `growlagent`, `aklog.bundle`, and `PrivilegedHelper`. Xcode projects build the preference pane, auth plugin, and installer pane. `afssettings` is compiled directly with Foundation. `growlagent` and `PrivilegedHelper` delegate to subdirectory makefiles. `dest` copies bundle outputs into `${DEST}/tools` and `${DEST}/installer`; `install` installs runtime command/helper components.

State and persistence: build outputs are under per-project `build` directories plus `afssettings`. Destination paths populate packaging trees and `${sbindir}`.

Dependencies and integration: includes OpenAFS config makefiles and pthread flags. Uses `xcodebuild`, compiler variables, `INSTALL`, and recursive make.

Risks: build depends on Xcode project files and legacy target names. `clean` removes broad build directories. Bundle copy targets use `rm -rf` on destination bundle paths.

Test signals: out-of-tree build, `DEST` package staging, `DESTDIR` install, clean idempotence, Xcode build flags propagation, and presence of all expected bundle artifacts.
