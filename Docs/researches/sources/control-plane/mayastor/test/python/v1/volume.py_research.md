# sources/control-plane/mayastor/test/python/v1/volume.py

Purpose: small helper object intended to create a volume by creating replicas on pool URIs and publishing a nexus on a target node.

Important APIs and control flow: `Volume.__init__` stores UUID, nexus node URI, pool URIs, and size. `__parse_uri` splits URIs with `urlparse`. `__create_replicas` expects `pool://host/pool_name`, opens a `MayastorHandle`, lists the named pool to get UUID, creates an NVMf shared replica with fixed name `"replica-1"` and the volume UUID, and returns replica responses. `create` expects `nvmt://host`, converts replica URIs into children, creates a handle, calls `nexus_create`, publishes the nexus, and returns device URI.

State, dependencies, and integration: state spans remote pool lookup, replica creation on each pool, and nexus creation/publish on the target. It depends on `MayastorHandle`, `urlparse`, `common_pb2.NVMF`, and `pool_pb2.ListPoolOptions`.

Risks and test signals: `create` calls `handle.nexus_create(self.uuid, self.size, replicas)` but `MayastorHandle.nexus_create` requires name, uuid, size, controller IDs, reservation keys, and children; this helper appears stale. Fixed replica names can collide. It is indirectly exercised by `test_enospace_on_volume`.
