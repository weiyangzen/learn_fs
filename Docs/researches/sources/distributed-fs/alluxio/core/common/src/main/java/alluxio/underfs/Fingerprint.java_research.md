<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/Fingerprint.java -->
# sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/Fingerprint.java

Purpose: serializable metadata/content fingerprint for UFS files and directories. It captures type, UFS type, owner, group, mode, optional content hash, and optional ACL for change detection.

Important APIs and control flow: `create` builds tag maps from `UfsStatus`, optional content hash, and optional ACL; files include `CONTENT_HASH`, directories do not. `parse` converts serialized `TAG|value` pairs back into a fingerprint and validates required tags. `serialize` emits required tags first then optional tags. `matchMetadata` compares owner/group/mode/ACL; `matchContent` compares type/UFS/content hash. `putTag` sanitizes values by replacing pipe and space with underscores, while missing tags read as `_`.

State, persistence, and integration: state is an internal mutable `Map<Tag,String>` despite final class and not-thread-safe annotation. Dependencies include Alluxio constants/status classes, ACL stringification, Guava `Splitter`, Apache `StringUtils`, and UFS type names. Risks include parse throwing on malformed enum names/key-value strings, lossy sanitization causing collisions, missing optional tags comparing as `_`, and mutable fingerprints after creation. Test signals should cover invalid fingerprints, serialization ordering, ACL inclusion, file versus directory content matching, and sanitization behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/Fingerprint.java -->
