<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/imagespec.go -->
# sources/cloud-native/moby/daemon/images/imagespec.go

Purpose: converts Docker container config fields into Docker OCI image config shape for image inspect responses.

Important APIs and control flow: `containerConfigToDockerOCIImageConfig` copies user, env, entrypoint, cmd, volumes, workdir, labels, stop signal, deprecated `ArgsEscaped`, exposed ports as string keys, healthcheck, onbuild, and shell into `dockerspec.DockerOCIImageConfig`.

State and persistence: no state is read or written beyond the supplied config pointer.

Dependencies and integration: used by `ImageInspect` to fill API config data while preserving Docker-specific extensions.

Risks: nil config returns an empty Docker OCI config. Deprecated fields are intentionally carried for compatibility. Port conversion depends on `nat.Port.String()` formatting from API container config.

Test signals: no direct tests here; image inspect tests validate serialized output.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/imagespec.go -->
