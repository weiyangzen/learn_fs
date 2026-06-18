# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_release.h

Purpose: Declares the release dialog entry point and task packet for fileset release.

Important APIs/types: `SET_RELEASE_PARAMS` contains the read-write fileset identity and force flag. `Filesets_Release(LPIDENT)` starts the UI.

Control flow/state: The UI allocates `SET_RELEASE_PARAMS` and hands ownership to `taskSET_RELEASE`.

Dependencies/integration: Uses server manager identity types and the task layer.

Risks/test signals: Check task code treats `lpiRW` as read-write and handles forced releases consistently with the UI radio selection.
