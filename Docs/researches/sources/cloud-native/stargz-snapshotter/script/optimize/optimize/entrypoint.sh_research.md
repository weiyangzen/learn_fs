# sources/cloud-native/stargz-snapshotter/script/optimize/optimize/entrypoint.sh

Purpose: Container entrypoint that validates image optimization output, TOC annotations, uncompressed-size annotations, and optimizer networking/mount support.
Important APIs/types/functions: helpers `retry`, `prepare_context`, `validate_toc_json`, `check_uncompressed_size`, `check_optimization`, and `append_toc`.
Control flow: logs into a TLS registry, starts buildkitd/containerd, builds a scratch sample image with files and an accessor binary, builds race-enabled `ctr-remote`, optimizes and no-optimizes images with supplied commands, saves/pulls them to inspect layer tar order and annotations, then runs optimizer with CNI, add-hosts, bind mount, and curl checks against a test server.
State and persistence: creates registry images, build context, Go binary, working dirs, BuildKit/containerd state, and bind-mount output files.
Dependencies and integration points: parameterized by `OPTIMIZE_COMMAND`, `NO_OPTIMIZE_COMMAND`, `GETTOCDIGEST_COMMAND`, `DECOMPRESS_COMMAND`, and `INVISIBLE_TOC` from `optimize/test.sh`.
Risks: assumes specific tar listing order and annotation names; uses privileged network setup and iptables legacy mode; `nerdctl push || true` can hide push failures before later checks catch them.
Test signals: run twice by `optimize/test.sh` for zstdchunked and gzip/eStargz modes.
