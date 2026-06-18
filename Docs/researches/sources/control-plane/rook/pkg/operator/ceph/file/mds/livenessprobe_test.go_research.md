# sources/control-plane/rook/pkg/operator/ceph/file/mds/livenessprobe_test.go

## Purpose
This file tests the embedded MDS liveness probe script end to end by rendering the Kubernetes probe command, running it through bash, shimming `ceph fs dump`, and feeding representative MDS map JSON fixtures.

## Important APIs, Types, and Functions
`probeShimWrapper` defines shell functions for `ceph` and `jq` so the rendered script can run under Go tests. Embedded fixture variables load `test/0FS.json`, `0FS-2MDS.json`, `1FS-2MDS.json`, and the four `2FS-*` maps. `writeLines` writes the generated command to a temporary script file. `Test_liveness_probe_script` discovers `jq` through `ROOK_UNIT_JQ_PATH` or `which jq`, then runs subtests for absent/present MDS scenarios, multiple filesystems, command errors, invalid JSON, and standby membership.

## Control Flow, State, and Persistence
Each subtest generates a probe for a daemon/filesystem pair, writes the exec command to `livenessprobeSample.sh`, launches bash with environment variables that provide monitor info, mocked command output, return code, and `JQ`, then checks process exit code. Temporary script files are removed with defer. If `jq` cannot be located, the whole test is skipped.

## Dependencies and Integration Points
The tests integrate Go unit tests, embedded JSON fixtures, the generated Kubernetes probe command, bash, a shimmed Ceph CLI, and real `jq`. They validate the shell script rather than only testing Go rendering.

## Risks
The test depends on a host `jq` binary unless CI sets `ROOK_UNIT_JQ_PATH`; otherwise important probe coverage is skipped. Several subtests share the same display name, which can make failure reports harder to scan. Temporary file name `livenessprobeSample.sh` is fixed in the working directory, so parallel test execution could collide. The shim asserts only one exact `ceph fs dump` argument shape.

## Test Signals
Signals include failure for zero filesystems and no matching MDS, success for MDS in the global standby list, success for active and standby-replay daemons in matching filesystems, failure for wrong filesystem or missing daemon, success for Ceph command failure and invalid JSON, and correct disambiguation across two filesystem maps.
