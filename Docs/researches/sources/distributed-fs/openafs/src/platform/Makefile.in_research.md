# sources/distributed-fs/openafs/src/platform/Makefile.in

## Purpose
Provides the common dispatcher makefile for `src/platform`, routing standard targets into the OS-specific subdirectory named by `$(MKAFS_OSTYPE)`.

## Important APIs, Types, And Functions
Targets are `all`, `clean`, `dest`, and `install`. Each target performs `cd $(MKAFS_OSTYPE) && $(MAKE) ...`, passing `DEST` or `DESTDIR` for staging/install targets.

## Control Flow
Top-level builds enter `src/platform`, include `Makefile.config`, and delegate work to exactly one platform directory. Version generation is included through `../config/Makefile.version`.

## State And Persistence
This file creates no artifacts directly; all state is produced by the selected platform child makefile.

## Dependencies And Integration Points
Depends on `MKAFS_OSTYPE` from OpenAFS configuration and on the existence of a matching subdirectory with compatible targets. It integrates Darwin, IRIX, Solaris, BSD, Linux, and other platform directories into the main build.

## Risks And Test Signals
Risks include unset or mismatched `MKAFS_OSTYPE`, missing platform directories, and target incompatibility in child makefiles. Test signals are successful target delegation for every configured OS type and correct propagation of destination variables.
