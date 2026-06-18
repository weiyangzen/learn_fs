# `sources/distributed-fs/ceph/src/osd/pg_features.h`

## Purpose

`pg_features.h` defines the feature-vector mechanism for capabilities supported by OSDs after a placement group becomes active. It mirrors the broad Ceph feature-bit style in a much smaller PG-local namespace and currently defines the `PCT` feature used by both Crimson and classic OSDs.

## Important APIs And Types

- `using pg_feature_vec_t = uint64_t` is the bit-vector type.
- `PG_FEATURE_INCARNATION_1` is the incarnation mask value used by feature definitions.
- `DEFINE_PG_FEATURE(bit, incarnation, name)` creates `PG_FEATURE_<name>` and `PG_FEATUREMASK_<name>`.
- `PG_HAVE_FEATURE(x, name)` tests whether a vector includes both the feature bit and the required incarnation mask.
- `PG_FEATURE_PCT`, `PG_FEATUREMASK_PCT`, `PG_FEATURE_NONE`, `PG_FEATURE_CRIMSON_ALL`, and `PG_FEATURE_CLASSIC_ALL` are the currently exported constants.

## Control Flow And State Behavior

There is no runtime control flow beyond macro expansion. `PG_HAVE_FEATURE()` performs a masked equality check, so a caller must pass a feature vector that includes the proper incarnation bit in addition to the feature bit. The all-feature constants currently map both Crimson and classic OSDs to `PG_FEATURE_PCT`.

## Persistence Behavior

The feature vector is embedded by users such as `pg_notify_t` in `osd_types.h`, so it participates in peering/wire state through those types, but this header itself has no encoder. Adding a feature changes negotiation semantics and must be coordinated with encode/decode versions and OSD feature compatibility wherever the vector is transmitted.

## Dependencies And Integration Points

The file intentionally has no includes. It is included by `osd_types.h` and is consumed by peering notification paths that need to know which active-PG behaviors are available. `PG_FEATURE_CRIMSON_ALL` and `PG_FEATURE_CLASSIC_ALL` connect classic and Crimson OSD implementations to the same feature mask.

## Risks And Edge Cases

- Feature-bit allocation is global within this 64-bit vector; duplicate bits would silently alias capabilities.
- `PG_HAVE_FEATURE()` requires the incarnation mask, so passing only `PG_FEATURE_PCT` without incarnation bits would fail the check.
- Adding a new incarnation or feature requires careful compatibility planning for mixed-version PGs.

## Test Signals

Compile-time tests can assert bit values and masks. Peering tests should cover mixed feature vectors and `pg_notify_t` propagation. Any new PG feature should include compatibility tests with old peers that lack the bit or required incarnation mask.
