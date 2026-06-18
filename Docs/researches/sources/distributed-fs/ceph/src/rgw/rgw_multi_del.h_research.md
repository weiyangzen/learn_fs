## sources/distributed-fs/ceph/src/rgw/rgw_multi_del.h

Purpose: declares multi-object delete XML parser classes and delete dispatch callback types.

Important APIs/types: `RGWMultiDelObject` exposes key, version id, optional ETag, last-modified time, and size match. `RGWMultiDelDelete` stores `objects` and `quiet`. Leaf XML classes represent `Quiet`, `Key`, and `VersionId`. `rgw::multi_delete::Item`, `Exec`, `OnDispatch`, and `dispatch()` define async delete scheduling.

Control flow: RGW delete operations parse XML into `RGWMultiDelDelete`, convert objects to dispatch `Item`s, then call `dispatch()` with an executor that performs actual deletes.

State and persistence: only request-local parsed state. Object deletion and OLH updates are delegated to executor code.

Dependencies/integration: includes Boost.Asio spawn/yield, RGW XML/common types, and `rgw_obj_key`.

Risks and test signals: accessors expose optional/precondition data used by conditional delete logic; tests should assert defaults for absent optional elements and correct values for parsed XML.
