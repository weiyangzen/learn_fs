# sources/cloud-native/ostree/tests/test-create-usb.sh

Purpose: validates `ostree create-usb` for collection refs, destination repo placement, summaries, and repo-finder integration.

Important APIs/functions: `skip_without_ostree_feature gpgme`, `ostree init`, signed commits and `summary --update --gpg-sign`, `remote add --collection-id --gpg-import`, `pull`, `create-usb`, `refs --collections`, `summary -v`, symlink assertions, and repo-finder output checks.

Control flow: builds a signed source repo with several refs, pulls them into a local repo, creates USB repositories in default, standard, and non-standard destinations, appends refs to an existing USB, and checks finder output includes trusted keyring and collection-ref checksums.

State/persistence: writes mount-like directories `dest-mount*`, `.ostree/repo`, `.ostree/repos.d` symlinks, summaries, and trusted keyrings. Dependencies include GPG fixture keys.

Integration/risk/test signals: protects offline media creation and discovery. Risks are symlink path expectations and GPG feature gating. Five TAP cases cover USB variants and finder lookup.
