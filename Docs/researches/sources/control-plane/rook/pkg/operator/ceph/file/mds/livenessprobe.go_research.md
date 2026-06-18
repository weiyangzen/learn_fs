# sources/control-plane/rook/pkg/operator/ceph/file/mds/livenessprobe.go

## Purpose
This file embeds and renders the MDS liveness probe script and exposes the probe specification used in MDS containers. The probe checks whether the daemon ID appears as active or standby in the Ceph MDS map for the expected filesystem.

## Important APIs, Types, and Functions
Probe constants define timeout, command timeout, initial delay, period, success threshold, and failure threshold. `mdsLivenessProbeCmdScript` embeds `livenessprobe.sh`. `mdsLivenessProbeConfig` carries MDS ID, filesystem name, keyring path, and command timeout. `renderProbe` applies Go `html/template` to the script. `generateMDSLivenessProbeExecDaemon` returns a Kubernetes `v1.Probe` with `bash -c <rendered script>`.

## Control Flow, State, and Persistence
At deployment generation time, the MDS container receives the rendered script inline as an exec probe. Template parse/render failures are logged as warnings and still return a probe with whatever command string was produced. The probe state is persisted only in the Kubernetes Deployment/Pod spec.

## Dependencies and Integration Points
The file integrates with Kubernetes `v1.Probe`, embedded shell script assets, keyring mount paths, MDS deployment spec creation, and the Ceph CLI environment variables used inside the script. User-provided liveness probe config can override the generated defaults through higher-level configuration.

## Risks
Embedding a rendered multi-line shell script in the Pod spec makes correctness sensitive to template escaping and shell quoting. Use of `html/template` rather than `text/template` could escape special characters if future values contain them, though current values are controlled daemon IDs and paths. Logging render errors but continuing can create an invalid probe command.

## Test Signals
Signals include rendered command presence in MDS container probes, default timing values, correct daemon/filesystem/keyring substitution, and behavioral shell tests against representative `ceph fs dump` JSON.
