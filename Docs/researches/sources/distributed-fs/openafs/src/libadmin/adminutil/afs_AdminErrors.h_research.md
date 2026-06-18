## sources/distributed-fs/openafs/src/libadmin/adminutil/afs_AdminErrors.h

Purpose: `afs_AdminErrors.h` is an aggregate public header that includes all generated admin error-table headers.

Important contents: after `afs/param.h`, it includes BOS, client, common, KAS, misc, PTS, util, VOS, and config admin error headers.

State and persistence: no runtime state; it is installed as part of the admin utility API surface.

Dependencies and integration points: depends on generated headers from `adminutil/Makefile.in` and gives admin API consumers a single include for admin error constants.

Risks: build/install order matters because the included generated headers must exist in the include tree. This header does not include lower-level subsystem error tables, only admin-layer generated ones.

Test signals: successful compile of a consumer including `afs/afs_AdminErrors.h` after `adminutil` generation/install.
