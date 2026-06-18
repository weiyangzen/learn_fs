## sources/control-plane/csi-driver-iscsi/Makefile

Purpose: defines build, container, sanity, module-check, and clean targets for the iSCSI CSI plugin.

Control flow includes `release-tools/build.make`, sets image/build variables, builds a static Linux `bin/${ARCH}/iscsiplugin` with vendor mode, builds Docker images via `docker buildx`, runs sanity through `./test/sanity/run-test.sh`, verifies modules, and cleans built artifacts. `all` maps to `iscsi`.

State includes `bin/<arch>/iscsiplugin`, Docker images, and Go module verification output. Dependencies are Go, vendor directory, Docker buildx, release-tools Make rules, and sanity scripts. Risks include Linux-only build target regardless of host, stale `CMDS=iscsiplugin` interactions with release-tools, `mod-check` using a fragile shell hash comparison, and clean removing only `bin/iscsiplugin` not `bin/${ARCH}`. Test signal comes from CI make, sanity, and container workflows.
