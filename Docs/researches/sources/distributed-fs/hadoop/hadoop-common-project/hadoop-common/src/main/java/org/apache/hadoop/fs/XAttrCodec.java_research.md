# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/XAttrCodec.java

## Purpose
Enum and helpers for extended-attribute value string encodings used by shell, HTTP, and JSON-facing paths.

## Important APIs, Types, and Functions
Enum values TEXT, HEX, BASE64; decodeValue(String); encodeValue(byte[], XAttrCodec).

## Control Flow
decodeValue recognizes quoted text, 0x/0X hex, 0s/0S base64, otherwise UTF-8 text. encodeValue emits prefixed hex/base64 or quoted UTF-8 text.

## State and Persistence Behavior
Stateless except a shared Commons Codec Base64 instance. Output bytes are caller-owned.

## Dependencies and Integration Points
Depends on commons-codec Hex/Base64 and StandardCharsets. Used by xattr CLI/web interfaces and filesystem xattr APIs.

## Risks and Test Signals
Risks include malformed hex wrapping, base64 leniency, quote handling without escaping, and null decode returning null. Tests should cover all prefixes, invalid hex, mixed case, empty values, and non-ASCII UTF-8.
