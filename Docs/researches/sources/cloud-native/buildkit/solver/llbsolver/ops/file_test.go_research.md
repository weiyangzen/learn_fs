# sources/cloud-native/buildkit/solver/llbsolver/ops/file_test.go

Purpose: unit-tests `FileOpSolver` graph semantics with an in-memory fake backend/ref manager.

Important APIs/types/functions: tests include `TestMkdirMkfile`, `TestChownOpt`, `TestChownCopy`, `TestInvalidNoOutput`, `TestInvalidDuplicateOutput`, `TestActionInvalidIndex`, `TestActionLoop`, `TestMultiOutput`, `TestFileFromScratch`, `TestFileCopyInputSrc`, `TestFileCopyInputRm`, and `TestFileParallelActions`. Helpers include `newTestFileSolver`, `testFileRef`, `testMount`, `testFileBackend`, and `testFileRefBackend`.

Control flow: tests build `pb.FileOp` action arrays and check the fake mount chain IDs and stored action pointers after solve. Invalid tests assert expected errors. The parallel-actions test blocks two independent branches on a callback and proves they run concurrently before joining through copy.

State/persistence: fake refs carry refcounts and mount chains; fake backend mutates string IDs and action chains instead of filesystem state. `checkReleased` asserts non-output refs and mounts are released, making lifecycle part of test validation.

Dependencies/integration: exercises `fileoptypes` interfaces directly and avoids cache manager/filesystem dependencies. It uses `atomic`, channels, and testify.

Risks: fake backend cannot detect real filesystem copy/chown behavior. It is valuable for DAG/ref lifecycle semantics but not for path security or platform-specific user resolution.

Test signals: strong coverage for solver dependency ordering, output indexing, scratch handling, release discipline, owner mount loading, and parallelism.
