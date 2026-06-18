<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/TestCodecRawCoderMapping.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/TestCodecRawCoderMapping.java

Purpose: Tests mapping from erasure-code codec names to raw encoder/decoder implementations, including defaults, dedicated config keys, fallback lists, invalid coder names, and native enable/disable behavior.

Important APIs/types/functions: uses `CodecUtil.createRawEncoder`, `createRawDecoder`, codec names from `ErasureCodeConstants`, coder options `(6 data, 3 parity)`, config keys like `IO_ERASURECODE_CODEC_RS_RAWCODERS_KEY`, `IO_ERASURECODE_CODEC_RS_LEGACY_RAWCODERS_KEY`, `IO_ERASURECODE_CODEC_XOR_RAWCODERS_KEY`, and `IO_ERASURECODE_CODEC_NATIVE_ENABLED_KEY`. It asserts concrete raw coder classes for RS, RS legacy, XOR, and native variants.

Control flow: setup creates a fresh `Configuration`. Default test creates RS encoder/decoder and expects native RS coders when native erasure code is loaded, otherwise Java RS coders; RS legacy always maps to legacy Java coders. Dedicated-key test sets dummy factory names for RS and RS legacy and expects creation failures with message fragments. Fallback test sets RS coder list to Java RS then native RS and expects Java RS chosen. Legacy fallback confirms RS legacy defaults. Invalid-codec test sets XOR list to invalid name then valid XOR factory and expects valid XOR coders. Native-enabled test assumes native code, verifies RS/XOR native coders by default, then disables native in configuration and expects Java RS/XOR coders.

State and persistence behavior: configuration-local only. Native availability is process/global but only read through `ErasureCodeNative.isNativeCodeLoaded`.

Dependencies and integration points: integrates with Hadoop erasure-code `CodecUtil`, raw coder factories/classes, `GenericTestUtils`, JUnit assumptions, and configuration keys. This is a contract test for how HDFS/client erasure coding selects raw implementations.

Risks and edge cases: one expected exception message for RS legacy contains `"codec: rs"` rather than `"rs-legacy"`, reflecting current behavior or a brittle message check. Native-enabled test is skipped without native erasure-code support. It does not call `release()` on created raw coder instances, if those implementations allocate resources.

Test signals: validates default and configured raw coder selection, fallback order, invalid factory skipping, native disable override, and useful failure when only invalid factories are configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/TestCodecRawCoderMapping.java -->
