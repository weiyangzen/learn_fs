# sources/control-plane/ceph-csi/deploy/cephcsi/image/Dockerfile

Purpose: multi-stage Dockerfile for building and packaging the `cephcsi` binary.

Important APIs/types/functions: stages are `updated_base`, `builder`, and final CentOS Stream 9 minimal image. Build args include source dir, Go arch, base images, CSI image name/version, Git commit, Go root, and Ceph version.

Control flow: updates Ceph base repos, installs NFS utilities, downloads architecture-specific Go, installs build deps and Ceph dev libraries, copies source, runs `make cephcsi`, then copies the binary into final image and installs runtime packages including Ceph clients, `rbd-nbd`, `ceph-fuse`, `cryptsetup`, `nvme-cli`, filesystems, and `kmod`.

State and persistence behavior: final image contains `/usr/local/bin/cephcsi` and runtime packages; no runtime cluster state.

Dependencies and integration points: relies on `build.env`, Ceph RPM repos, Go downloads, dnf/microdnf, CGO/Ceph libraries, and `make cephcsi`.

Risks: network package/download availability affects reproducibility. Dynamic library check catches missing libs but not runtime kernel/tool compatibility. Broad runtime package set increases image surface.

Test signals: image build CI, `ldd` check, binary startup, and deployment e2e tests.
