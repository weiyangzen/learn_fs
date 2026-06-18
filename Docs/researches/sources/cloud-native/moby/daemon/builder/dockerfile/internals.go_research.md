## sources/cloud-native/moby/daemon/builder/dockerfile/internals.go

**Purpose:** Provides lower-level builder operations for committing layers, exporting copied RW layers, cache probing, container creation, host config construction, and run-config copying.

**Important APIs:** `getArchiver`, `commit`, `commitContainer`, `exportImage`, `performCopy`, `createDestInfo`, `getSourceHashFromInfos`, `hashStringSlice`, run-config modifiers, `copyRunConfig`, `getShell`, `probeCache`, `probeAndCreate`, `create`, `hostConfigFromOptions`, and `getPlatform`.

**Control flow:** Metadata commands call `commit`, which probes cache and creates a temporary container if needed, then commits through backend. ADD/COPY calls `performCopy`, computes source hash, probes cache, mounts destination image, creates RW layer, normalizes destination, resolves chown, copies sources, and exports a child image from the committed layer.

**State and persistence:** Mutates dispatch image ID after commit/export. Creates images/layers through backend. Copies run configs deeply enough for mutable slices/maps. Host config carries build resource/network/security options.

**Dependencies and integration:** Uses daemon builder interfaces, image/layer types, chroot archiver, network defaults, OCI platforms, and server backend commit configs.

**Risks:** Cache compatibility depends on exact NOP command format. Copy export depends on parent image type assertion and content-store digest. Shallow config copying would cause stage mutation bleed; tests protect this.

**Test signals:** `internals_test.go` covers Dockerfile context read errors, run-config copy depth, and export image. Platform tests cover chown and destination normalization.
