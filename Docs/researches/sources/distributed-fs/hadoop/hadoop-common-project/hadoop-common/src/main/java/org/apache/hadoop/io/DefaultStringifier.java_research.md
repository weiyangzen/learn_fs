<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DefaultStringifier.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DefaultStringifier.java

Purpose: default `Stringifier` implementation that converts objects to Base64 strings using Hadoop serialization and restores them from those strings. It also provides configuration storage helpers.

Important APIs, types, and functions: constructor obtains `Serializer` and `Deserializer` from `SerializationFactory` and opens them on reusable buffers. `toString(T)` serializes to `DataOutputBuffer` and Base64 encodes. `fromString(String)` Base64 decodes into `DataInputBuffer` and deserializes. Static `store/load` persist one value in `Configuration`; `storeArray/loadArray` store comma-separated Base64 values.

Control flow: every conversion resets the reusable buffer before serializing/deserializing. Static helpers create a stringifier, use it, and close it in finally paths for load/arrays.

State and persistence: instance state includes serializer, deserializer, and buffers. Persistent state is configuration key strings containing Base64 payloads.

Dependencies and integration points: depends on Hadoop serialization framework, commons-codec Base64, `GenericsUtil`, and configuration.

Risks and test signals: constructor does not validate missing serializer/deserializer before `open()`. `load()` and `loadArray()` fail if the key is missing. `storeArray()` rejects empty arrays and uses the first element's class for all items. Tests should cover writable and custom serializers, missing keys, empty arrays, comma separator safety, close behavior, and mixed-subclass arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DefaultStringifier.java -->
