<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/resource.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/resource.h

Purpose: defines resource identifiers for the admin-server Windows executable.

Important APIs/types/functions: `IDI_MAIN` is resource id 102. The `APSTUDIO_INVOKED` block sets default resource editor values such as `_APS_NEXT_RESOURCE_VALUE`, command, control, and symbol ids.

Control flow: no runtime logic. The resource compiler and Visual Studio resource editor consume these constants.

State and persistence: no runtime state or persistence.

Dependencies/integration: integrated with the admin-server `.rc` resource file and Windows executable icon loading.

Risks and test signals: low runtime risk. Build tests should ensure `IDI_MAIN` matches the resource script and that new resources do not collide with the reserved default range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/resource.h -->
