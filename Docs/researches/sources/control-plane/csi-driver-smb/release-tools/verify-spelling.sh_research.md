<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-spelling.sh -->
# sources/control-plane/csi-driver-smb/release-tools/verify-spelling.sh

Purpose: Runs misspell over tracked repository files outside vendor.

Important behavior: Uses strict shell options, installs `github.com/client9/misspell/cmd/misspell@v0.3.4` into a temporary directory if missing, runs `git ls-files -z | grep -z -v vendor | xargs -0 misspell --`, records output, prefixes errors, and exits nonzero when spelling errors are found.

Control flow: Temporary directory is always removed by trap. Missing tool triggers a temporary Go install outside the repo module.

State and persistence behavior: Writes only the temp directory and error log; reads git tracked files.

Dependencies and integration points: Invoked by `.prow.sh`; overlaps with the GitHub Actions codespell workflow but uses a different spelling engine.

Risks: Requires Go/network if misspell is not installed. The vendor filter is a simple substring exclusion and may skip paths containing `vendor` elsewhere.

Test signals: Static spelling signal for tracked files.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-spelling.sh -->
