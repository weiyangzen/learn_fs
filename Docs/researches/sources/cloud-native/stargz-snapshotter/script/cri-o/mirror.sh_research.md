# sources/cloud-native/stargz-snapshotter/script/cri-o/mirror.sh

Purpose: Mirrors and optimizes CRI-O test images into a local registry.
Important APIs/types/functions: same structure as CRI containerd `mirror.sh`: `retry`, `TOOLS_DIR/list`, `TOOLS_DIR/host`.
Control flow: builds `ctr-remote`, starts containerd, pulls each unique source image, optimizes to eStargz, and pushes to the mirror over plain HTTP.
State and persistence: writes `/bin/ctr-remote` and registry content.
Dependencies and integration points: used by CRI-O stargz tests from a prepare node with repository mounted read-only.
Risks: inherits URL rewriting/plain-HTTP assumptions from the containerd mirror script.
Test signals: failures surface during CRI-O stargz validation when pulls cannot resolve optimized images.
