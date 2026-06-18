# sources/cloud-native/nydus/contrib/nydusify/pkg/packer/artifact.go

Purpose: centralizes local artifact path construction for packer bootstrap, blob, and `output.json` files.

Important APIs/types/functions: `Artifact`, `NewArtifact`, `bootstrapPath`, `blobFilePath`, `outputJSONPath`, and `ensureOutputDir`.

Control flow: `NewArtifact` initializes an artifact with a user-provided or default output directory and ensures the directory exists. `bootstrapPath` preserves file names with extensions or appends `.meta`. `blobFilePath` returns digest-named blobs when requested, otherwise replaces existing extension with `.blob` or appends `.blob`.

State and persistence: creates the output directory on disk with mode `0755`. It does not create artifact files itself.

Dependencies and integration points: packer build/push flows, path utilities, and nydus build output contracts.

Risks and test signals: extension-based path decisions mean image names containing dots are treated as explicit file names. Default output dir is relative, which depends on caller working directory.
