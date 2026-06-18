# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ynl.mk

Purpose: Makefile include for networking selftests that need YNL-generated rtnetlink/netlink family bindings and `libynl.a`.

Important APIs/variables: consumes `YNL_GENS`, `YNL_GEN_PROGS`, and `YNL_GEN_FILES`. Computes `YNL_OUTPUTS` under `$(OUTPUT)` and `YNL_SPECS` from `Documentation/netlink/specs/*.yaml`. Adds include paths for kernel UAPI headers, YNL lib, and generated headers to targets that depend on YNL.

Control flow: all YNL output binaries/files depend on `$(OUTPUT)/libynl.a`. A hash signature file `.libynl-$(YNL_GENS_HASH).sig` is created from `YNL_GENS`; changing families removes old signatures and forces rebuilding `libynl.a`. The lib target deletes any source-tree `tools/net/ynl/libynl.a`, invokes make in `tools/net/ynl` with `GENS="$(YNL_GENS)" RSTS="" libynl.a`, and copies the archive to `$(OUTPUT)`.

State and persistence: writes build artifacts in `$(OUTPUT)` and temporarily in `tools/net/ynl`. `EXTRA_CLEAN` removes YNL Python caches, library object/archive/dependency files, signature files, and output archive.

Dependencies and integration: included by selftest Makefiles using generated YNL C bindings, such as TUN/TAP tests that include `rt-*-user.h`. Depends on `sha1sum`, make, generated spec YAMLs, and top-level kernel source variables.

Risks: content changes within `YNL_GENS` list are tracked by hash, but changes to generator internals rely on make dependencies outside this snippet. It removes source-tree lib artifacts, which is expected for this build but can surprise manual builds.

Test signals: build success and correct regeneration of `libynl.a`; stale-family bugs appear as missing generated headers/symbols or link failures.
