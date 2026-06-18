<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/jobs_test.go -->
## sources/cloud-native/buildkit/solver/jobs_test.go

Purpose: integration-test job scheduling parallelism against real workers.

Important APIs and types: `TestJobsIntegration`, `testParallelism`, and config updaters `parallelismSetterSingle` / `parallelismSetterUnlimited`. It initializes OCI and containerd workers and runs an integration matrix.

Control flow: two independent busybox LLB runs share a persistent cache mount and each waits for the other to write a signal file. With max parallelism set to one, elapsed time should exceed ten seconds; with unlimited parallelism it should be below ten seconds.

State and dependencies: uses BuildKit integration sandbox, client solve API, LLB marshal, temporary local mounts, and errgroup. The cache mount is persistent within the worker to coordinate the two commands.

Integration points: validates that solver/job scheduling respects worker `max-parallelism` configuration while allowing true concurrency when unrestricted.

Risks and test signals: this is a high-value integration signal but platform-sensitive; it skips Windows and depends on worker images/mirrors. It does not directly test job deletion, provenance, or error wrapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/jobs_test.go -->
