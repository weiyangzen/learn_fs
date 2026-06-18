# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/CodecUtil.java

Purpose: factory utility for high-level erasure codecs/coders and raw erasure coders, driven by Hadoop configuration and `CodecRegistry`.

Important APIs and control flow: constants define configuration keys for codec class names, raw coder order, and native enablement. `createEncoder()`/`createDecoder()` resolve the codec class name for a schema, instantiate it reflectively with `(Configuration, ErasureCodecOptions)`, and return its encoder/decoder. `createRawEncoder()`/`createRawDecoder()` obtain ordered raw coder names from configuration or the registry, skip native coders when disabled, try factories in order, and fall back on exceptions until one succeeds.

State and persistence: stateless utility; all durable choices are in `Configuration` or classpath service registration.

Dependencies and integration: integrates `ECSchema`, `ErasureCodecOptions`, high-level codec classes, raw coder factories, reflection, and `CodecRegistry`. It is the main bridge from HDFS/EC policy configuration to actual coding implementations.

Risks and test signals: test default RS/XOR/HHXOR class resolution, custom codec missing config errors, native-disabled fallback, factory failure fallback, and reflection constructor failures. `createRawCoderFactory()` can return null, so fallback tests should cover null/exception paths.
