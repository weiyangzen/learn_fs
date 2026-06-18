# sources/distributed-fs/seaweedfs/weed/filer/mongodb/mongodb_store_kv.go

## Purpose

`mongodb_store_kv.go` implements the generic filer KV API on top of the same MongoDB `filemeta` collection used for metadata. It maps arbitrary byte keys into synthetic directory/name document fields.

## Important APIs, Types, and Functions

The public methods are `KvPut`, `KvGet`, and `KvDelete`. `genDirAndName` pads keys shorter than eight bytes and splits the first eight bytes into `directory` and the remainder into `name`.

## Control Flow

KV put computes synthetic directory/name, then performs an upsert setting `meta` to the raw value. KV get finds one matching document, maps query failure or empty meta to `filer.ErrKvNotFound`, and returns the stored bytes. KV delete removes one matching document.

## State and Persistence Behavior

KV state persists in the `filemeta` collection with the same fields and unique index as metadata. Values are raw bytes in `meta`. Short keys are zero-padded locally before splitting, so the effective key is padded to at least eight bytes.

## Dependencies and Integration Points

The file depends on `MongodbStore` connection fields, Mongo BSON builders, and the filer KV error contract. It is used by shared filer components such as metadata offset tracking.

## Risks and Edge Cases

KV documents share the metadata collection and could collide with real metadata documents if synthetic directory/name values overlap. Empty values are treated as not found because `KvGet` checks `len(data.Meta) == 0`. `genDirAndName` mutates its local slice by appending zeros, which is safe for caller data but important for key semantics.

## Test Signals

Tests should cover short and long binary keys, empty value behavior, put/get/delete, collision isolation from metadata paths, and query error handling.
