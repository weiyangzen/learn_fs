# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/AwsCredential.java

Purpose: `AwsCredential` parses and stores the credential-scope portion of AWS Signature V4 authentication: access key ID, date, region, service, and terminal request marker.

Important APIs are `create`, getters, `createScope`, and `validateDateRange`. Control flow uses a regex to split credentials shaped like `access/yyyymmdd/region/service/aws4_request`, validates the date, then constructs the immutable credential object. Date validation parses with `S3Constants.DATE_FORMATTER` and only accepts dates from yesterday through tomorrow relative to local system date.

State and persistence are final in-memory fields only. Dependencies include `S3Exception`, `S3ErrorCode`, Java time, regex, and SLF4J. Integration points are `AwsAuthV4HeaderParserUtils` and `AwsAuthV4QueryParserUtils`; `StringToSignProducer` later uses `createScope` via `SignatureInfo`. Risks include a permissive regex (`aws\\S+`) that accepts nonstandard terminal strings beginning with `aws`, local-clock sensitivity, and `LocalDate.parse` exceptions escaping as runtime errors if the date has the wrong numeric shape but matches the regex. Test signals in `TestAuthorizationV4HeaderParser` rely on today's date to avoid the date range rejection.
