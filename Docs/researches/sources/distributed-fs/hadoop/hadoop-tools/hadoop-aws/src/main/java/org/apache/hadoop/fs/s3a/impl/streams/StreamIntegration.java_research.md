<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/StreamIntegration.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/StreamIntegration.java

Purpose: central stream integration utility for resolving configured S3A input stream types, constructing factories, loading custom factories, and building vectored IO context from configuration.

Important APIs/types/functions: constants name stream modes (`classic`, `prefetch`, `analytics`, `custom`, `default`), with `DEFAULT_STREAM_TYPE` set to analytics. `factoryFromConfig()` resolves an `InputStreamType` and invokes its factory function. `determineInputStreamType()` handles deprecated `fs.s3a.prefetch.enabled`, default mapping, enum resolution, and invalid type errors. `loadCustomFactory()` requires `INPUT_STREAM_CUSTOM_FACTORY`, loads a no-arg constructor, and wraps instantiation failures. `populateVectoredIOContext()` reads min seek, max merged read size, and active range read settings.

Control flow: stream selection first honors deprecated prefetch enablement, then resolves `fs.s3a.input.stream.type`, then constructs the factory. Custom factories are reflection-loaded only for the custom enum path.

State/persistence: stateless utility. The only durable behavior is configuration interpretation and one-time deprecation logging through `LogExactlyOnce`.

Dependencies/integration: ties Hadoop `Configuration`, `ConfigurationHelper.resolveEnum`, S3A constants, `VectoredIOContext`, and `InputStreamType` factory functions together.

Risks/test signals: wrong default or deprecated-option precedence changes runtime stream type. Custom factory loading can fail on missing class/no no-arg constructor. Tests should cover empty/default/custom/invalid values, deprecated prefetch override, and vectored IO bounds parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/StreamIntegration.java -->
