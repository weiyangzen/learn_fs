# sources/control-plane/rook/deploy/examples/object-separate-pools-test.yaml

Purpose: creates explicit one-replica RGW pools for a test object store that uses separate pools rather than Rook-created defaults.

Important APIs/types/functions: eight `CephBlockPool` resources including `.rgw.root`, control, meta, log, buckets index, non-EC buckets, OTP, and buckets data pools, all labeled/applicationed for RGW usage with `pg_num`/autoscale test parameters.

Control flow: applying this prepares the pool topology that an object store can reference for separated RGW functions.

State and persistence: each pool stores a specific slice of RGW metadata or object data.

Dependencies/integration: intended for object store tests that require pre-created named pools.

Risks: small `pg_num`, autoscale off, and replica size 1 are not production safe.

Test signals: all pools exist and the object store using them reaches ready state.
