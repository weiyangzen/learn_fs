# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/UnresolvedLinkException.java

## Purpose
Checked IOException signaling that a filesystem symlink or link-like path component could not be resolved.

## Important APIs, Types, and Functions
Constructors: no-arg and message constructor. Public type extends IOException.

## Control Flow
No internal flow; callers throw it during link resolution and higher layers may retry through FileContext/FSLinkResolver.

## State and Persistence Behavior
No state beyond IOException message/stack.

## Dependencies and Integration Points
Integrated with FSLinkResolver, FileContext, AbstractFileSystem, and path resolution code.

## Risks and Test Signals
Compatibility risk is exception taxonomy. Tests should verify symlink resolution APIs surface this specific checked type where expected.
