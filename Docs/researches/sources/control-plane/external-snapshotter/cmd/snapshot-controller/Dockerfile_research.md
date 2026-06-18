# sources/control-plane/external-snapshotter/cmd/snapshot-controller/Dockerfile

## Purpose
Container image definition for the `snapshot-controller` external-snapshotter binary.

Source size: 7 lines, 225 bytes.

## Important APIs, Types, and Functions
- Base stages: `FROM gcr.io/distroless/static:latest`.
- Copy steps: `COPY ${binary} snapshot-controller`.
- Runtime directives: `ENTRYPOINT ["/snapshot-controller"]`.

## Control Flow
- Build context provides a prebuilt binary or staged artifact.
- The image copies the command binary into the runtime filesystem and sets process/user directives.
- Kubernetes Deployment manifests run this image as the controller or sidecar container.

## State and Persistence
- No runtime persistence is declared by the Dockerfile.
- Container state is ephemeral; Kubernetes objects and CSI driver state are external.

## Dependencies and Integration Points
- Container base image, built Go command binary, image build system/cloudbuild, Kubernetes deployment manifests.

## Risks and Edge Cases
- Binary path/name must match the command built by release tooling.
- Base image and user settings affect CVE profile and runtime permissions.

## Test Signals
- Image build success and command startup in Kubernetes are the relevant signals.
