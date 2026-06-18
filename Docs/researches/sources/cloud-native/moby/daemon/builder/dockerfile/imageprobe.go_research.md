## sources/cloud-native/moby/daemon/builder/dockerfile/imageprobe.go

**Purpose:** Wraps image cache probing for classic builder steps and enforces cache-busted behavior after the first miss.

**Important APIs/types:** `ImageProber`, `resetFunc`, `imageProber`, `newImageProber`, `Reset`, `Probe`, and `nopProber`.

**Control flow:** `newImageProber` returns `nopProber` for `NoCache`, otherwise builds an image cache from `cacheFrom`. `Probe` skips if cache is busted, asks cache for parent/runconfig/platform match, marks busted on miss, and returns cached image ID on hit. `Reset` rebuilds cache at each new stage.

**State and persistence:** In-memory cache handle and `cacheBusted` boolean. Persistent cache entries are owned by backend image cache implementation.

**Dependencies and integration:** Called by `initializeStage`, `probeCache`, and build internals. Depends on `builder.ImageCacheBuilder`.

**Risks:** One miss disables further cache probing within the current stage, matching classic builder semantics. Incorrect reset scope would make cache too aggressive or too weak.

**Test signals:** Indirectly covered through dispatcher/internals tests. Dedicated tests would help for `NoCache`, miss-after-hit, and reset behavior.
