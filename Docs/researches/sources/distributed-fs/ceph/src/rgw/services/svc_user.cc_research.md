<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_user.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_user.cc

Purpose: Provides the trivial constructor/destructor implementation for the abstract user service base.

Important APIs, types, and functions: `RGWSI_User::RGWSI_User(CephContext*)` forwards to `RGWServiceInstance`; `~RGWSI_User()` is empty.

Control flow: Concrete user services derive from this base and implement all persistence/index operations.

State and persistence: No state or persistence in this file.

Dependencies and integration points: Depends on `svc_user.h`. Used by `RGWSI_User_RADOS`.

Risks and test signals: Minimal risk. Compile/link tests ensure the abstract base has a definition for constructor/destructor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_user.cc -->
