# sources/distributed-fs/lizardfs/src/master/acl_storage_unittest.cc

Purpose: unit test for `AclStorage` deduplication and mutation behavior.

Important APIs/functions: `TEST(AclStorageTests, Basic)` creates a `RichACL`, stores it under multiple inode IDs, compares returned pointers/values, erases one mapping, and updates mode on present/absent inodes.

Control flow: verifies identical ACLs share a single interned pointer, erasing one inode does not remove another inode's ACL, `setMode` on absent inode is a no-op, and `setMode` on a present inode re-interns a changed ACL without mutating the old interned object.

State and persistence: test-local in-memory state only.

Dependencies and integration: uses GoogleTest, `master/acl_storage.h`, and `RichACL::setMode`.

Risks: tests only basic interning; does not exercise high refcounts, hash collisions, or serialization integration.

Test signals: direct coverage for ACL storage core semantics.
