# sources/control-plane/ceph-csi/internal/nfs/nodeserver/nodeserver.go

## Purpose
`nodeserver.go` implements the NFS CSI node service. It validates publish requests, resolves NFS mount sources, optionally reads updated server metadata from the CephFS journal, mounts NFS exports, unmounts targets, and reports filesystem stats.

## Important APIs, Types, And Functions
`NodeServer` embeds `csicommon.DefaultNodeServer`. `NewNodeServer()` initializes the CephFS volume journal and default node server. CSI methods include `NodePublishVolume`, `NodeUnpublishVolume`, `NodeGetCapabilities`, and `NodeGetVolumeStats`. Helpers include `mountNFS`, `validateNodePublishVolumeRequest`, `getSource`, and `getServerFromVolume`.

## Control Flow And State
`NodePublishVolume()` validates the request, enforces service account restrictions, builds mount options including read-only mode, resolves the source as `server:share`, optionally resolves a network namespace path from cluster ID, and mounts. `mountNFS()` creates the target directory if absent, returns success if already mounted, then either runs `mount` through `nsenter` or uses the Kubernetes mounter. `getSource()` prefers journal-stored server metadata when credentials are supplied, falls back to volume context `server`, formats IPv6 in brackets, and requires `share`.

## State And Persistence Behavior
Node-side state is the mounted filesystem target. Server override state can be persisted in the CephFS volume journal by controller modify operations. The node does not persist its own metadata.

## Dependencies And Integration Points
The node server integrates CSI protobufs, Kubernetes mount utils, network utilities, CephFS journal/store setup, NFS volume metadata, service account restriction validation, net namespace config, and common filesystem stats.

## Risks And Edge Cases
Invalid credentials in `getServerFromVolume()` are ignored and cause fallback to volume context, which favors availability but can hide metadata access failures. Mount stderr with zero exit status is treated as an error. The mount option append produces `-o` followed by each option as separate args only in nsenter path; the direct mounter receives the raw slice. Error classification relies partly on substring matching.

## Test Signals
`nodeserver_test.go` covers publish request validation and source formatting for hostnames, IPv4, IPv6, missing server, and missing share. It does not cover real mount/unmount, net namespace mounting, service account restrictions, journal server overrides, stats, or error mapping.
