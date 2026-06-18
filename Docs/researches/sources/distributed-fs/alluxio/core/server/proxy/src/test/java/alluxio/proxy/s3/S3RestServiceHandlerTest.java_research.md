# sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/S3RestServiceHandlerTest.java

Purpose: `S3RestServiceHandlerTest` covers selected S3 REST utility and XML model behavior.

Important tests are `userFromAuthorization`, `testDeleteObjectReq`, and `testDeleteObjectResp`. `userFromAuthorization` verifies malformed authorization strings throw `S3Exception` and that `Credential=test/asd` extracts `test`. The XML tests use Jackson `XmlMapper` to deserialize and serialize delete-object request/result bodies, checking quiet mode, object count, deleted/error lists, and request round-trip equality.

State and persistence are absent; the tests exercise parsing and serialization only. Dependencies include Alluxio global configuration, Jackson XML, JUnit, and S3 delete request/result models. Integration signals include legacy non-authenticated user extraction in `S3RestUtils.getUserFromAuthorization` and multi-object delete REST payload compatibility. Risks covered are malformed credential headers and XML shape drift. Gaps include behavior under `AuthType.NOSASL`, v4 parser integration, object delete execution, and detailed delete response serialization equality for response objects.
