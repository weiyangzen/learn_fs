<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/check-latest-image-required.sh -->
# sources/control-plane/juicefs-csi-driver/.github/scripts/check-latest-image-required.sh

## Purpose
`check-latest-image-required.sh` decides whether the JuiceFS CSI Driver `latest` Docker image should be rebuilt/pushed by comparing upstream JuiceFS release time, CSI driver release time, and Docker Hub `latest` image update time.

## Important APIs, Types, and Functions
Functions are `image_update_required` and `main`. It queries GitHub release APIs with `curl`, parses JSON with `jq`, derives the latest CSI driver tag from `git describe --tags --match 'v*' | grep -oE`, queries Docker Hub tag metadata, converts timestamps with `date -d`, and prints `yes` or `no`.

## Control Flow, State, and Persistence
`image_update_required` exits on missing upstream/CSI release tags, returns true if any publication timestamp is missing, and otherwise returns true when Docker Hub `latest` is older than or equal to either latest JuiceFS or latest CSI driver release. `main` maps return status to `yes`/`no`. It has no persistent local state.

## Dependencies and Integration Points
It depends on network access to GitHub and Docker Hub, `jq`, GNU `date`, Git tags in the checked-out repository, and Docker Hub's `last_updated` field. `latest-ignore.yaml` invokes it inside a GitHub Actions workflow to gate `make image-latest` and `make push-latest`.

## Risks and Test Signals
Risks include API rate limits, tag regex not matching versions with zero minor components, timestamp parse differences outside GNU date, Docker Hub eventual consistency, and returning `yes` on partial metadata. Signals are the printed `IMAGE_REQUIRED` value in the workflow and successful conditional image build/push.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/check-latest-image-required.sh -->
