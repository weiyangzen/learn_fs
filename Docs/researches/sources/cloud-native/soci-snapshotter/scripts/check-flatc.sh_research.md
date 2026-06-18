# sources/cloud-native/soci-snapshotter/scripts/check-flatc.sh

Purpose: verifies generated Go flatbuffer files are up to date with ztoc and zinfo schemas.

Important APIs/types/functions: runs `flatc -o <tmp> -g` for `ztoc/fbs/ztoc.fbs` and `ztoc/compression/fbs/zinfo.fbs`, then diffs generated directories against checked-in generated code.

Control flow: generate into tempdir for ztoc, compare, cleanup; repeat for zinfo.

State and persistence: creates/removes temporary directories only; reads schema and generated code.

Dependencies/integration points: requires `flatc` installed, schema directory layout, and generated Go code under expected sibling folders.

Risks: exact generated output can vary by flatc version, so dependency version pinning matters. Failure path removes tempdir through shell expression but abrupt errors may leave temp dirs.

Test signals: CI guard for schema-generated code drift.
