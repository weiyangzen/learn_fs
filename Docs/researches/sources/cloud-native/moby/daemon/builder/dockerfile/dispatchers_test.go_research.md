## sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers_test.go

**Purpose:** Broad unit coverage for Dockerfile instruction dispatch behavior.

**Important APIs:** Exercises env, maintainer, label, FROM scratch/args/multistage, ONBUILD, WORKDIR, CMD, HEALTHCHECK, ENTRYPOINT, EXPOSE, USER, VOLUME, STOPSIGNAL, ARG, SHELL, `prependEnvOnCmd`, RUN with build args, healthcheck suppression, unsupported options, and port/network parsing helpers.

**Control flow:** Tests build dispatch requests with mock builders/configs and assert resulting `runConfig`, errors, or parsed port maps.

**State and persistence:** Uses mocks and in-memory config state; no real daemon containers.

**Dependencies and integration:** Depends on mock backend and instruction parsing helpers. It is the main safety net for `dispatchers.go`.

**Risks:** Because mocks bypass real container/image backends, tests cannot fully validate commit, runtime attach, platform-specific container behavior, or actual image cache storage.

**Test signals:** Strong direct signal for parser-to-dispatch semantics and many legacy compatibility cases, especially port grammar and build-arg cache command construction.
