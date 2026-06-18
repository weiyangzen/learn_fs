<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/add-license.sh -->
# sources/control-plane/juicefs-csi-driver/hack/add-license.sh

## Purpose
License maintenance helper that checks or applies Apache license headers to source files using `addlicense`.

## Important APIs, Types, and Resources
Accepts one positional mode: `check` or `run`. Builds `addlicense` arguments with copyright holder `Juicedata Inc`, template `LICENSE_TEMPLATE`, and many ignore patterns for docs, YAML/JSON, generated/site assets, deploy, docker, scripts, and GitHub metadata.

## Control Flow
The script validates its mode, appends `-check` for check mode, runs `addlicense`, and emits a remediation message if missing headers are found. In run mode it updates files in place.

## State and Persistence
Check mode is read-only except for tool side effects; run mode mutates file headers. It relies on repository files and `LICENSE_TEMPLATE` as persistent inputs.

## Dependencies and Integration Points
Depends on Bash features despite lacking an explicit bash shebang in the snippet, `addlicense`, and repository root execution. Integrates with CI/license verification workflows.

## Risks
Risks include no shebang causing `/bin/sh` incompatibility for arrays/`[[ ]]` if executed directly, broad ignore patterns excluding files that should be licensed, and run mode touching many files.

## Test Signals
Run `bash hack/add-license.sh check`, ensure CI invokes it with bash, and test a temporary missing-header file to verify detection.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/add-license.sh -->
