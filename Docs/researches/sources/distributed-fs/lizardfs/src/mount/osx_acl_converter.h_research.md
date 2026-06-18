## sources/distributed-fs/lizardfs/src/mount/osx_acl_converter.h

Purpose: declares macOS ACL conversion helpers and `AclConversionException`.

Important APIs: namespace `osxAclConverter` provides `extractAclObject(const void*, size_t)` returning `RichACL` and `objectToOsxXattr(const RichACL&)` returning serialized xattr bytes.

Dependencies and integration: depends on `common/exception`, `common/richacl`, `mount/lizard_client`, and `sys/acl.h`; used by mount xattr/ACL handling on Apple builds.

Risks: declarations are platform-specific because `sys/acl.h` here means Apple's ACL API, not libacl. Non-Apple build inclusion must be guarded by the build system or platform headers.
