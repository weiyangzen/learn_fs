# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3Error.java

`S3Error` is the Jackson XML DTO for AWS-style `<Error>` responses. It carries `Code`, `Message`, `RequestId`, and `Resource`. The default constructor initializes empty strings for serializer compatibility; the resource/code constructor copies code and default description from `S3ErrorCode`.

The class is transient response state only. It is created and serialized by `S3ErrorResponse` with `XmlMapper`.

Tests should verify root and property element names, default constructor serialization, message overrides after construction, resource propagation, and behavior with blank request IDs. Client compatibility may require attention because request IDs are always empty here.
