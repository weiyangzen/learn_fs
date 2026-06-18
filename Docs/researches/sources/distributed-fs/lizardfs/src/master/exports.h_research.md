# sources/distributed-fs/lizardfs/src/master/exports.h

Purpose: public interface for master export information and authorization.

Important APIs/functions: `exports_info_size`, `exports_info_data`, `exports_check`, and `exports_init`.

Control flow: master initializes exports at startup, serves serialized export info to admin/status clients, and calls `exports_check` during client authentication.

State and persistence: state owned by `exports.cc`; backed by `mfsexports.cfg`.

Dependencies and integration: includes integer types and exposes protocol-level status via return codes and output parameters.

Risks: many output parameters must be non-null and interpreted consistently by callers; header does not document ownership because buffers are caller-provided.

Test signals: no direct tests in this subset.
