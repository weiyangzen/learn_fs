# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ACopyFromLocalFile.java

Purpose: Parameterized contract coverage for `copyFromLocalFile()` with optimized copy enabled and disabled. It verifies option propagation and rejects non-local sources or destinations where the API contract requires local input.

Important APIs/types/functions: extends `AbstractContractCopyFromLocalTest`, uses `S3AContract`, toggles `Constants.OPTIMIZED_COPY_FROM_LOCAL`, and checks `FileSystem.hasPathCapability()`. Test helpers from the base class create temp files/directories and perform local-to-S3 copies.

Control flow: constructor receives the enabled flag. `createConfiguration()` removes bucket overrides, sets the optimized flag, and disables FS caching. Tests assert path capability equals the parameter, reject S3-to-S3 or destination-as-source misuse with `IllegalArgumentException`, and validate a local path without a `file:` scheme copies to S3.

State and persistence: writes temporary local files through the inherited contract base and remote S3 objects at method paths. No long-lived state.

Dependencies and integration points: Hadoop copy-from-local contract, S3A optimized upload path, local filesystem URI parsing, and path capability reporting.

Risks: optimized and non-optimized paths must remain semantically equivalent; scheme-less local paths are easy to misclassify; filesystem cache would hide per-parameter configuration without explicit disabling.

Test signals: catches option propagation regressions, local-source validation gaps, and behavior divergence between optimized and standard copy paths.
