# sources/control-plane/csi-driver-nfs/.github/workflows/codespell.yml

Purpose: runs codespell on NFS driver pushes and PRs.

Important APIs and types: one Ubuntu job with pinned checkout and pinned `actions-codespell`, filename checking, broad skip list, and ignored word `ro`.

Control flow: GitHub Actions scans text files except `.git`, workflow file, images, sums, vendor, `go.sum`, and `release-tools/prow.sh`.

State and persistence: check status and logs only.

Dependencies and integration: complements release-tools `verify-spelling.sh` in Prow.

Risks: excludes `release-tools/prow.sh` and vendor/go.sum. Ignoring `ro` may hide real typo-like tokens but avoids false positives for read-only abbreviations.

Test signals: workflow status on push and PR.
