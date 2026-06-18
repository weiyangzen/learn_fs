# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/tool/image_test.go

Purpose: tests pure helper behavior and error paths in the image mount wrapper.

Important APIs and flow: `TestMkMounts` asserts nil, bind, and overlay mount structures. `TestCheckImageType` verifies priority of `NydusImage` over `OCIImage`. `TestImageMountErrors` forces `MkdirAll` failure by setting `Rootfs` to an existing file. `TestImageUmount` covers missing rootfs, stat failure through a file-as-parent path, and unmount failure for an ordinary temporary directory.

State and persistence: uses temporary files and directories only; no successful privileged mount is attempted.

Dependencies and integration: validates the shape expected by containerd mount APIs. It does not require OCI descriptors with real layer metadata.

Risks and test signals: good coverage for branch behavior and error wrapping. It intentionally avoids positive mount tests, so actual overlay/bind mount compatibility is left to integration testing on Linux with privileges.
