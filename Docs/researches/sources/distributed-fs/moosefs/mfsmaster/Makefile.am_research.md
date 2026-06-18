# sources/distributed-fs/moosefs/mfsmaster/Makefile.am

## Purpose
`mfsmaster/Makefile.am` is the Automake manifest for master-side binaries: `mfsmaster`, `mfsstatsdump`, and `mfssupervisor`.

## Important targets and integration
`sbin_PROGRAMS` installs the binaries. `mfsstatsdump_SOURCES` builds the chart/stat dump utility with common chart, CRC, log, and string-error code. `mfsmaster_SOURCES` lists master runtime modules for filesystem metadata, chunks, sessions, locks, storage classes, topology, client/chunkserver/listener protocols, background saving, restore, and shared `mfscommon` utilities. `mfsmaster_CPPFLAGS` defines `MFSMAXFILES=16384` and `APPNAME=mfsmaster`; zlib is linked where needed. `mfssupervisor` builds from supervisor and common socket/clock/log/protocol code with `MFSSUPERVISOR=1`.

## Persistence and risks
Persistence-related modules include `metadata`, `changelog`, `restore`, `bgsaver`, `missinglog`, filesystem, chunks, and sessions. Build-manifest omissions can remove runtime behavior, so `make distcheck`, clean builds, package script checks for `mfsmetarestore`, and flag-variant builds are important signals.
