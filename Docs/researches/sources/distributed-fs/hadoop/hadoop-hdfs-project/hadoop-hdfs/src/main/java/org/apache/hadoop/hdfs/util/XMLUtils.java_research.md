<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/XMLUtils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/XMLUtils.java

## Purpose
`XMLUtils` centralizes XML-safe string mangling/unmangling, SAX string emission, and a simple parsed XML stanza tree representation for HDFS internals.

## APIs and Types
Public nested exceptions are `InvalidXmlException` and `UnmanglingError`. Public methods include `mangleXmlString`, `unmangleXmlString`, and `addSaxString`. Nested `Stanza` stores a value plus sorted child-name map to lists of child stanzas, with accessors and `toString`.

## Control Flow
`mangleXmlString` iterates Unicode code points, mangling XML-illegal code points and backslash as `\XXXX;`, and optionally replacing XML entity characters with entity references. `unmangleXmlString` runs a small state machine for backslash escapes and optional entity refs, throwing `UnmanglingError` on malformed escapes/entities. `addSaxString` emits a tag and mangled character data. `Stanza` adds children into a `TreeMap`, retrieves single or multiple children, and formats nested content.

## State and Persistence
The utility methods are stateless. `Stanza` holds mutable value and child lists in memory. No persistence.

## Dependencies and Integration
It depends on SAX `ContentHandler`, `AttributesImpl`, Java collections, and Hadoop annotations. It is used by offline image XML writers and XML parsing/serialization code that must preserve characters XML cannot represent directly.

## Risks
The mangling format uses exactly four hex positions despite code points potentially exceeding `0xffff`; current illegal code points handled here fit that pattern except backslash. `unmangleXmlString` only decodes named entity refs it knows, not numeric refs. `Stanza.getValueOrNull` rejects multiple values for a key, so callers must choose child-list APIs for repeated tags. `mangleXmlString` does not handle null input.

## Test Signals
Tests should cover XML-illegal controls, allowed tab/LF/CR, surrogate/noncharacters, backslash round trip, entity creation/decoding, malformed escape and entity errors, SAX emission, stanza multiple-child handling, and deterministic `TreeMap` ordering in `toString`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/util/XMLUtils.java -->
