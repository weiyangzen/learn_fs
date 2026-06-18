# sources/distributed-fs/orangefs/src/io/job/module.mk.in

## Purpose
This makefile fragment registers the job subsystem sources with the OrangeFS build.

## Important entries
It sets `DIR := src/io/job` and appends `job.c`, `job-desc-queue.c`, `thread-mgr.c`, and `job-time-mgr.c` to both `LIBSRC` and `SERVERSRC`.

## Control flow and build behavior
The fragment has no runtime control flow. Build inclusion is simple and duplicated: the same job implementation is compiled into the general library source set and into server source builds.

## State, persistence, and dependencies
No state or persistence is defined here. The dependency signal is architectural: the job subsystem is both client/library-facing and server-facing, so changes to its ABI or build guards can affect both deployment shapes.

## Risks
Because the fragment lists the same files in two source variables, any new job subsystem file must be added consistently to both unless it is intentionally server-only or library-only. Formatting uses backslash continuations without spaces after some filenames, so mechanical edits should preserve make syntax carefully.

## Test signals
Build tests should confirm both library and server targets still compile after any source-list change, especially with `__PVFS2_JOB_THREADED__`, `__PVFS2_CLIENT__`, and TROVE support variants.
