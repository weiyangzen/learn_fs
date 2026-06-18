<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_depedencies.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_depedencies.h

Purpose: dependency aggregation header for DML2.0 code, intentionally without an include guard.

Important APIs/types/functions: declares no functions or types itself. It includes `os_types.h` and `cmntypes.h` to provide standard AMD display/DML type definitions.

Control flow: none.

State and persistence behavior: none.

Dependencies and integration points: used as a compatibility include target for DML code that expects shared standard types to be pulled in. The lack of guard is documented as intentional because the header is just an include bundle.

Risks and test signals: the filename contains the misspelling `depedencies`, so include paths must match exactly. Repeated inclusion is expected; adding declarations with side effects would be risky. Test signal is build coverage for files that include this compatibility header more than once or through generated DML sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml_depedencies.h -->
