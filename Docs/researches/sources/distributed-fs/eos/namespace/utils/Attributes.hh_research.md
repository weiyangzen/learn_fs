# sources/distributed-fs/eos/namespace/utils/Attributes.hh

## Purpose
`Attributes.hh` provides inline helpers for EOS extended attribute lookup with support for linked attributes. A metadata object can carry `sys.attr.link` pointing to a container whose attributes are inherited unless overridden locally.

## Important APIs, Types, and Functions
The file defines attribute key constants `kAttrLinkKey`, `kAttrTmpEtagKey`, and `kAttrObfuscateKey`. `populateLinkedAttributes(const XAttrMap&, XAttrMap&, bool)` merges linked attributes without overriding existing keys and optionally rewrites linked `sys.*` keys to `sys.link.*`. `populateLinkedAttributes(IView*, XAttrMap&, bool)` follows `sys.attr.link` through the view. `listAttributes()` overloads handle `IContainerMD*`, `IFileMD*`, and `FileOrContainerMD`. Template `getAttribute()` retrieves a key locally first, then follows the linked container with prefetching and read locking.

## Control Flow
List operations clear and seed `out` from the target's own attributes, then call linked population. If the link is absent or empty, nothing else happens. If the linked container lookup fails, the link attribute is modified in output to append " - not found" and a debug log is emitted. `getAttribute()` first checks the target directly; if not present and no link exists it returns false. With a link, it prefetches, gets the container, acquires a read lock, checks for the key, and returns the linked value if present.

## State and Persistence Behavior
These helpers do not persist metadata changes. They build returned maps and strings from current metadata state. The only mutation is to the caller-provided output map when a linked container is missing.

## Dependencies and Integration Points
The file integrates `IView`, `Prefetcher`, string utilities, logging, and metadata locking. It is used by namespace exploration and user-facing metadata display paths that need effective attributes rather than only local attributes.

## Risks and Edge Cases
Linked attribute inheritance depends on `sys.attr.link` pointing to a directory; file links or missing paths are treated as not found. Prefixing applies only to inherited `sys.*` attributes, preserving non-system names. `getAttribute()` writes `errno` on link lookup failure, which can leak state into callers. Because this header is inline/template-heavy, changes can have broad rebuild impact.

## Test Signals
`VariousTests.cc` includes linked-attribute tests for containers, not-found links, overriding, and prefixing of inherited system attributes. Additional tests should cover `getAttribute()` on file metadata and prefetch failure behavior.
