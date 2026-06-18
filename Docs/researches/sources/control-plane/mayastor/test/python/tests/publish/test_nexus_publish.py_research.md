# sources/control-plane/mayastor/test/python/tests/publish/test_nexus_publish.py

Purpose: legacy Mayastor gRPC tests for nexus lifecycle around create, publish, unpublish, and destroy with a mixed child set. It builds children from a local malloc bdev, a remotely shared NVMf bdev, and temporary aio/uring files, then repeats lifecycle flows for five deterministic UUIDs.

Important APIs and control flow: helpers convert sizes, deterministic UUIDs, child URIs, and publish protocol enums. Fixtures create `BaseBdev` devices through `bdev.Create`, share the remote child via `bdev.Share`, create temporary 64 MiB files with `sudo truncate`, track created nexuses, and clean them via `DestroyNexus`. Tests call `CreateNexus`, `PublishNexus`, `UnpublishNexus`, and `DestroyNexus`, asserting the final `ListNexus` count is zero.

State, dependencies, and integration: persistent state is temporary `/tmp/*-file.img` files and live Mayastor in-container bdev/nexus state. It depends on `common.mayastor` docker-compose fixtures, `mayastor_pb2`, sudo, and NVMf sharing between `ms0` and `ms1`.

Risks and test signals: cleanup is fixture-driven but a failing publish/destroy path may leave nexuses or temp files behind. Only `nvmf` is parameterized despite enum support for nbd/iscsi. The strongest signal is leak detection by `nexus_count() == 0` after all lifecycle variants.
