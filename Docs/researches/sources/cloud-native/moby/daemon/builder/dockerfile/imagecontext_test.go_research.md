## sources/cloud-native/moby/daemon/builder/dockerfile/imagecontext_test.go

**Purpose:** Tests image source mount tracking and scratch image platform behavior.

**Important APIs:** Helper constructors create mock image sources/mounts. Tests cover `Add` with scratch images, platform population, immutability of input platform, nil platform defaults, and `Get` adding returned mounts.

**Control flow:** Tests instantiate `imageSources`, call `Add` or `Get`, then inspect `mounts`, image metadata, and platform fields.

**State and persistence:** In-memory only.

**Dependencies and integration:** Uses mock image/layer implementations from test support.

**Risks:** Tests do not exercise real layer release failures or backend pull-policy behavior.

**Test signals:** Strong direct signal for scratch handling and mount list management.
