# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_repprop.h

Purpose: Declares replication-property workflow entry points and the init packet populated by the async resolver.

Important APIs/types: `SET_REPPROP_INIT_PARAMS` stores requested identity, resolved RW identity, and `FILESETSTATUS`. `Filesets_ShowReplication` starts the workflow; `Filesets_OnEndTask_ShowReplication` handles init completion.

Control flow/state: The task layer fills `lpiRW` and `fs`; UI opens a cached properties sheet once the RW fileset is known.

Dependencies/integration: Integrates with task dispatch and fileset display/replica management modules.

Risks/test signals: Verify callers do not rely on the unused `lpiTarget` parameter without downstream support.
