# sources/cloud-native/composefs-rs/examples/common/make-image

Purpose: final image assembly helper that checks composefs EROFS images, runs repart under fakeroot, converts raw disk to qcow2, and removes the raw intermediate.

Important APIs/types/functions: iterates `tmp/sysroot/composefs/images/*` through `fsck.erofs`, runs `fakeroot run-repart tmp/image.raw`, and runs `qemu-img convert`.

Control flow: validate images first, create raw disk image, convert to requested output, delete raw image.

State/persistence: writes final qcow2 at caller path and temporary raw image under `tmp`.

Dependencies/integration: depends on `fsck.erofs`, `fakeroot`, `systemd-repart` via `run-repart`, and `qemu-img`.

Risks/test signals: fails early on invalid EROFS; assumes image glob exists. Conversion failures leave partial artifacts.
