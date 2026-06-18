# sources/compression/zlib/os400/make.sh

## Purpose
`os400/make.sh` is the IBM i / OS/400 build script for zlib, used where standard `make` is not assumed. It creates library objects, copies headers/docs, compiles modules, and builds static/dynamic binding directories and a service program.

## Important APIs, Types, and Functions
Shell procedures include `action_needed()`, `make_module()`, `db2_name()`, and `copy_hfile()`. Tunable variables include `TARGETLIB`, `STATBNDDIR`, `DYNBNDDIR`, `SRVPGM`, `IFSDIR`, `TGTCCSID`, `DEBUG`, `OPTIMIZE`, `OUTPUT`, and `TGTRLS`.

## Control Flow, State, and Persistence
The script resolves `TOPDIR`, extracts `VERSION` from `treebuild.xml`, creates OS/400 library/source-file objects, copies documentation and headers with target CCSID conversion, installs RPG headers, generates and compiles `os400.c`, compiles all XML-listed C sources into modules, rebuilds binding directories when needed, copies binder source, creates the service program, duplicates a versioned backup, and updates dynamic bindings. Persistent outputs are OS/400 library members, IFS include symlinks, modules, binding directories, and service programs.

## Dependencies and Integration Points
It depends on IBM i commands such as `CRTLIB`, `CRTSRCPF`, `CPY`, `CHGPFM`, `CRTCMOD`, `CRTBNDDIR`, `ADDBNDDIRE`, `CRTSRVPGM`, `CRTDUPOBJ`, and `system`, plus `treebuild.xml`.

## Risks and Test Signals
Risks include shell quoting in generated commands, stale dependency detection from XML/header timestamps, CCSID conversion issues, DB2 name truncation collisions, and accidental rebuild/link churn. Test signals are successful clean and incremental OS/400 builds, correct exported service program, valid include symlinks, and module recompilation when headers change.
