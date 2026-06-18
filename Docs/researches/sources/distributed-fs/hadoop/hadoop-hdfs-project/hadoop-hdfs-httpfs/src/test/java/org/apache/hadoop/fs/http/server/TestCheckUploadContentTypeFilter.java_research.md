# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/server/TestCheckUploadContentTypeFilter.java

## Purpose
This unit test verifies `CheckUploadContentTypeFilter` accepts data-upload requests only when upload semantics and content type are consistent.

## Important APIs, Types, and Functions
JUnit tests call helper `test(method, operation, contentType, upload, error)`. The helper uses Mockito `HttpServletRequest`, `HttpServletResponse`, and `FilterChain`, sets method, operation, data parameter, and content type, invokes `new CheckUploadContentTypeFilter().doFilter`, and verifies either `chain.doFilter` or `response.sendError(SC_BAD_REQUEST, contains("Data upload"))`.

## Control Flow
`putUpload` and `postUpload` assert valid `PUT CREATE` and `POST APPEND` uploads with `application/octet-stream` are allowed, including uppercase content type. `putUploadWrong` and `postUploadWrong` distinguish bad content type with and without `data=true`: bad type only errors when upload data is expected. `getOther` and `putOther` assert non-upload operations pass through.

## State and Persistence
The test is stateless and uses mocks only.

## Dependencies and Integration Points
It depends on `HttpFSFileSystem.Operation` names and `HttpFSParametersProvider.DataParam.NAME`, making it sensitive to client/server operation naming contracts. It verifies the filter registered in both web descriptors.

## Risks
The tests do not cover missing content type, multipart variants, charset parameters, or request bodies. They focus on the key create/append upload gate.

## Test Signals
The file directly signals that create/append two-step upload requests must use octet-stream content type only when the `data` flag marks the upload leg.
