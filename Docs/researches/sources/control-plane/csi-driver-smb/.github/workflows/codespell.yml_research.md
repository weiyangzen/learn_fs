## sources/control-plane/csi-driver-smb/.github/workflows/codespell.yml

Purpose: checks common spelling mistakes on every push and pull request through `codespell-project/actions-codespell`.

Important behavior: it checks filenames, skips git metadata, the workflow file itself, image assets, checksum files, vendor, and `go.sum`, and ignores known SMB-related words `browseable` and `ro`.

State is limited to the GitHub Actions checkout. Dependencies are pinned checkout and codespell actions. Risks include false positives in generated/vendor-like files not skipped, false negatives from broad skip patterns, and maintaining the ignore word list as SMB terminology evolves. Test signal is a spelling-check CI job.
