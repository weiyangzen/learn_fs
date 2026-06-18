<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/hostpath.go -->
# sources/control-plane/rook/pkg/daemon/ceph/cleanup/hostpath.go

Purpose: cleans host-path data left by a Rook Ceph cluster, including namespace data directories, monitor directories whose key matches the current mon secret, exporter data, and CSI driver directories.

Important APIs/types/functions: `StartHostPathCleanup`, `cleanCSIDirs`, `cleanExporterDir`, `cleanMonDirs`, and `secretKeyMatch`.

Control flow: `StartHostPathCleanup` removes `dataDirHostPath/namespaceDir`, then calls monitor, exporter, and CSI cleanup helpers. `cleanMonDirs` glob-matches `mon-*`, checks each keyring with `secretKeyMatch`, and deletes only matching monitor directories. `cleanCSIDirs` removes directories whose names end in `.csi.ceph.com`; `cleanExporterDir` removes `exporter` if present.

State and persistence behavior: this file performs filesystem deletion via `os.RemoveAll`. Secret matching reads `monDir/data/keyring` and compares the extracted key to the supplied mon secret to avoid deleting unrelated monitor data.

Dependencies and integration points: depends on `os`, `filepath`, `path`, Rook operator key extraction, and cleanup logging. It is invoked by cleanup jobs for host-mounted Rook data directories.

Risks: `filepath.Join(monDir, "/data/keyring")` uses an absolute second path component, so path-cleaning behavior deserves attention. Recursive deletes are broad and depend on correct inputs. CSI cleanup deletes all matching suffix directories under the data root.

Test signals: monitor secret match/mismatch, missing keyring behavior, exporter deletion, CSI suffix deletion, namespace data deletion, invalid glob/read-dir paths, and path traversal/absolute-path safeguards.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/hostpath.go -->
