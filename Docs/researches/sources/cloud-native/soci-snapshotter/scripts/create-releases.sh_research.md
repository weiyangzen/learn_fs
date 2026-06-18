# sources/cloud-native/soci-snapshotter/scripts/create-releases.sh

Purpose: builds dynamic and static Linux release tarballs with checksums.

Important APIs/types/functions: validates a `vMAJOR.MINOR.PATCH` tag, determines arch (`amd64`/`arm64`), computes release filenames, runs `make build` and `STATIC=1 make build`, copies `NOTICE.md` and `THIRD_PARTY_LICENSES`, creates tarballs, and writes sha256sum files.

Control flow: validate one tag argument and supported architecture, clear/create `release/`, build dynamic artifacts into `out`, archive them, clean out, build static artifacts, archive them, then checksum tarballs.

State and persistence: mutates `out/` and `release/`, creates tarballs and checksum files.

Dependencies/integration points: requires Makefile build targets, project license/notice files, tar, sha256sum, and Linux architecture mapping.

Risks: cleanup commands use `rm -rf "{$OUT_DIR:?}"/*`, where braces are quoted literally, likely not deleting intended output. This can contaminate static/dynamic artifacts if not caught. Tag regex dots are unescaped, accepting broader strings than intended.

Test signals: paired with `verify-release-artifacts.sh` to validate tarball contents and checksums.
