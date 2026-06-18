# File Research: sources/cow-pools/bcachefs-tools/.github/workflows/obs.yml

- Reusable workflow for publishing source artifacts into an OBS-backed package repository.
- Takes artifact, runner, architecture, and distro inputs plus GPG and OBS repository secrets.
- Builds an isolated Debian container with Podman, imports signing material for non-PR runs, downloads source artifacts, verifies GitHub attestations, checks or creates detached GPG signatures, and clones the selected snapshot or release OBS repository.
- Replaces repository contents with `.dsc`, `.tar.xz`, `.sig`, generated `_service`, RPM lint config, extracted spec files, and cargo config; patches the RPM spec version from the tarball name.
- Produces checksum provenance with `actions/attest-build-provenance@v3`, commits the OBS state with the attestation URL, and pushes over SSH backed by GPG agent auth.
