# sources/cloud-native/containerd/pkg/oci/spec_test.go

Purpose: tests core spec generation, defaults, selected options, descriptor conversions, and safe user-file opening through absolute symlinks.

Important APIs/types/functions: `TestGenerateSpec`, `TestGenerateSpecWithPlatform`, `TestSpecWithTTY`, `TestWithLinuxNamespace`, capability tests, default Windows/Unix population tests, `TestWithPrivileged`, `TestOpenUserFile_AbsoluteSymlink`, and `TestGroupLookup_AbsoluteSymlink`. `readLinkFS` is a test filesystem implementing `ReadLink`.

Control flow: tests build specs through generation helpers or direct options, then inspect fields. Symlink tests simulate NixOS-style absolute symlinks and ensure `openUserFile` reanchors them inside the root fs.

State/persistence: temporary or in-memory filesystem state.

Dependencies/integration: runtime-spec defaults, platform parsing, user/group parsing, and descriptor API types.

Risks: generated default specs are broad and can change for valid runtime reasons, making tests sensitive to default policy changes. Symlink behavior depends on filesystem interface support.

Test signals: protects top-level generation behavior, platform-specific defaults, security option behavior, and the rootfs symlink compatibility path added for stricter Go fs validation.
