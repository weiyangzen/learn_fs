# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_delete.h

Purpose: Declares service deletion UI entry point.

Important APIs/types: `Services_Delete(LPIDENT)` prompts for confirmation and dispatches deletion.

Control flow/state: The target identity is passed to `taskSVC_DELETE` on OK.

Dependencies/integration: Called from service tab/property/context commands.

Risks/test signals: Ensure command gating excludes BOS and null identities before calling.
