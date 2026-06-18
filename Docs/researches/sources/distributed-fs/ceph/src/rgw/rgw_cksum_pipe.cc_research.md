# sources/distributed-fs/ceph/src/rgw/rgw_cksum_pipe.cc

Purpose: implements the put-object checksum pipe that streams incoming object data through a digest while forwarding data to the next SAL data processor.

Important APIs/types/functions: `RGWPutObj_Cksum` constructor, `RGWPutObj_Cksum::Factory()`, and `RGWPutObj_Cksum::process()`.

Control flow: factory first finds checksum headers in the request environment; known algorithms create a pipe, unknown or malformed headers throw `rgw::io::Exception(EINVAL)`. If no header exists but an override type is supplied, it creates a pipe using the synthetic SDK checksum-algorithm header mapping. `process()` updates the digest over every buffer segment, then forwards the moved bufferlist to the next pipe.

State/persistence: the pipe maintains digest variant, digest pointer, selected type, flags, current finalized `Cksum`, and selected header. Final checksum is stored by higher layers after upload processing.

Dependencies/integration: `rgw_cksum_pipe.h`, `rgw_cksum`, `RGWEnv`, SAL `DataProcessor`, put-object pipe chain, and `rgw_client_io` exceptions.

Risks: `_digest` is null for `Type::none`, but factory avoids constructing that except malformed paths. Override path may not fix the request environment, as noted by comment. Exceptions must be translated by REST upload paths.

Test signals: factory behavior for each checksum header source, unknown algorithm errors, override type, streaming multi-buffer digest, forwarding logical offsets, and final verification against request headers.
