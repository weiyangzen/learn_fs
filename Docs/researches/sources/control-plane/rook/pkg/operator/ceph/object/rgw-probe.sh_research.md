# sources/control-plane/rook/pkg/operator/ceph/object/rgw-probe.sh

Purpose: templated bash probe script for RGW startup/readiness checks that provides custom treatment for RGW throttling and misconfiguration responses.

Important APIs/variables: template variables `ProbeType`, `Port`, `Protocol`, and `Path`; constants `USAGE_ERR_CODE=125`, `PROBE_ERR_CODE=124`, `STARTUP_TYPE`, `READINESS_TYPE`, `RGW_RATE_LIMITING_RESPONSE=503`, and `RGW_MISCONFIGURATION_RESPONSE=500`; helper function `check`.

Control flow: builds `RGW_URL` against `0.0.0.0`, uses `curl --insecure --silent --output /dev/stderr --write-out '%{response_code}'`, exits with curl's error code if curl cannot reach RGW, treats HTTP 200-399 as success, treats 503 as success to avoid cascading readiness removal during S3 slow-down throttling, treats HTTP 500 as startup failure but readiness success with a warning, and treats all other HTTP statuses as probe failure with code 124.

State and persistence: stateless; writes diagnostics to stderr/stdout and returns exit codes for Kubernetes probes.

Dependencies and integration points: depends on bash, curl, Kubernetes probe execution, and Rook templating that fills the probe type, port, protocol, and path. It is consumed by RGW deployment generation.

Risks: `0.0.0.0` assumes local pod listener behavior; 500 readiness success trades availability for potentially serving broken endpoints; the 503 path has `2>/dev/stderr`, which is unusual redirection syntax and likely intended to write to stderr; `PROBE_TYPE` validation only happens in the 500 branch.

Test signals: no direct test file in this subset. Behavior should be validated through rendered deployment/probe tests or shell-level tests if changed.
