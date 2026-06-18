# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/EdgeEntry.java

Purpose: simple immutable representation of a resolved inode edge and the child inode id it points to.

Important APIs and types: constructor stores parent id, child name, and child id. Getters expose each field.

Control flow: edge iteration or lookup code can return `EdgeEntry` to provide both the edge key and the target inode id without loading a full inode object.

State and persistence behavior: value object only. It mirrors persisted edge/inode-store relationships but owns no persistence.

Dependencies and integration points: no external dependencies beyond core Java. Integrates with inode store and traversal code that need compact edge records.

Risks: no equality/hash code or validation, so it is best suited as a transport record rather than a set key. Callers must ensure parent/child ids and names are consistent with the inode store.

Test signals: getter tests are enough at unit level; meaningful coverage comes from inode store edge iteration tests.
