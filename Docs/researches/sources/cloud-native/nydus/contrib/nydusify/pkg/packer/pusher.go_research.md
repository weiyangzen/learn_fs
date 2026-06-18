# sources/cloud-native/nydus/contrib/nydusify/pkg/packer/pusher.go

Purpose: uploads local packer metadata and blob artifacts to OSS/S3-like backends.

Important APIs/types/functions: `Pusher`, `PushRequest`, `PushResult`, `NewPusherOpt`, `NewPusher`, `Push`, `ParseBackendConfig`, and `ParseBackendConfigString`.

Control flow: constructor validates output dir and initializes separate meta and blob backend clients from corresponding raw configs. `Push` uploads parent blobs first without force, uploads the new blob when present, finalizes blob backend, uploads bootstrap metadata with force, finalizes meta backend, and returns first URL from each descriptor. On any error it attempts cancel finalization for both backends.

State and persistence: reads files from `Artifact` paths and persists objects to remote backends. Backend clients hold upload state until finalized.

Dependencies and integration points: shared backend factory, packer artifacts, JSON config files/strings, context background, logrus, and OSS/S3 config structs.

Risks and test signals: mock backend `Upload` tests assume non-nil descriptors. Parent blob uploads use digest-named files and size zero. Context is not caller-controlled and lacks timeout. Finalize error handling can mask upload cleanup details.
