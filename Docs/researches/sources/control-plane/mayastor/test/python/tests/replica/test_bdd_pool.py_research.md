# sources/control-plane/mayastor/test/python/tests/replica/test_bdd_pool.py

Purpose: legacy pytest-bdd pool management coverage for invalid block sizes, duplicate names, aio pools, multi-disk rejection, destruction, missing destruction, and listing.

Important APIs and control flow: fixtures create `/tmp/ms0-disk0.img`, find pools through `ms.ListPools(pb.Null())`, track created pools for cleanup, and wrap `ms.CreatePool`. Step functions create malloc or aio pools, expect `INVALID_ARGUMENT` for invalid block size and multiple disks, create duplicate pools, destroy pools, and list pools. Then steps assert creation failure/success, destruction success, and listing membership.

State, dependencies, and integration: state is a live pool in `ms0` and a temporary aio image. It depends on legacy `mayastor_pb2`, pytest-bdd feature files, `common.command.run_cmd`, and `common.mayastor` fixtures.

Risks and test signals: duplicate pool creation and missing pool destruction do not explicitly wrap expected gRPC errors in this file, so scenario behavior relies on pytest-bdd failing on unhandled exceptions. Cleanup iterates tracked pool names and can fail if a test deletes a pool without removing it from the dictionary. Strong signals are enum-specific invalid-argument checks and post-operation `find_pool`/list assertions.
