# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_delete_test.go

Purpose: unit-tests delete path safety and low-level unversioned delete request construction. It focuses on traversal prevention and the `metadataOnly` flag's translation to filer delete semantics.

Important coverage includes `TestValidateDeleteObjectIdentifier`, `TestGetSpecificObjectVersionRejectsUnsafeVersionID`, `TestDeleteUnversionedObjectWithClient_MetadataOnlySkipsChunkDelete`, `TestDeleteUnversionedObjectWithClient_FullDeletePreservesIsDeleteData`, `TestDeleteUnversionedObjectWithClient_FullPathFromBucketsRoot`, `TestDeleteUnversionedObjectWithClientRejectsTraversal`, and `TestDeleteUnversionedObjectWithClient_PropagatesEntryAttributesIrrelevant`.

Control flow uses table-driven invalid key/version cases with traversal segments and backslashes, calls version lookup with an unsafe version ID, and uses a fake delete client to inspect generated filer `DeleteEntryRequest` fields. It verifies metadata-only delete clears `IsDeleteData`, normal delete sets it, nested object keys split into directory/name correctly, invalid paths are rejected before RPC, and entry attributes do not influence this helper.

State and persistence are in-memory test server structs and request captures. No real filer mutation occurs.

Dependencies include `testify`, `filer_pb`, `s3err`, `errInvalidVersionID`, and the package test fake `deleteObjectEntryTestClient`. Integration point is the delete handler and lifecycle callers that rely on `deleteUnversionedObjectWithClient`.

Risks: the tests do not cover full HTTP DeleteObject/DeleteObjects, version marker creation, object-lock enforcement, or routed delete branches. They are strong guards for path safety and data-delete flag behavior, which are high-impact failure modes.
