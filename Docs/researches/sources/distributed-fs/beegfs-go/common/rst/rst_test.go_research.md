# sources/distributed-fs/beegfs-go/common/rst/rst_test.go

Purpose: unit tests common RST helpers for recreating work requests from jobs and splitting file ranges into work segments.

Important fixtures are `baseTestJob`, `baseTestSegments`, and `getNewTestSegments`. Tests are `TestRecreateWorkRequests` and `TestGenerateSegments`.

Control flow: `TestRecreateWorkRequests` clones a base job into sync and mock request types, regenerates work requests from two segments, and checks copied job/request fields, request IDs, external IDs, segment identity, remote target, and type-specific payload cloning. It also verifies invalid request types produce work requests with nil type. `TestGenerateSegments` table-tests empty, one-byte, evenly split, and unevenly split files.

State behavior under test includes deep-copy expectations for protobuf fields and direct segment reuse. Persistence is not involved.

Dependencies include `testing`, `testify/assert`, `testify/require`, protobuf cloning, and BeeRemote/Flex messages.

Integration points are provider `GenerateWorkRequests` implementations that use `RecreateWorkRequests` and `generateSegments`, especially mock and S3 providers.

Risks: tests do not cover builder work-request recreation with nil segments in depth, segment invalid inputs such as zero segment count, or file sizes large enough to expose overflow. They intentionally rely on private helpers from the same package.

Test signals: good coverage for core request shape and byte/part range math.
