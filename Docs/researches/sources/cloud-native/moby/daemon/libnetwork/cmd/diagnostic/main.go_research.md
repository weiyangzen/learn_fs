# sources/cloud-native/moby/daemon/libnetwork/cmd/diagnostic/main.go

## Purpose
Command-line diagnostic client for libnetwork NetworkDB tables. It checks daemon readiness, fetches cluster/network peers, dumps service-discovery or overlay peer tables, identifies orphan entries, and can optionally delete orphaned entries.

## Important APIs, Types, And Functions
Flags include `-ip`, `-port`, `-net`, `-t`, `-r`, `-a`, and `-v`. URL templates target `/ready`, `/joinnetwork`, `/leavenetwork`, `/clusterpeers`, `/networkpeers`, `/gettable`, and `/deleteentry`. `httpIsOk` validates readiness responses. `fetchNodePeers` decodes `diagnostic.TablePeersResult`. `fetchTable` decodes table entries, base64-decodes values, unmarshals `libnetwork.EndpointRecord` or `overlay.PeerRecord`, and optionally remediates.

## Control Flow
`main` parses flags, blocks disruptive join/leave unless `DIND_CLIENT` is set, checks readiness, optionally joins the target network, fetches peers, dumps the selected table, prompts before deletion when remediation is requested, and leaves the network if it joined.

## State And Persistence
Read-only by default. With `-r`, it can delete NetworkDB entries through daemon diagnostic endpoints after an exact `Yes` confirmation.

## Dependencies And Integration Points
Depends on libnetwork diagnostic HTTP result types, endpoint protobuf decoding, overlay peer decoding, and containerd logging.

## Risks And Test Signals
Uses unauthenticated HTTP URLs from flags and has potentially disruptive remediation. Error handling is fatal and exits the process. No tests are included in this subset.
