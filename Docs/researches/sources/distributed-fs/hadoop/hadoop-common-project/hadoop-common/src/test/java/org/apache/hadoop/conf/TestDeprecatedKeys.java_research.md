# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestDeprecatedKeys.java

## Purpose

`TestDeprecatedKeys` is a compact regression suite for deprecated configuration key compatibility. It validates a built-in deprecated key, XML write behavior after deprecation registration, and iteration/value propagation when one deprecated key maps to multiple replacement keys.

## Important APIs and types

- `Configuration.addDeprecation(String, String[])`.
- `Configuration.set`, `setBoolean`, `get`, `writeXml`, and `iterator`.
- `CommonConfigurationKeys.NET_TOPOLOGY_SCRIPT_FILE_NAME_KEY` as the replacement for `"topology.script.file.name"`.

## Control flow

`testDeprecatedKeys` sets the old topology script key and reads the modern common key. `testReadWriteWithDeprecatedKeys` sets an old key before registering deprecation, writes XML, and checks that both old and new names appear. `testIteratorWithDeprecatedKeysMappedToMultipleNewKeys` registers `"dK"` to `"nK1"` and `"nK2"`, repeatedly updates old and new names, checks alias values, and confirms iteration exposes all aliases plus a normal key.

## State and persistence behavior

The tests are in-memory and use a `ByteArrayOutputStream` for XML. Deprecation registration mutates global `Configuration` static state with simple test key names, so repeated execution depends on idempotent deprecation handling.

## Dependencies and integration points

This file overlaps with broader deprecation tests but covers specific public/common constants and XML serialization. It guards compatibility for users who still set legacy config keys.

## Risks and edge cases

- The test key names are very short and global; they can collide with other tests if deprecation state is not isolated.
- XML assertions are substring-based and do not validate structure or final/source metadata.
- Multi-new-key semantics are order-sensitive: later updates to one alias propagate to all aliases.

## Test signals

The file gives quick signals that old keys still read through new constants, deprecation registration after setting still affects XML output, and iterators include both deprecated and replacement keys with synchronized values.
