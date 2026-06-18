<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ObjectInputStreamFactory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ObjectInputStreamFactory.java

Purpose: defines the stable service interface for S3A object input stream factories. It lets `S3AStore` create, bind, start, and query stream implementations without changing the factory method signature as new read parameters are added.

Important APIs/types/functions: `ObjectInputStreamFactory` extends Hadoop `Service` and `StreamCapabilities`; `bind(FactoryBindingParameters)` wires store callbacks after init and before start; `readObject(ObjectReadParameters)` creates an `ObjectInputStream`; `factoryRequirements()` exposes thread/vector IO needs; `streamType()` identifies the produced `InputStreamType`; nested `StreamFactoryCallbacks` supplies a synchronous AWS `S3Client` and factory statistic increments.

Control flow: store code constructs a factory, initializes it as a service, binds extra callbacks, then calls `readObject()` for each opened object. Implementations may lazily contact S3 after returning the stream.

State/persistence: the interface persists no data, but it defines a lifecycle state contract through `Service`. Implementations may retain bound callbacks and configuration.

Dependencies/integration: integrates with AWS SDK v2 `S3Client`, Hadoop service lifecycle, stream capability probing, S3A `Statistic`, and the stream factory selection layer in `StreamIntegration`.

Risks/test signals: lifecycle misuse is the main risk, especially calling `bind()` outside init/start ordering. Tests should exercise custom factories, service lifecycle, factory requirement propagation, and capability/statistic callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ObjectInputStreamFactory.java -->
