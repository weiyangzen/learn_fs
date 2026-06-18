# sources/cloud-native/cri-o/hack/govulncheck.sh

## Purpose
Vulnerability scanning helper that installs govulncheck, emits OpenVEX, and optionally fails on module dependency vulnerabilities.

## Important APIs, Types, and Functions
Uses apt-get to install native deps, go install golang.org/x/vuln/cmd/govulncheck@v1.1.4, govulncheck -format openvex/json -tags=test ./..., jq parsing, VEX_ONLY flag.

## Control Flow
Installs dependencies/tool, writes build/cri-o.openvex.json, optionally exits if VEX_ONLY, otherwise generates JSON report, prints stdlib/module vuln summaries, and exits 1 for module vulnerabilities.

## State and Persistence
Writes build/cri-o.openvex.json and temp JSON report.

## Dependencies
Depends on Debian apt packages, Go, module download, jq, and govulncheck schema.

## Integration Points
CI security scan lane for CRI-O.

## Risks and Edge Cases
Runs apt-get on host, version may lag supported Go, JSON query assumes schema, stdlib vulnerabilities are printed but do not fail.

## Test Signals
OpenVEX output and exit status are the scan signals.
