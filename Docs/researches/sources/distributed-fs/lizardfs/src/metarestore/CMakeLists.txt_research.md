# sources/distributed-fs/lizardfs/src/metarestore/CMakeLists.txt

## Purpose

`src/metarestore/CMakeLists.txt` builds the `mfsmetarestore` library, tests, and executable used to restore metadata from metadata files plus changelogs. The source was read as a complete 29-line CMake file.

## Important APIs, Types, and Functions

It includes current and master directories, defines `METARESTORE`, `APPNAME=mfsmetarestore`, and docs subdir, collects metarestore sources, globs master filesystem sources, selects hstring storage implementation based on DB availability, builds a `metarestore` library with master metadata/restore/chunks/quota/task/snapshot/setgoal/settrashtime/locks dependencies, links `mfscommon` and optional Judy, creates unit tests, builds `mfsmetarestore`, links PAM, and installs it.

## Control Flow

CMake configure selects the source set and optional libraries; build flow compiles a master-like metadata engine under `METARESTORE` definitions so changelogs can be replayed offline.

## State and Persistence Behavior

The build file itself has no runtime state. It produces an executable that reads metadata/changelogs and writes restored metadata according to metarestore source behavior.

## Dependencies and Integration Points

This target is deeply integrated with master filesystem implementation files, `restore.cc`, quota database, task manager, snapshot and recursive set operations, hstring storage, common code, optional DB/Judy support, PAM, and project test/install macros.

## Risks and Edge Cases

Globbed master filesystem sources can unintentionally include or omit files as the master changes. `METARESTORE` compile definitions disable or alter runtime service integrations, so source code must keep conditional paths correct. Pulling many master files into an offline tool risks link drift when master dependencies change.

## Test Signals

Build `metarestore` and `mfsmetarestore`, run metarestore unit tests, replay fixture changelogs containing snapshot/setgoal/settrashtime/quota/lock operations, and verify restored metadata checksums against master-generated metadata.
