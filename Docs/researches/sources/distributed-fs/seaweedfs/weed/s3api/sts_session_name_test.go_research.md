## sources/distributed-fs/seaweedfs/weed/s3api/sts_session_name_test.go

Purpose: tests STS role session name validation rules.

Important APIs under test: `validateRoleSessionName`; helper `repeat` is also used by packed policy tests in the same package.

Control flow: table cases assert missing name maps to `STSErrMissingParameter`; one-character, overlong, invalid charset, whitespace, slash, colon, and Unicode values map to `STSErrInvalidParameterValue`; length 2, normal ASCII, allowed symbols `+=,.@-`, email-style, and 64-character valid names are accepted.

State and dependencies: no persistence. Uses package-level STS error code constants.

Signals and risks: covers AWS-compatible min/max length and allowed character set. The zero-byte 64-length case explicitly proves length alone is insufficient. It does not test every STS parameter, only role session names.
