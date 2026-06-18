# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/template-component-messages.h

Purpose: `template-component-messages.h` is a template for defining stable component-scoped structured log/message IDs.

Important APIs and types: it includes `glfs-message-id.h` and documents use of `GLFS_COMPONENT`, `GLFS_NEW`, `GLFS_OLD`, and `GLFS_GONE`. The file intentionally contains no real component messages.

Control flow and state: no runtime behavior. It is a developer template and compile-time message catalog pattern.

Dependencies and integration: integrates with structured logging macros in `logging.h`, especially `gf_smsg` and `GF_LOG_*` generated-data macros. Components copy/adapt this template to add message definitions.

Risks: message ordering is stable ABI/user-facing behavior. Adding messages anywhere but the end changes IDs. Removing IDs can cause reuse, so deprecation must leave placeholders. The template guard `_component_MESSAGES_H_` must be renamed for real components.

Test signals: generated message headers should compile, message IDs should remain stable across releases, and logging tests should verify new/old/gone behavior in structured logs.
