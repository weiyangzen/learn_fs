# sources/control-plane/juicefs-csi-driver/.github/workflows/sync_image.yaml

## Purpose
This manual workflow syncs JuiceFS-related images from Docker Hub to Alibaba Cloud registries. It supports mount images, CSI images, operator images, and arbitrary images.

## Important Jobs and Steps
`mount-image-sync` syncs a provided mount tag or discovers latest CE and EE mount tags, checking Alibaba registry existence before syncing. `csi-image-sync` syncs a provided CSI tag or discovers the latest CSI release. `operator-image-sync` syncs a provided operator tag or discovers the latest operator release. `other-image-sync` syncs an arbitrary input image with an optional platform argument.

## Control Flow
Each job checks out the repo, logs into Docker Hub, enters `.github/scripts`, and runs `sync.sh` with the selected image/tag. Jobs are independent and may run even when unrelated inputs are empty. Concurrency cancels superseded runs per ref.

## State and Persistence Behavior
The workflow writes no repository state but publishes/syncs images to external Alibaba Cloud registries using ACR credentials.

## Dependencies and Integration Points
It depends on Docker Hub credentials, ACR credentials, GitHub release APIs, JuiceFS static package downloads for EE version detection, and `.github/scripts/sync.sh`.

## Risks
Several shell tests interpolate optional inputs directly into `[ ... ]`, which can be fragile for empty values or special characters. All four jobs run on every dispatch, so a request to sync one image still performs setup for other lanes and may hit external endpoints. Version discovery is grep based.

## Test Signals
Success indicates requested or latest images were found and synced, or already existed in target registries. It does not validate runtime behavior of the synced images.
